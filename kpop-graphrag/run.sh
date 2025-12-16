#!/bin/bash
# K-POP GraphRAG 실행 스크립트
# 사용법: ./run.sh

set -e  # 에러 발생 시 중단

echo "🎵 K-POP GraphRAG 시스템 실행 스크립트"
echo "========================================"
echo ""

# 1. 환경 확인
echo "1️⃣  환경 확인 중..."
python3 --version || { echo "❌ Python 3.11+ 필요"; exit 1; }
docker --version || { echo "❌ Docker 필요"; exit 1; }
echo "✅ Python 및 Docker 확인 완료"
echo ""

# 2. API 키 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. 생성 중..."
    cp .env.example .env
    echo "❗ .env 파일을 열어서 ANTHROPIC_API_KEY를 추가하세요!"
    echo "   예: ANTHROPIC_API_KEY=sk-ant-api03-..."
    echo ""
    read -p "API 키를 추가했으면 Enter를 누르세요..."
fi

# API 키 확인
source .env
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY가 설정되지 않았습니다."
    echo "   .env 파일을 열어서 API 키를 추가하세요."
    exit 1
fi
echo "✅ API 키 확인 완료"
echo ""

# 3. 가상환경 확인 및 생성
echo "2️⃣  Python 가상환경 설정 중..."
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "✅ 가상환경 활성화 완료"
echo ""

# 4. 의존성 설치
echo "3️⃣  의존성 설치 중..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ 의존성 설치 완료"
echo ""

# 5. Neo4j 실행
echo "4️⃣  Neo4j 실행 중..."
docker compose up -d neo4j 2>/dev/null || docker-compose up -d neo4j

echo "Neo4j 시작 대기 중 (15초)..."
sleep 15
echo "✅ Neo4j 실행 완료"
echo "   URL: http://localhost:7474"
echo "   ID: neo4j"
echo "   PW: kpop_graphrag_2024"
echo ""

# 6. 샘플 데이터 처리
echo "5️⃣  샘플 데이터 처리 중..."
echo ""
echo "📄 BTS 위키 텍스트 → JSON 추출 중..."
python scripts/run_extraction.py \
    --input data/raw/sample_bts.txt \
    --title "방탄소년단"

echo ""
echo "📊 JSON → Neo4j 적재 중..."
python scripts/load_to_neo4j.py \
    --input data/extracted/sample_bts.json \
    --init-schema

echo ""
echo "✅ 샘플 데이터 처리 완료"
echo ""

# 7. 완료 안내
echo "========================================"
echo "🎉 설치 및 초기 데이터 로드 완료!"
echo "========================================"
echo ""
echo "다음 단계:"
echo ""
echo "1. Neo4j 브라우저 확인:"
echo "   http://localhost:7474"
echo "   (ID: neo4j, PW: kpop_graphrag_2024)"
echo ""
echo "2. Cypher 쿼리 테스트:"
echo "   MATCH (g:IdolGroup)-[:HAS_ACTIVITY]->(c:Content)"
echo "   RETURN g.name_ko, c.title, c.release_date"
echo "   ORDER BY c.release_date"
echo ""
echo "3. API 서버 실행:"
echo "   python src/api/server.py"
echo "   → http://localhost:8000/docs"
echo ""
echo "4. 더 많은 데이터 수집:"
echo "   python scripts/crawl_wikipedia.py --limit 10"
echo ""
echo "5. 전체 파이프라인 실행:"
echo "   python scripts/run_full_pipeline.py --crawl-limit 5"
echo ""
