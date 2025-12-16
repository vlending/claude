#!/usr/bin/env python3
"""위키피디아 K-POP 그룹 크롤링 스크립트"""

import argparse
from pathlib import Path
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crawler import WikiCrawler
from src.utils import setup_logger


def main():
    parser = argparse.ArgumentParser(description="위키피디아 K-POP 그룹 크롤링")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="data/raw",
        help="출력 디렉토리",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="대한민국의_아이돌_그룹",
        help="위키 카테고리",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="최대 페이지 수 (None이면 전체)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="ko",
        choices=["ko", "en"],
        help="언어 (ko=한국어, en=영어)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="요청 간 대기 시간 (초)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="로그 레벨",
    )

    args = parser.parse_args()

    # 로거 설정
    logger = setup_logger(level=args.log_level)

    logger.info("=" * 60)
    logger.info("위키피디아 K-POP 그룹 크롤링")
    logger.info("=" * 60)
    logger.info(f"언어: {args.lang}")
    logger.info(f"카테고리: {args.category}")
    logger.info(f"출력 디렉토리: {args.output_dir}")
    logger.info(f"제한: {args.limit or '전체'}")
    logger.info("=" * 60)

    # 크롤러 실행
    crawler = WikiCrawler(
        lang=args.lang,
        delay=args.delay,
    )

    saved_files = crawler.crawl_kpop_groups(
        output_dir=args.output_dir,
        category=args.category,
        limit=args.limit,
    )

    # 요약
    logger.info("")
    logger.info("=" * 60)
    logger.info("크롤링 완료!")
    logger.info(f"  저장된 파일: {len(saved_files)}개")
    logger.info(f"  출력 디렉토리: {args.output_dir}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("다음 단계:")
    logger.info("  1. 추출: python scripts/run_extraction.py --input data/raw/")
    logger.info("  2. 적재: python scripts/load_to_neo4j.py --input data/extracted/")
    logger.info("")


if __name__ == "__main__":
    main()
