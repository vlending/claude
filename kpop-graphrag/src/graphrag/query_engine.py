"""GraphRAG 쿼리 엔진"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

logger = logging.getLogger(__name__)


class KpopQueryEngine:
    """K-POP GraphRAG 쿼리 엔진 (하이브리드 검색)"""

    def __init__(
        self,
        graphrag_index_dir: Path | str = "data/graphrag/output",
        neo4j_client = None,
    ):
        """
        Args:
            graphrag_index_dir: GraphRAG 인덱스 디렉토리
            neo4j_client: Neo4jClient 인스턴스 (선택)
        """
        self.index_dir = Path(graphrag_index_dir)
        self.neo4j_client = neo4j_client

        # GraphRAG 컨텍스트 로드
        self._load_graphrag_context()

        logger.info("KpopQueryEngine 초기화 완료")

    def _load_graphrag_context(self):
        """GraphRAG 커뮤니티 요약 로드"""
        # 실제로는 GraphRAG가 생성한 커뮤니티 요약을 로드
        # 여기서는 간단한 구현
        self.communities = {}

        community_file = self.index_dir / "communities.json"
        if community_file.exists():
            with open(community_file, "r", encoding="utf-8") as f:
                self.communities = json.load(f)
            logger.info(f"커뮤니티 요약 로드: {len(self.communities)}개")
        else:
            logger.warning(f"커뮤니티 파일 없음: {community_file}")

    def query(
        self,
        question: str,
        mode: str = "hybrid",
        k: int = 5,
    ) -> Dict[str, Any]:
        """
        질의응답 수행

        Args:
            question: 사용자 질문
            mode: 검색 모드 (local, global, hybrid, cypher)
            k: 반환할 결과 수

        Returns:
            응답 딕셔너리
        """
        logger.info(f"쿼리 수행 (mode={mode}): {question}")

        if mode == "cypher":
            # Pure Neo4j Cypher 쿼리
            return self._cypher_query(question, k)

        elif mode == "local":
            # GraphRAG 로컬 검색 (특정 커뮤니티)
            return self._local_search(question, k)

        elif mode == "global":
            # GraphRAG 글로벌 검색 (전체 커뮤니티)
            return self._global_search(question, k)

        elif mode == "hybrid":
            # 하이브리드 (Cypher + GraphRAG)
            return self._hybrid_search(question, k)

        else:
            raise ValueError(f"알 수 없는 모드: {mode}")

    def _cypher_query(self, question: str, k: int) -> Dict[str, Any]:
        """순수 Cypher 쿼리 (구조화된 질문)"""
        if not self.neo4j_client:
            return {"error": "Neo4j 클라이언트가 없습니다."}

        # 질문에서 Cypher 쿼리 생성 (간단한 패턴 매칭)
        # 실제로는 LLM으로 자연어 → Cypher 변환

        cypher_query = self._question_to_cypher(question)

        try:
            results = self.neo4j_client.query(cypher_query)
            return {
                "mode": "cypher",
                "question": question,
                "cypher": cypher_query,
                "results": results[:k],
                "count": len(results),
            }
        except Exception as e:
            logger.error(f"Cypher 쿼리 실패: {e}")
            return {"error": str(e)}

    def _question_to_cypher(self, question: str) -> str:
        """질문을 Cypher 쿼리로 변환 (간단한 패턴 매칭)"""
        question_lower = question.lower()

        # 예: "BTS 멤버는?" → MATCH (m:Member)-[:MEMBER_OF]->(g:IdolGroup {name_ko: "방탄소년단"})
        if "멤버" in question_lower:
            # 그룹명 추출 (간단한 예시)
            return """
            MATCH (m:Member)-[:MEMBER_OF]->(g:IdolGroup)
            RETURN g.name_ko AS 그룹, collect(m.stage_name) AS 멤버
            """

        # 예: "활동" 관련
        elif "활동" in question_lower:
            return """
            MATCH (g:IdolGroup)-[:HAS_ACTIVITY]->(c:Content)
            RETURN g.name_ko AS 그룹, c.title AS 활동, c.release_date AS 날짜
            ORDER BY c.release_date DESC
            LIMIT 10
            """

        # 기본 쿼리
        else:
            return "MATCH (n) RETURN n LIMIT 10"

    def _local_search(self, question: str, k: int) -> Dict[str, Any]:
        """GraphRAG 로컬 검색 (특정 엔티티 중심)"""
        # 실제로는 GraphRAG의 local search 사용
        # 여기서는 시뮬레이션

        logger.info("로컬 검색 수행 중...")

        # 커뮤니티 검색
        relevant_communities = self._find_relevant_communities(question, k)

        # LLM으로 최종 답변 생성 (프롬프트 템플릿 사용)
        answer = self._generate_answer_from_communities(
            question,
            relevant_communities,
            mode="local"
        )

        return {
            "mode": "local",
            "question": question,
            "answer": answer,
            "communities": relevant_communities,
        }

    def _global_search(self, question: str, k: int) -> Dict[str, Any]:
        """GraphRAG 글로벌 검색 (전체 커뮤니티 요약)"""
        logger.info("글로벌 검색 수행 중...")

        # 모든 커뮤니티 요약을 종합
        all_communities = list(self.communities.values())[:k]

        answer = self._generate_answer_from_communities(
            question,
            all_communities,
            mode="global"
        )

        return {
            "mode": "global",
            "question": question,
            "answer": answer,
            "total_communities": len(all_communities),
        }

    def _hybrid_search(self, question: str, k: int) -> Dict[str, Any]:
        """하이브리드 검색 (Cypher + GraphRAG)"""
        logger.info("하이브리드 검색 수행 중...")

        # 1. Cypher로 구조화된 데이터 추출
        cypher_result = self._cypher_query(question, k)

        # 2. GraphRAG로 컨텍스트 요약
        graphrag_result = self._local_search(question, k)

        # 3. 결합
        combined_answer = f"""
## 구조화된 데이터 (Neo4j)
{json.dumps(cypher_result.get('results', []), ensure_ascii=False, indent=2)}

## 맥락적 요약 (GraphRAG)
{graphrag_result.get('answer', '정보 없음')}
        """

        return {
            "mode": "hybrid",
            "question": question,
            "cypher_results": cypher_result.get("results", []),
            "graphrag_answer": graphrag_result.get("answer", ""),
            "combined_answer": combined_answer.strip(),
        }

    def _find_relevant_communities(self, question: str, k: int) -> List[Dict]:
        """질문과 관련된 커뮤니티 찾기 (간단한 키워드 매칭)"""
        # 실제로는 임베딩 유사도 사용

        question_lower = question.lower()
        scored_communities = []

        for comm_id, comm_data in self.communities.items():
            score = 0
            text = str(comm_data).lower()

            # 간단한 키워드 매칭
            keywords = question_lower.split()
            for keyword in keywords:
                if keyword in text:
                    score += 1

            if score > 0:
                scored_communities.append((score, comm_data))

        # 점수순 정렬
        scored_communities.sort(key=lambda x: x[0], reverse=True)

        return [comm for score, comm in scored_communities[:k]]

    def _generate_answer_from_communities(
        self,
        question: str,
        communities: List[Dict],
        mode: str
    ) -> str:
        """커뮤니티 정보로부터 답변 생성 (LLM 사용)"""
        # 실제로는 Claude API 호출
        # 여기서는 간단한 템플릿

        if not communities:
            return "관련 정보를 찾을 수 없습니다."

        # 커뮤니티 정보 요약
        context_summary = "\n\n".join([
            f"- {comm.get('name', comm.get('id', '알 수 없음'))}"
            for comm in communities
        ])

        # 간단한 답변 생성
        answer = f"""
질문: {question}

관련 커뮤니티:
{context_summary}

(실제로는 Claude API로 상세 답변 생성)
        """

        return answer.strip()


if __name__ == "__main__":
    # 테스트
    from src.utils import setup_logger

    setup_logger(level="INFO")

    engine = KpopQueryEngine()

    # 테스트 쿼리
    result = engine.query("BTS의 멤버는?", mode="cypher")
    print(json.dumps(result, ensure_ascii=False, indent=2))
