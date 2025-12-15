#!/usr/bin/env python3
"""위키 텍스트에서 엔티티 추출 실행 스크립트"""

import argparse
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.extraction import KpopEntityExtractor
from src.utils import setup_logger


def main():
    parser = argparse.ArgumentParser(description="위키 텍스트에서 K-POP 엔티티 추출")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="입력 위키 텍스트 파일 (.txt)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="출력 JSON 파일 경로 (기본: data/extracted/{input_name}.json)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="위키 문서 제목 (선택)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="",
        help="위키 문서 URL (선택)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-5-20250929",
        help="사용할 Claude 모델",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="로그 레벨",
    )

    args = parser.parse_args()

    # 환경변수 로드
    load_dotenv()

    # 로거 설정
    logger = setup_logger(level=args.log_level)

    # 입력 파일 확인
    if not args.input.exists():
        logger.error(f"입력 파일을 찾을 수 없습니다: {args.input}")
        sys.exit(1)

    # 출력 경로 설정
    if args.output is None:
        output_dir = project_root / "data" / "extracted"
        output_dir.mkdir(parents=True, exist_ok=True)
        args.output = output_dir / f"{args.input.stem}.json"

    # 위키 텍스트 읽기
    logger.info(f"위키 텍스트 읽기: {args.input}")
    wiki_text = args.input.read_text(encoding="utf-8")

    # 제목 자동 추론 (제공되지 않은 경우)
    title = args.title or args.input.stem

    # 추출기 초기화
    logger.info(f"추출기 초기화 (model={args.model})")
    extractor = KpopEntityExtractor(
        config_path=project_root / "config" / "extraction_prompts.yaml",
        model=args.model,
    )

    # 추출 실행
    logger.info(f"엔티티 추출 시작: {title}")
    result = extractor.extract(
        wiki_text=wiki_text,
        wiki_title=title,
        wiki_url=args.url,
    )

    # 결과 저장
    logger.info(f"결과 저장: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(
            result.model_dump(),
            f,
            ensure_ascii=False,
            indent=2,
        )

    # 요약 출력
    logger.info("=" * 60)
    logger.info("추출 완료!")
    logger.info(f"  그룹: {len(result.entities.get('groups', []))}개")
    logger.info(f"  멤버: {len(result.entities.get('members', []))}개")
    logger.info(f"  기획사: {len(result.entities.get('agencies', []))}개")
    logger.info(f"  콘텐츠: {len(result.entities.get('contents', []))}개")
    logger.info(f"출력 파일: {args.output}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
