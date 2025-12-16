"""위키 텍스트에서 K-POP 엔티티/관계 추출"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic import BaseModel, Field
from unidecode import unidecode
import re

from ..utils.llm_client import ClaudeClient

logger = logging.getLogger(__name__)


class ExtractionResult(BaseModel):
    """추출 결과"""
    entities: Dict[str, list] = Field(default_factory=dict)
    relations: Dict[str, list] = Field(default_factory=dict)
    dedupe_hints: Dict[str, list] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KpopEntityExtractor:
    """K-POP 엔티티 추출기"""

    def __init__(
        self,
        config_path: Path | str = "config/extraction_prompts.yaml",
        model: str = "claude-sonnet-4-5-20250929",
    ):
        """
        Args:
            config_path: 프롬프트 설정 파일 경로
            model: Claude 모델 ID
        """
        self.config_path = Path(config_path)
        self.llm = ClaudeClient(model=model)
        self._load_config()

    def _load_config(self):
        """설정 파일 로드"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        logger.info(f"설정 파일 로드 완료: {self.config_path}")

    def extract(
        self,
        wiki_text: str,
        wiki_title: str = "",
        wiki_url: str = "",
        temperature: float = 0.0,
    ) -> ExtractionResult:
        """
        위키 텍스트에서 엔티티/관계 추출

        Args:
            wiki_text: 위키 문서 텍스트
            wiki_title: 위키 문서 제목
            wiki_url: 위키 문서 URL
            temperature: LLM 온도

        Returns:
            ExtractionResult
        """
        logger.info(f"추출 시작: {wiki_title or '(제목 없음)'}")

        # 프롬프트 생성
        system_prompt = self.config["system_prompt"]
        user_prompt = self.config["user_prompt_template"].format(
            wiki_title=wiki_title,
            wiki_url=wiki_url,
            wiki_text=wiki_text,
        )

        # LLM 호출
        try:
            result_json = self.llm.extract_json(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )

            # 검증
            validated = self._validate_result(result_json)

            # 메타데이터 추가
            validated["metadata"] = {
                "source_title": wiki_title,
                "source_url": wiki_url,
                "model": self.llm.model,
            }

            result = ExtractionResult(**validated)
            logger.info(
                f"추출 완료: "
                f"그룹={len(result.entities.get('groups', []))}, "
                f"멤버={len(result.entities.get('members', []))}, "
                f"콘텐츠={len(result.entities.get('contents', []))}"
            )

            return result

        except Exception as e:
            logger.error(f"추출 실패: {e}")
            raise

    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        추출 결과 검증 및 정규화

        Args:
            result: LLM 응답 JSON

        Returns:
            검증된 결과
        """
        # 필수 키 존재 확인
        if "entities" not in result:
            result["entities"] = {}
        if "relations" not in result:
            result["relations"] = {}
        if "dedupe_hints" not in result:
            result["dedupe_hints"] = {}

        # 엔티티 검증
        for entity_type in ["groups", "members", "agencies", "contents"]:
            if entity_type not in result["entities"]:
                result["entities"][entity_type] = []

        # ID 자동 생성 (누락 시)
        result["entities"]["groups"] = [
            self._ensure_group_id(g) for g in result["entities"]["groups"]
        ]
        result["entities"]["members"] = [
            self._ensure_member_id(m, result["entities"]["groups"])
            for m in result["entities"]["members"]
        ]
        result["entities"]["agencies"] = [
            self._ensure_agency_id(a) for a in result["entities"]["agencies"]
        ]
        result["entities"]["contents"] = [
            self._ensure_content_id(c) for c in result["entities"]["contents"]
        ]

        # confidence 기본값 설정
        for rel_type in result["relations"].values():
            for rel in rel_type:
                if "confidence" not in rel:
                    rel["confidence"] = 0.8

        return result

    @staticmethod
    def _slugify(text: str) -> str:
        """텍스트를 슬러그로 변환"""
        # 한글 → 영문 음역 (예: "방탄소년단" → "bangtansonyeondan")
        slug = unidecode(text)
        # 소문자, 알파벳/숫자/하이픈만 허용
        slug = re.sub(r'[^a-z0-9]+', '-', slug.lower())
        slug = slug.strip('-')
        return slug or "unknown"

    def _ensure_group_id(self, group: Dict) -> Dict:
        """그룹 ID 보장"""
        if not group.get("group_id"):
            name = group.get("name_ko") or group.get("name_en") or "unknown"
            group["group_id"] = self._slugify(name)
        return group

    def _ensure_member_id(self, member: Dict, groups: list) -> Dict:
        """멤버 ID 보장"""
        if not member.get("member_id"):
            # 기본적으로 첫 번째 그룹 ID 사용 (실제로는 MEMBER_OF 관계에서 유추)
            group_id = groups[0]["group_id"] if groups else "unknown"
            stage_name = member.get("stage_name") or "unknown"
            member["member_id"] = f"{group_id}:{self._slugify(stage_name)}"
        return member

    def _ensure_agency_id(self, agency: Dict) -> Dict:
        """기획사 ID 보장"""
        if not agency.get("agency_id"):
            name = agency.get("name") or "unknown"
            agency["agency_id"] = self._slugify(name)
        return agency

    def _ensure_content_id(self, content: Dict) -> Dict:
        """콘텐츠 ID 보장"""
        if not content.get("content_id"):
            # {group_id}:{content_type}:{year}:{title_slug}
            # group_id는 HAS_ACTIVITY 관계에서 유추 (여기서는 간단히 처리)
            content_type = content.get("content_type", "ETC")
            title = content.get("title", "unknown")
            release_date = content.get("release_date", "")
            year = release_date[:4] if release_date else "unknown"

            title_slug = self._slugify(title)
            content["content_id"] = f"{content_type.lower()}:{year}:{title_slug}"

        return content


if __name__ == "__main__":
    # 테스트
    import os
    from dotenv import load_dotenv
    from ..utils.logger import setup_logger

    load_dotenv()
    setup_logger(level="DEBUG")

    # 프로젝트 루트에서 실행 가정
    config_path = Path("config/extraction_prompts.yaml")

    extractor = KpopEntityExtractor(config_path=config_path)

    # 테스트 위키 텍스트
    test_text = """
    방탄소년단(防彈少年團, BTS)은 대한민국의 7인조 보이 그룹이다.
    빅히트 엔터테인먼트(현 하이브)에서 2013년 6월 13일에 데뷔했다.

    멤버는 RM, 진, 슈가, 제이홉, 지민, 뷔, 정국이다.

    2020년 8월 21일, 디지털 싱글 'Dynamite'를 발매했다.
    """

    result = extractor.extract(
        wiki_text=test_text,
        wiki_title="방탄소년단",
        wiki_url="https://ko.wikipedia.org/wiki/방탄소년단",
    )

    print("추출 결과:")
    print(result.model_dump_json(indent=2, ensure_ascii=False))
