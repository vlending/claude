#!/usr/bin/env python3
"""추출된 JSON을 Neo4j에 적재하는 스크립트"""

import argparse
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.graph import Neo4jClient
from src.utils import setup_logger


def main():
    parser = argparse.ArgumentParser(description="추출 결과를 Neo4j에 적재")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="입력 JSON 파일 또는 디렉토리 (data/extracted/)",
    )
    parser.add_argument(
        "--init-schema",
        action="store_true",
        help="스키마 초기화 (제약/인덱스 생성)",
    )
    parser.add_argument(
        "--clear-db",
        action="store_true",
        help="⚠️ 데이터베이스 전체 삭제 후 재적재 (주의!)",
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

    # Neo4j 클라이언트 초기화
    logger.info("Neo4j 연결 중...")
    client = Neo4jClient(
        schema_config_path=project_root / "config" / "schema.yaml"
    )

    if not client.verify_connectivity():
        logger.error("Neo4j 연결 실패. 데이터베이스가 실행 중인지 확인하세요.")
        sys.exit(1)

    logger.info("✓ Neo4j 연결 성공")

    # 데이터베이스 초기화 (선택)
    if args.clear_db:
        confirm = input("⚠️  데이터베이스를 완전히 삭제합니다. 계속하시겠습니까? (yes/no): ")
        if confirm.lower() == "yes":
            logger.warning("데이터베이스 삭제 중...")
            client.query("MATCH (n) DETACH DELETE n")
            logger.info("✓ 데이터베이스 삭제 완료")
        else:
            logger.info("취소되었습니다.")
            sys.exit(0)

    # 스키마 초기화 (선택)
    if args.init_schema:
        logger.info("스키마 초기화 중...")
        client.init_schema()
        logger.info("✓ 스키마 초기화 완료")

    # JSON 파일 수집
    json_files = []
    if args.input.is_file():
        json_files = [args.input]
    elif args.input.is_dir():
        json_files = list(args.input.glob("*.json"))
    else:
        logger.error(f"입력 경로를 찾을 수 없습니다: {args.input}")
        sys.exit(1)

    if not json_files:
        logger.error("처리할 JSON 파일이 없습니다.")
        sys.exit(1)

    logger.info(f"발견된 JSON 파일: {len(json_files)}개")

    # 각 파일 처리
    total_stats = {
        "groups": 0,
        "members": 0,
        "agencies": 0,
        "contents": 0,
    }

    for json_file in json_files:
        logger.info(f"처리 중: {json_file.name}")

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 적재
            client.load_extraction_result(data)

            # 통계 업데이트
            entities = data.get("entities", {})
            total_stats["groups"] += len(entities.get("groups", []))
            total_stats["members"] += len(entities.get("members", []))
            total_stats["agencies"] += len(entities.get("agencies", []))
            total_stats["contents"] += len(entities.get("contents", []))

        except Exception as e:
            logger.error(f"파일 처리 실패: {json_file.name} - {e}")
            continue

    # 최종 요약
    logger.info("=" * 60)
    logger.info("적재 완료!")
    logger.info(f"  총 그룹: {total_stats['groups']}개")
    logger.info(f"  총 멤버: {total_stats['members']}개")
    logger.info(f"  총 기획사: {total_stats['agencies']}개")
    logger.info(f"  총 콘텐츠: {total_stats['contents']}개")
    logger.info("=" * 60)

    # 연결 종료
    client.close()


if __name__ == "__main__":
    main()
