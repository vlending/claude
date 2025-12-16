"""GraphRAG 인덱싱 및 커뮤니티 탐지"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import pandas as pd
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


class GraphRAGIndexer:
    """Neo4j 데이터를 GraphRAG 형식으로 변환하고 인덱싱"""

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        output_dir: Path | str = "data/graphrag/input",
    ):
        """
        Args:
            neo4j_uri: Neo4j URI
            neo4j_user: 사용자명
            neo4j_password: 비밀번호
            output_dir: GraphRAG 입력 데이터 출력 디렉토리
        """
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"GraphRAG Indexer 초기화: {neo4j_uri}")

    def close(self):
        """연결 종료"""
        if self.driver:
            self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def extract_group_communities(self) -> List[Dict[str, Any]]:
        """
        그룹 중심 커뮤니티 추출

        Returns:
            커뮤니티 정보 리스트 (각 그룹별)
        """
        logger.info("그룹 중심 커뮤니티 추출 시작...")

        cypher = """
        MATCH (g:IdolGroup)
        OPTIONAL MATCH (g)-[:MANAGED_BY]->(a:Agency)
        OPTIONAL MATCH (m:Member)-[:MEMBER_OF]->(g)
        OPTIONAL MATCH (g)-[:HAS_ACTIVITY]->(c:Content)
        OPTIONAL MATCH (m)-[:PARTICIPATED_IN]->(solo:Content)

        RETURN
            g.group_id AS group_id,
            g.name_ko AS group_name,
            g.debut_date AS debut_date,
            a.name AS agency_name,
            collect(DISTINCT {
                member_id: m.member_id,
                stage_name: m.stage_name,
                roles: m.roles
            }) AS members,
            collect(DISTINCT {
                content_id: c.content_id,
                title: c.title,
                type: c.content_type,
                release_date: c.release_date
            }) AS group_activities,
            collect(DISTINCT {
                member_id: m.member_id,
                content_id: solo.content_id,
                title: solo.title,
                type: solo.content_type
            }) AS solo_activities
        ORDER BY g.debut_date
        """

        with self.driver.session() as session:
            result = session.run(cypher)
            communities = [dict(record) for record in result]

        logger.info(f"추출된 그룹 커뮤니티: {len(communities)}개")
        return communities

    def extract_agency_communities(self) -> List[Dict[str, Any]]:
        """
        기획사 중심 커뮤니티 추출

        Returns:
            기획사별 커뮤니티 정보
        """
        logger.info("기획사 중심 커뮤니티 추출 시작...")

        cypher = """
        MATCH (a:Agency)
        OPTIONAL MATCH (a)<-[r:MANAGED_BY]-(g:IdolGroup)
        OPTIONAL MATCH (g)-[:HAS_ACTIVITY]->(c:Content)

        RETURN
            a.agency_id AS agency_id,
            a.name AS agency_name,
            collect(DISTINCT {
                group_id: g.group_id,
                group_name: g.name_ko,
                debut_date: g.debut_date,
                contract_from: r.from,
                contract_to: r.to
            }) AS groups,
            collect(DISTINCT {
                content_id: c.content_id,
                title: c.title,
                type: c.content_type,
                release_date: c.release_date
            }) AS activities
        """

        with self.driver.session() as session:
            result = session.run(cypher)
            communities = [dict(record) for record in result]

        logger.info(f"추출된 기획사 커뮤니티: {len(communities)}개")
        return communities

    def generate_text_documents(self) -> List[str]:
        """
        GraphRAG 입력용 텍스트 문서 생성

        각 커뮤니티(그룹/기획사)를 하나의 텍스트 문서로 변환

        Returns:
            텍스트 문서 경로 리스트
        """
        logger.info("텍스트 문서 생성 시작...")

        documents = []

        # 1. 그룹 중심 문서
        group_communities = self.extract_group_communities()
        for idx, community in enumerate(group_communities):
            doc_text = self._format_group_document(community)
            doc_path = self.output_dir / f"group_{community['group_id']}.txt"
            doc_path.write_text(doc_text, encoding="utf-8")
            documents.append(str(doc_path))
            logger.debug(f"생성: {doc_path.name}")

        # 2. 기획사 중심 문서
        agency_communities = self.extract_agency_communities()
        for community in agency_communities:
            if not community['agency_id']:
                continue
            doc_text = self._format_agency_document(community)
            doc_path = self.output_dir / f"agency_{community['agency_id']}.txt"
            doc_path.write_text(doc_text, encoding="utf-8")
            documents.append(str(doc_path))
            logger.debug(f"생성: {doc_path.name}")

        logger.info(f"총 {len(documents)}개 문서 생성 완료")
        return documents

    def _format_group_document(self, community: Dict) -> str:
        """그룹 커뮤니티를 텍스트 문서로 포맷"""
        lines = [
            f"# {community['group_name']}",
            "",
            "## 기본 정보",
            f"- 그룹 ID: {community['group_id']}",
            f"- 데뷔: {community['debut_date'] or '정보 없음'}",
            f"- 소속사: {community['agency_name'] or '정보 없음'}",
            "",
            "## 멤버",
        ]

        # 멤버 정보
        members = [m for m in community['members'] if m.get('stage_name')]
        if members:
            for member in members:
                roles = ", ".join(member.get('roles') or [])
                lines.append(f"- {member['stage_name']}" + (f" ({roles})" if roles else ""))
        else:
            lines.append("- 정보 없음")

        lines.append("")
        lines.append("## 그룹 활동")

        # 그룹 활동 (시간순 정렬)
        activities = [a for a in community['group_activities'] if a.get('title')]
        activities_sorted = sorted(
            activities,
            key=lambda x: x.get('release_date') or '',
            reverse=True
        )

        if activities_sorted:
            by_type = {}
            for act in activities_sorted:
                content_type = act.get('type', 'ETC')
                if content_type not in by_type:
                    by_type[content_type] = []
                by_type[content_type].append(act)

            for content_type, acts in by_type.items():
                lines.append(f"\n### {content_type}")
                for act in acts[:10]:  # 최대 10개만
                    date = act.get('release_date') or '날짜 미상'
                    lines.append(f"- [{date}] {act['title']}")
        else:
            lines.append("- 정보 없음")

        # 멤버 개인 활동
        lines.append("")
        lines.append("## 멤버 개인 활동")

        solo_acts = [s for s in community['solo_activities'] if s.get('title')]
        if solo_acts:
            by_member = {}
            for act in solo_acts:
                member_id = act.get('member_id')
                if member_id not in by_member:
                    by_member[member_id] = []
                by_member[member_id].append(act)

            for member_id, acts in by_member.items():
                # 멤버 이름 찾기
                member_name = next(
                    (m['stage_name'] for m in members if m.get('member_id') == member_id),
                    member_id
                )
                lines.append(f"\n### {member_name}")
                for act in acts[:5]:
                    lines.append(f"- {act['title']} ({act.get('type', 'ETC')})")
        else:
            lines.append("- 정보 없음")

        return "\n".join(lines)

    def _format_agency_document(self, community: Dict) -> str:
        """기획사 커뮤니티를 텍스트 문서로 포맷"""
        lines = [
            f"# {community['agency_name']} (기획사)",
            "",
            "## 소속 그룹",
        ]

        groups = [g for g in community['groups'] if g.get('group_name')]
        if groups:
            # 현재/과거 소속 구분
            current_groups = [g for g in groups if not g.get('contract_to')]
            past_groups = [g for g in groups if g.get('contract_to')]

            if current_groups:
                lines.append("\n### 현재 소속")
                for group in current_groups:
                    debut = group.get('debut_date') or '정보 없음'
                    lines.append(f"- {group['group_name']} (데뷔: {debut})")

            if past_groups:
                lines.append("\n### 과거 소속")
                for group in past_groups:
                    period = f"{group.get('contract_from')} ~ {group.get('contract_to')}"
                    lines.append(f"- {group['group_name']} ({period})")
        else:
            lines.append("- 정보 없음")

        lines.append("")
        lines.append("## 주요 활동")

        activities = [a for a in community['activities'] if a.get('title')]
        if activities:
            activities_sorted = sorted(
                activities,
                key=lambda x: x.get('release_date') or '',
                reverse=True
            )

            for act in activities_sorted[:20]:  # 최대 20개
                date = act.get('release_date') or '날짜 미상'
                lines.append(f"- [{date}] {act['title']} ({act.get('type', 'ETC')})")
        else:
            lines.append("- 정보 없음")

        return "\n".join(lines)

    def export_for_graphrag(self) -> Dict[str, Any]:
        """
        GraphRAG 파이프라인용 데이터 내보내기

        Returns:
            내보내기 정보 (문서 경로, 통계 등)
        """
        logger.info("GraphRAG 입력 데이터 생성 중...")

        # 텍스트 문서 생성
        documents = self.generate_text_documents()

        # 메타데이터 생성
        metadata = {
            "total_documents": len(documents),
            "input_directory": str(self.output_dir),
            "document_list": documents,
        }

        # 메타데이터 저장
        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"GraphRAG 입력 준비 완료: {self.output_dir}")
        logger.info(f"  문서 수: {len(documents)}")
        logger.info(f"  메타데이터: {metadata_path}")

        return metadata


if __name__ == "__main__":
    # 테스트
    import os
    from dotenv import load_dotenv
    import sys

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from src.utils import setup_logger

    load_dotenv()
    setup_logger(level="INFO")

    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    with GraphRAGIndexer(neo4j_uri, neo4j_user, neo4j_password) as indexer:
        metadata = indexer.export_for_graphrag()
        print("생성 완료!")
        print(f"문서 경로: {metadata['input_directory']}")
        print(f"문서 수: {metadata['total_documents']}")
