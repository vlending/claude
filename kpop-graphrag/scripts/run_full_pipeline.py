#!/usr/bin/env python3
"""전체 파이프라인 실행 스크립트 (크롤링 → 추출 → 적재 → 인덱싱)"""

import argparse
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import setup_logger


def run_command(cmd: list, description: str) -> bool:
    """
    셸 명령 실행

    Args:
        cmd: 명령 리스트
        description: 설명

    Returns:
        성공 여부
    """
    print("\n" + "=" * 60)
    print(f"▶ {description}")
    print("=" * 60)
    print(f"실행: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            cwd=project_root,
            text=True,
        )
        print(f"\n✓ {description} 완료")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} 실패: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="K-POP GraphRAG 전체 파이프라인 실행")
    parser.add_argument(
        "--skip-crawl",
        action="store_true",
        help="크롤링 단계 건너뛰기 (이미 데이터가 있는 경우)",
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="추출 단계 건너뛰기",
    )
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="Neo4j 적재 단계 건너뛰기",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="GraphRAG 인덱싱 단계 건너뛰기",
    )
    parser.add_argument(
        "--crawl-limit",
        type=int,
        default=10,
        help="크롤링할 최대 페이지 수 (기본: 10)",
    )
    parser.add_argument(
        "--init-schema",
        action="store_true",
        help="Neo4j 스키마 초기화",
    )

    args = parser.parse_args()

    # 환경변수 로드
    load_dotenv()

    logger = setup_logger(level="INFO")

    print("=" * 60)
    print("🎵 K-POP GraphRAG 전체 파이프라인")
    print("=" * 60)

    # 1. 크롤링
    if not args.skip_crawl:
        success = run_command(
            [
                sys.executable,
                "scripts/crawl_wikipedia.py",
                "--limit", str(args.crawl_limit),
                "--output-dir", "data/raw",
            ],
            "1단계: 위키피디아 크롤링"
        )
        if not success:
            print("\n크롤링 실패. 계속 진행하시겠습니까? (y/n): ", end="")
            if input().lower() != 'y':
                sys.exit(1)

    # 2. 추출 (모든 파일)
    if not args.skip_extract:
        raw_dir = project_root / "data" / "raw"
        txt_files = list(raw_dir.glob("*.txt"))

        if not txt_files:
            print("\n⚠️  data/raw/에 .txt 파일이 없습니다.")
            print("크롤링을 먼저 실행하세요.")
            sys.exit(1)

        print(f"\n발견된 텍스트 파일: {len(txt_files)}개")

        for txt_file in txt_files:
            success = run_command(
                [
                    sys.executable,
                    "scripts/run_extraction.py",
                    "--input", str(txt_file),
                ],
                f"2단계: 추출 - {txt_file.name}"
            )
            if not success:
                print(f"\n⚠️  {txt_file.name} 추출 실패 (계속 진행)")

    # 3. Neo4j 적재
    if not args.skip_load:
        cmd = [
            sys.executable,
            "scripts/load_to_neo4j.py",
            "--input", "data/extracted/",
        ]
        if args.init_schema:
            cmd.append("--init-schema")

        success = run_command(
            cmd,
            "3단계: Neo4j 적재"
        )
        if not success:
            print("\nNeo4j 적재 실패. GraphRAG 인덱싱을 건너뜁니다.")
            args.skip_index = True

    # 4. GraphRAG 인덱싱
    if not args.skip_index:
        success = run_command(
            [
                sys.executable,
                "scripts/build_graphrag_index.py",
            ],
            "4단계: GraphRAG 인덱싱"
        )

    # 최종 요약
    print("\n" + "=" * 60)
    print("🎉 파이프라인 실행 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("  1. Neo4j 브라우저: http://localhost:7474")
    print("  2. API 서버 실행: python src/api/server.py")
    print("  3. API 문서: http://localhost:8000/docs")
    print("")


if __name__ == "__main__":
    main()
