"""API 테스트"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def client():
    """테스트 클라이언트"""
    from src.api.server import app
    return TestClient(app)


def test_root(client):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "K-POP GraphRAG API"


def test_health(client):
    """헬스체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "neo4j_connected" in data
    assert "query_engine_ready" in data


@pytest.mark.skipif(
    not Path(".env").exists(),
    reason="환경변수 파일 없음"
)
def test_query(client):
    """쿼리 엔드포인트 테스트"""
    response = client.post(
        "/query",
        json={
            "question": "테스트 질문",
            "mode": "cypher",
            "k": 5
        }
    )
    # Neo4j 연결이 없을 수 있으므로 200 또는 503 허용
    assert response.status_code in [200, 503]


def test_query_invalid_mode(client):
    """잘못된 모드 테스트"""
    response = client.post(
        "/query",
        json={
            "question": "테스트",
            "mode": "invalid_mode",
            "k": 5
        }
    )
    # 검증 오류 또는 처리 오류
    assert response.status_code in [422, 500, 503]


def test_groups_list(client):
    """그룹 목록 테스트"""
    response = client.get("/groups?limit=10")
    # Neo4j 연결이 없을 수 있음
    assert response.status_code in [200, 503]


def test_group_detail_not_found(client):
    """존재하지 않는 그룹 테스트"""
    response = client.get("/groups/nonexistent_group_id")
    # 404 또는 503
    assert response.status_code in [404, 503]
