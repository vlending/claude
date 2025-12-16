"""위키피디아 크롤러 - K-POP 그룹 데이터 자동 수집"""

import logging
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote, unquote
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WikiCrawler:
    """위키피디아 크롤러"""

    def __init__(
        self,
        lang: str = "ko",
        delay: float = 1.0,
        user_agent: str = None,
    ):
        """
        Args:
            lang: 언어 코드 (ko, en)
            delay: 요청 간 대기 시간 (초)
            user_agent: User-Agent 헤더
        """
        self.lang = lang
        self.delay = delay
        self.base_url = f"https://{lang}.wikipedia.org"

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or (
                "Mozilla/5.0 (compatible; KpopGraphRAG/0.1; "
                "+https://github.com/kpop-graphrag)"
            )
        })

        logger.info(f"WikiCrawler 초기화 (lang={lang})")

    def search_kpop_groups(
        self,
        category: str = "대한민국의_아이돌_그룹",
        limit: Optional[int] = None,
    ) -> List[str]:
        """
        K-POP 그룹 카테고리에서 페이지 목록 가져오기

        Args:
            category: 위키 카테고리 (한글)
            limit: 최대 페이지 수 (None이면 전체)

        Returns:
            페이지 제목 리스트
        """
        logger.info(f"카테고리 '{category}'에서 페이지 검색 중...")

        # 카테고리 URL
        category_url = f"{self.base_url}/wiki/분류:{quote(category)}"

        pages = []
        continue_token = None

        while True:
            # API를 통한 카테고리 멤버 조회
            api_url = f"{self.base_url}/w/api.php"
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"분류:{category}",
                "cmlimit": 500,
                "format": "json",
            }

            if continue_token:
                params["cmcontinue"] = continue_token

            try:
                response = self.session.get(api_url, params=params)
                response.raise_for_status()
                data = response.json()

                members = data.get("query", {}).get("categorymembers", [])
                for member in members:
                    title = member.get("title")
                    # "분류:" 페이지는 제외
                    if title and not title.startswith("분류:"):
                        pages.append(title)

                # 다음 페이지 확인
                continue_token = data.get("continue", {}).get("cmcontinue")
                if not continue_token:
                    break

                # limit 확인
                if limit and len(pages) >= limit:
                    pages = pages[:limit]
                    break

                time.sleep(self.delay)

            except Exception as e:
                logger.error(f"카테고리 조회 오류: {e}")
                break

        logger.info(f"발견된 페이지: {len(pages)}개")
        return pages

    def fetch_page(self, title: str) -> Optional[Dict[str, str]]:
        """
        위키 페이지 내용 가져오기

        Args:
            title: 페이지 제목

        Returns:
            {
                "title": 제목,
                "url": URL,
                "text": 본문 텍스트,
                "html": HTML (선택)
            }
        """
        logger.info(f"페이지 가져오기: {title}")

        # API를 통한 페이지 내용 조회
        api_url = f"{self.base_url}/w/api.php"
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts|info",
            "explaintext": True,  # 순수 텍스트
            "inprop": "url",
            "format": "json",
        }

        try:
            response = self.session.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            page_id = list(pages.keys())[0]

            if page_id == "-1":
                logger.warning(f"페이지를 찾을 수 없음: {title}")
                return None

            page_data = pages[page_id]

            result = {
                "title": page_data.get("title"),
                "url": page_data.get("fullurl"),
                "text": page_data.get("extract", ""),
            }

            time.sleep(self.delay)
            return result

        except Exception as e:
            logger.error(f"페이지 가져오기 오류: {e}")
            return None

    def crawl_kpop_groups(
        self,
        output_dir: Path | str = "data/raw",
        category: str = "대한민국의_아이돌_그룹",
        limit: Optional[int] = None,
    ) -> List[Path]:
        """
        K-POP 그룹 페이지 일괄 크롤링

        Args:
            output_dir: 출력 디렉토리
            category: 카테고리
            limit: 최대 페이지 수

        Returns:
            저장된 파일 경로 리스트
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 60)
        logger.info("K-POP 그룹 크롤링 시작")
        logger.info("=" * 60)

        # 1. 페이지 목록 가져오기
        page_titles = self.search_kpop_groups(category=category, limit=limit)

        if not page_titles:
            logger.warning("크롤링할 페이지가 없습니다.")
            return []

        logger.info(f"크롤링할 페이지: {len(page_titles)}개")

        # 2. 각 페이지 가져오기
        saved_files = []

        for idx, title in enumerate(page_titles, 1):
            logger.info(f"[{idx}/{len(page_titles)}] {title}")

            page_data = self.fetch_page(title)
            if not page_data:
                continue

            # 파일명 생성 (안전한 파일명)
            safe_filename = self._make_safe_filename(title)
            file_path = output_dir / f"{safe_filename}.txt"

            # 저장
            try:
                file_path.write_text(
                    page_data["text"],
                    encoding="utf-8"
                )
                saved_files.append(file_path)
                logger.info(f"  → 저장: {file_path.name}")

            except Exception as e:
                logger.error(f"파일 저장 오류: {e}")

        logger.info("=" * 60)
        logger.info(f"크롤링 완료! 총 {len(saved_files)}개 파일 저장")
        logger.info("=" * 60)

        return saved_files

    @staticmethod
    def _make_safe_filename(title: str) -> str:
        """안전한 파일명 생성"""
        # 특수문자 제거
        safe = re.sub(r'[<>:"/\\|?*]', '', title)
        safe = safe.replace(' ', '_')
        # 길이 제한
        if len(safe) > 100:
            safe = safe[:100]
        return safe


class NaverKpopCrawler:
    """네이버 K-POP 위키 크롤러 (선택적)"""

    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.base_url = "https://namu.wiki"
        logger.info("NaverKpopCrawler 초기화")

    def fetch_page(self, title: str) -> Optional[Dict[str, str]]:
        """
        나무위키 페이지 가져오기
        (참고: 나무위키는 크롤링 제한이 있을 수 있음)

        Args:
            title: 페이지 제목

        Returns:
            페이지 데이터
        """
        logger.warning("나무위키 크롤러는 현재 제한적으로 지원됩니다.")
        # 구현 생략 (나무위키 API가 공식적으로 제공되지 않음)
        return None


if __name__ == "__main__":
    # 테스트
    from dotenv import load_dotenv
    import sys

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from src.utils import setup_logger

    load_dotenv()
    setup_logger(level="INFO")

    # 크롤러 실행
    crawler = WikiCrawler(lang="ko", delay=2.0)

    # 테스트: 소수의 페이지만 크롤링
    saved_files = crawler.crawl_kpop_groups(
        output_dir="data/raw",
        limit=5,  # 테스트용 5개만
    )

    print(f"\n저장된 파일: {len(saved_files)}개")
    for file_path in saved_files:
        print(f"  - {file_path}")
