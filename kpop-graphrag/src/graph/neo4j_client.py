"""Neo4j 그래프 데이터베이스 클라이언트"""

import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from neo4j import GraphDatabase, Driver, Session
import yaml

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j 데이터베이스 클라이언트"""

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        schema_config_path: Path | str = "config/schema.yaml",
    ):
        """
        Args:
            uri: Neo4j URI (None이면 환경변수 사용)
            user: 사용자명 (None이면 환경변수 사용)
            password: 비밀번호 (None이면 환경변수 사용)
            schema_config_path: 스키마 설정 파일 경로
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD")

        if not self.password:
            raise ValueError("NEO4J_PASSWORD가 설정되지 않았습니다.")

        self.driver: Driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )

        # 스키마 설정 로드
        self.schema_config_path = Path(schema_config_path)
        self._load_schema_config()

        logger.info(f"Neo4j 연결 성공: {self.uri}")

    def _load_schema_config(self):
        """스키마 설정 로드"""
        if not self.schema_config_path.exists():
            logger.warning(f"스키마 설정 파일 없음: {self.schema_config_path}")
            self.schema_config = {}
            return

        with open(self.schema_config_path, "r", encoding="utf-8") as f:
            self.schema_config = yaml.safe_load(f)

        logger.info(f"스키마 설정 로드 완료: {self.schema_config_path}")

    def close(self):
        """연결 종료"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j 연결 종료")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def verify_connectivity(self) -> bool:
        """연결 확인"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS num")
                record = result.single()
                return record["num"] == 1
        except Exception as e:
            logger.error(f"연결 실패: {e}")
            return False

    def init_schema(self):
        """스키마 초기화 (제약/인덱스 생성)"""
        if not self.schema_config:
            logger.warning("스키마 설정이 없어 초기화를 건너뜁니다.")
            return

        logger.info("스키마 초기화 시작...")

        # Cypher 템플릿 실행
        templates = self.schema_config.get("cypher_templates", {})

        # 1. 제약 조건 생성
        if "create_constraints" in templates:
            self._execute_multiline_cypher(templates["create_constraints"])
            logger.info("제약 조건 생성 완료")

        # 2. 인덱스 생성
        if "create_indexes" in templates:
            self._execute_multiline_cypher(templates["create_indexes"])
            logger.info("인덱스 생성 완료")

        logger.info("스키마 초기화 완료")

    def _execute_multiline_cypher(self, cypher: str):
        """여러 줄의 Cypher 쿼리 실행 (세미콜론으로 분리)"""
        queries = [q.strip() for q in cypher.split(";") if q.strip()]
        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    logger.warning(f"쿼리 실행 실패 (무시): {query[:50]}... - {e}")

    def merge_group(self, group: Dict[str, Any]):
        """그룹 노드 MERGE"""
        cypher = self.schema_config["cypher_templates"]["merge_group"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(group))

    def merge_member(self, member: Dict[str, Any]):
        """멤버 노드 MERGE"""
        cypher = self.schema_config["cypher_templates"]["merge_member"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(member))

    def merge_agency(self, agency: Dict[str, Any]):
        """기획사 노드 MERGE"""
        cypher = self.schema_config["cypher_templates"]["merge_agency"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(agency))

    def merge_content(self, content: Dict[str, Any]):
        """콘텐츠 노드 MERGE"""
        cypher = self.schema_config["cypher_templates"]["merge_content"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(content))

    def create_managed_by(self, relation: Dict[str, Any]):
        """MANAGED_BY 관계 생성"""
        cypher = self.schema_config["cypher_templates"]["create_managed_by"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(relation))

    def create_member_of(self, relation: Dict[str, Any]):
        """MEMBER_OF 관계 생성"""
        cypher = self.schema_config["cypher_templates"]["create_member_of"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(relation))

    def create_has_activity(self, relation: Dict[str, Any]):
        """HAS_ACTIVITY 관계 생성"""
        cypher = self.schema_config["cypher_templates"]["create_has_activity"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(relation))

    def create_participated_in(self, relation: Dict[str, Any]):
        """PARTICIPATED_IN 관계 생성"""
        cypher = self.schema_config["cypher_templates"]["create_participated_in"]
        with self.driver.session() as session:
            session.run(cypher, **self._prepare_params(relation))

    @staticmethod
    def _prepare_params(data: Dict[str, Any]) -> Dict[str, Any]:
        """파라미터 준비 (None 값 처리)"""
        return {k: v for k, v in data.items() if v is not None}

    def load_extraction_result(self, result: Dict[str, Any]):
        """
        추출 결과를 그래프에 적재

        Args:
            result: ExtractionResult.model_dump() 또는 유사 구조
        """
        entities = result.get("entities", {})
        relations = result.get("relations", {})

        logger.info("그래프 적재 시작...")

        # 1. 엔티티 적재
        for group in entities.get("groups", []):
            self.merge_group(group)
        logger.info(f"그룹 {len(entities.get('groups', []))}개 적재")

        for member in entities.get("members", []):
            self.merge_member(member)
        logger.info(f"멤버 {len(entities.get('members', []))}개 적재")

        for agency in entities.get("agencies", []):
            self.merge_agency(agency)
        logger.info(f"기획사 {len(entities.get('agencies', []))}개 적재")

        for content in entities.get("contents", []):
            self.merge_content(content)
        logger.info(f"콘텐츠 {len(entities.get('contents', []))}개 적재")

        # 2. 관계 적재
        for rel in relations.get("managed_by", []):
            self.create_managed_by(rel)
        logger.info(f"MANAGED_BY 관계 {len(relations.get('managed_by', []))}개 생성")

        for rel in relations.get("member_of", []):
            self.create_member_of(rel)
        logger.info(f"MEMBER_OF 관계 {len(relations.get('member_of', []))}개 생성")

        for rel in relations.get("has_activity", []):
            self.create_has_activity(rel)
        logger.info(f"HAS_ACTIVITY 관계 {len(relations.get('has_activity', []))}개 생성")

        for rel in relations.get("participated_in", []):
            self.create_participated_in(rel)
        logger.info(f"PARTICIPATED_IN 관계 {len(relations.get('participated_in', []))}개 생성")

        logger.info("그래프 적재 완료")

    def query(self, cypher: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Cypher 쿼리 실행

        Args:
            cypher: Cypher 쿼리
            params: 파라미터

        Returns:
            결과 레코드 리스트
        """
        with self.driver.session() as session:
            result = session.run(cypher, params or {})
            return [dict(record) for record in result]

    def get_group_timeline(self, group_id: str) -> List[Dict]:
        """그룹의 활동 타임라인 조회"""
        cypher = self.schema_config["example_queries"]["group_timeline"]["cypher"]
        return self.query(cypher, {"group_id": group_id})


if __name__ == "__main__":
    # 테스트
    from dotenv import load_dotenv
    from ..utils.logger import setup_logger

    load_dotenv()
    setup_logger(level="INFO")

    with Neo4jClient() as client:
        # 연결 확인
        if client.verify_connectivity():
            print("✓ Neo4j 연결 성공")

            # 스키마 초기화
            client.init_schema()
            print("✓ 스키마 초기화 완료")

            # 테스트 데이터 삽입
            test_group = {
                "group_id": "bts",
                "name_ko": "방탄소년단",
                "name_en": "BTS",
                "debut_date": "2013-06-13",
                "debut_year": 2013,
                "status": "active"
            }
            client.merge_group(test_group)
            print("✓ 테스트 그룹 추가 완료")

        else:
            print("✗ Neo4j 연결 실패")
