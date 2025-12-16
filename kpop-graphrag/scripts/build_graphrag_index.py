#!/usr/bin/env python3
"""GraphRAG 인덱스 빌드 스크립트"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.graphrag import GraphRAGIndexer
from src.utils import setup_logger


def main():
    parser = argparse.ArgumentParser(description="GraphRAG 인덱스 빌드")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="data/graphrag/input",
        help="출력 디렉토리",
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

    # Neo4j 연결 정보
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    if not neo4j_password:
        logger.error("NEO4J_PASSWORD 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("GraphRAG 인덱스 빌드 시작")
    logger.info("=" * 60)

    # 인덱서 초기화
    with GraphRAGIndexer(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        output_dir=args.output_dir,
    ) as indexer:

        # Neo4j → GraphRAG 입력 문서 생성
        logger.info("1단계: Neo4j 데이터 → 텍스트 문서 변환")
        metadata = indexer.export_for_graphrag()

        logger.info("=" * 60)
        logger.info("GraphRAG 입력 생성 완료!")
        logger.info(f"  출력 디렉토리: {metadata['input_directory']}")
        logger.info(f"  생성된 문서: {metadata['total_documents']}개")
        logger.info("=" * 60)

        # 다음 단계 안내
        logger.info("")
        logger.info("다음 단계: Microsoft GraphRAG 실행")
        logger.info("")
        logger.info("1. GraphRAG CLI 설치 (아직 안했다면):")
        logger.info("   pip install graphrag")
        logger.info("")
        logger.info("2. GraphRAG 설정 초기화:")
        logger.info(f"   cd {metadata['input_directory']}")
        logger.info("   graphrag init --root .")
        logger.info("")
        logger.info("3. settings.yaml 편집:")
        logger.info("   - LLM 설정 (Claude 또는 OpenAI)")
        logger.info("   - 임베딩 모델 설정")
        logger.info("")
        logger.info("4. 인덱싱 실행:")
        logger.info("   graphrag index --root .")
        logger.info("")
        logger.info("5. 쿼리 테스트:")
        logger.info('   graphrag query --root . --method local "BTS 멤버는?"')
        logger.info("")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
