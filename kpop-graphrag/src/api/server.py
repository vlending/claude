"""FastAPI 서버 - K-POP GraphRAG API"""

import logging
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.graphrag import KpopQueryEngine
from src.graph import Neo4jClient
from src.utils import setup_logger

# 환경변수 로드
load_dotenv()

# 로거 설정
logger = setup_logger(name="api", level=os.getenv("LOG_LEVEL", "INFO"))

# FastAPI 앱 생성
app = FastAPI(
    title="K-POP GraphRAG API",
    description="K-POP 지식 그래프 기반 질의응답 API",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j 클라이언트 초기화
neo4j_client = None
query_engine = None


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    global neo4j_client, query_engine

    logger.info("서버 시작 중...")

    # Neo4j 연결
    try:
        neo4j_client = Neo4jClient(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD"),
        )
        if neo4j_client.verify_connectivity():
            logger.info("✓ Neo4j 연결 성공")
        else:
            logger.warning("✗ Neo4j 연결 실패")
    except Exception as e:
        logger.error(f"Neo4j 연결 오류: {e}")

    # 쿼리 엔진 초기화
    try:
        query_engine = KpopQueryEngine(neo4j_client=neo4j_client)
        logger.info("✓ 쿼리 엔진 초기화 완료")
    except Exception as e:
        logger.error(f"쿼리 엔진 초기화 오류: {e}")

    logger.info("🚀 서버 준비 완료!")


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 정리"""
    logger.info("서버 종료 중...")
    if neo4j_client:
        neo4j_client.close()


# === 요청/응답 모델 ===

class QueryRequest(BaseModel):
    """질의 요청"""
    question: str = Field(..., description="질문")
    mode: str = Field(
        default="hybrid",
        description="검색 모드 (local, global, hybrid, cypher)"
    )
    k: int = Field(default=5, description="반환할 결과 수", ge=1, le=20)


class QueryResponse(BaseModel):
    """질의 응답"""
    question: str
    mode: str
    answer: Optional[str] = None
    results: Optional[list] = None
    metadata: Optional[dict] = None


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    neo4j_connected: bool
    query_engine_ready: bool


# === API 엔드포인트 ===

@app.get("/", response_model=dict)
async def root():
    """루트 엔드포인트"""
    return {
        "service": "K-POP GraphRAG API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "groups": "/groups",
            "members": "/members",
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스체크"""
    neo4j_ok = neo4j_client.verify_connectivity() if neo4j_client else False
    engine_ok = query_engine is not None

    return HealthResponse(
        status="healthy" if (neo4j_ok and engine_ok) else "degraded",
        neo4j_connected=neo4j_ok,
        query_engine_ready=engine_ok,
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    질의응답 수행

    - **question**: 질문 (예: "BTS 멤버는?")
    - **mode**: 검색 모드
        - `local`: 특정 엔티티 중심 검색
        - `global`: 전체 커뮤니티 요약
        - `hybrid`: Cypher + GraphRAG 조합
        - `cypher`: 순수 Neo4j Cypher 쿼리
    - **k**: 반환할 결과 수 (1-20)
    """
    if not query_engine:
        raise HTTPException(status_code=503, detail="쿼리 엔진이 준비되지 않았습니다.")

    logger.info(f"쿼리 요청: {request.question} (mode={request.mode})")

    try:
        result = query_engine.query(
            question=request.question,
            mode=request.mode,
            k=request.k,
        )

        return QueryResponse(
            question=request.question,
            mode=request.mode,
            answer=result.get("answer") or result.get("combined_answer"),
            results=result.get("results") or result.get("cypher_results"),
            metadata={
                "communities": result.get("communities"),
                "total_communities": result.get("total_communities"),
                "cypher": result.get("cypher"),
            }
        )

    except Exception as e:
        logger.error(f"쿼리 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/groups")
async def list_groups(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    그룹 목록 조회

    - **limit**: 반환할 그룹 수 (1-100)
    - **offset**: 시작 오프셋
    """
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Neo4j 연결 안 됨")

    try:
        cypher = f"""
        MATCH (g:IdolGroup)
        OPTIONAL MATCH (g)-[:MANAGED_BY]->(a:Agency)
        RETURN g.group_id AS group_id,
               g.name_ko AS name_ko,
               g.name_en AS name_en,
               g.debut_date AS debut_date,
               a.name AS agency
        ORDER BY g.debut_date DESC
        SKIP {offset}
        LIMIT {limit}
        """

        results = neo4j_client.query(cypher)

        return {
            "total": len(results),
            "offset": offset,
            "limit": limit,
            "groups": results,
        }

    except Exception as e:
        logger.error(f"그룹 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/groups/{group_id}")
async def get_group(group_id: str):
    """
    특정 그룹 상세 조회

    - **group_id**: 그룹 ID (예: bangtansonyeondan)
    """
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Neo4j 연결 안 됨")

    try:
        cypher = """
        MATCH (g:IdolGroup {group_id: $group_id})
        OPTIONAL MATCH (g)-[:MANAGED_BY]->(a:Agency)
        OPTIONAL MATCH (m:Member)-[:MEMBER_OF]->(g)
        OPTIONAL MATCH (g)-[:HAS_ACTIVITY]->(c:Content)

        RETURN g.group_id AS group_id,
               g.name_ko AS name_ko,
               g.name_en AS name_en,
               g.debut_date AS debut_date,
               g.status AS status,
               a.name AS agency,
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
               }) AS activities
        """

        results = neo4j_client.query(cypher, {"group_id": group_id})

        if not results:
            raise HTTPException(status_code=404, detail="그룹을 찾을 수 없습니다.")

        return results[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"그룹 상세 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/members/{member_id}")
async def get_member(member_id: str):
    """
    특정 멤버 상세 조회

    - **member_id**: 멤버 ID (예: bangtansonyeondan:rm)
    """
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Neo4j 연결 안 됨")

    try:
        cypher = """
        MATCH (m:Member {member_id: $member_id})
        OPTIONAL MATCH (m)-[:MEMBER_OF]->(g:IdolGroup)
        OPTIONAL MATCH (m)-[:PARTICIPATED_IN]->(c:Content)

        RETURN m.member_id AS member_id,
               m.stage_name AS stage_name,
               m.legal_name AS legal_name,
               m.birth_date AS birth_date,
               m.roles AS roles,
               g.name_ko AS group_name,
               collect(DISTINCT {
                   content_id: c.content_id,
                   title: c.title,
                   type: c.content_type,
                   role: c.role
               }) AS activities
        """

        results = neo4j_client.query(cypher, {"member_id": member_id})

        if not results:
            raise HTTPException(status_code=404, detail="멤버를 찾을 수 없습니다.")

        return results[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"멤버 상세 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
