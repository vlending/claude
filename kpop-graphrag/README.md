# K-POP GraphRAG 시스템

위키피디아 텍스트에서 K-POP 그룹/멤버/기획사/활동 정보를 추출하여 Neo4j 그래프 DB 구축 및 GraphRAG 기반 질의응답 시스템

## 아키텍처

```
┌─────────────────┐
│  위키 텍스트     │
│  (한국어/영어)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  1. 추출 파이프라인          │
│  - Claude Sonnet 4.5        │
│  - 구조화 프롬프트          │
│  → JSON (엔티티/관계)       │
└────────┬────────────────────┘
         │
         ├──────────────────┐
         ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│  2-A. Neo4j     │  │  2-B. GraphRAG   │
│  (관계도 탐색)  │  │  (커뮤니티 요약) │
│                 │  │                  │
│  • 실시간 쿼리  │  │  • Leiden 커뮤니티│
│  • Cypher       │  │  • 계층적 요약    │
│  • 시각화       │  │  • 벡터 검색      │
└─────────────────┘  └──────────────────┘
         │                  │
         └────────┬─────────┘
                  ▼
         ┌─────────────────┐
         │  3. 쿼리 API     │
         │  - 그래프 탐색   │
         │  - 의미론적 검색 │
         │  - 하이브리드 RAG│
         └─────────────────┘
```

## 기술 스택

- **Language**: Python 3.11+
- **LLM**: Anthropic Claude Sonnet 4.5
- **Graph DB**: Neo4j 5.x
- **GraphRAG**: Microsoft GraphRAG
- **Vector Store**: Qdrant (내장)
- **Orchestration**: LangChain (optional)

## 프로젝트 구조

```
kpop-graphrag/
├── config/
│   ├── schema.yaml              # 그래프 스키마 정의
│   ├── extraction_prompts.yaml  # 추출 프롬프트
│   └── graphrag_settings.yaml   # GraphRAG 설정
│
├── src/
│   ├── extraction/
│   │   ├── wiki_loader.py       # 위키 텍스트 로더
│   │   ├── entity_extractor.py  # LLM 기반 엔티티 추출
│   │   └── normalizer.py        # 데이터 정규화
│   │
│   ├── graph/
│   │   ├── neo4j_client.py      # Neo4j 연결/쿼리
│   │   ├── schema_builder.py    # 스키마 초기화
│   │   └── data_loader.py       # 그래프 적재
│   │
│   ├── graphrag/
│   │   ├── indexer.py           # GraphRAG 인덱싱
│   │   ├── community_detector.py # 커뮤니티 탐지
│   │   └── query_engine.py      # 쿼리 엔진
│   │
│   ├── api/
│   │   ├── server.py            # FastAPI 서버
│   │   └── endpoints.py         # REST API
│   │
│   └── utils/
│       ├── llm_client.py        # Claude API 클라이언트
│       └── logger.py            # 로깅
│
├── data/
│   ├── raw/                     # 원본 위키 텍스트
│   ├── extracted/               # 추출된 JSON
│   ├── neo4j/                   # Neo4j import용 CSV
│   └── graphrag/                # GraphRAG 인덱스
│
├── notebooks/
│   ├── 01_extraction_demo.ipynb
│   ├── 02_graph_visualization.ipynb
│   └── 03_query_examples.ipynb
│
├── scripts/
│   ├── setup_neo4j.sh           # Neo4j 초기화
│   ├── run_extraction.py        # 추출 실행
│   ├── load_to_neo4j.py         # 그래프 적재
│   └── build_graphrag_index.py  # GraphRAG 인덱싱
│
├── tests/
│   ├── test_extraction.py
│   ├── test_neo4j.py
│   └── test_graphrag.py
│
├── docker-compose.yml           # Neo4j + Qdrant
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Neo4j 실행 (Docker)

```bash
docker-compose up -d neo4j
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일 편집:
# ANTHROPIC_API_KEY=sk-ant-...
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_password
```

### 4. 파이프라인 실행

```bash
# 1단계: 위키 텍스트 → JSON 추출
python scripts/run_extraction.py --input data/raw/wiki_pages.txt

# 2단계: JSON → Neo4j 적재
python scripts/load_to_neo4j.py --input data/extracted/

# 3단계: GraphRAG 인덱스 빌드
python scripts/build_graphrag_index.py --source neo4j

# 4단계: API 서버 실행
python src/api/server.py
```

## 핵심 기능

### 1. 엔티티/관계 추출

```python
from src.extraction.entity_extractor import KpopEntityExtractor

extractor = KpopEntityExtractor(model="claude-sonnet-4-5-20250929")
result = extractor.extract(wiki_text)

# result.entities: groups, members, agencies, contents
# result.relations: managed_by, member_of, has_activity, participated_in
```

### 2. Neo4j 그래프 탐색

```cypher
// 그룹의 전체 활동 타임라인
MATCH (g:IdolGroup {group_id: "bts"})-[:HAS_ACTIVITY]->(c:Content)
RETURN c.title, c.release_date, c.content_type
ORDER BY c.release_date

// 멤버의 개인 활동
MATCH (m:Member {member_id: "bts:jungkook"})-[:PARTICIPATED_IN]->(c:Content)
WHERE c.content_type IN ["BROADCAST", "COLLAB"]
RETURN c
```

### 3. GraphRAG 커뮤니티 쿼리

```python
from src.graphrag.query_engine import KpopQueryEngine

engine = KpopQueryEngine()

# 그룹 중심 커뮤니티 요약
answer = engine.query(
    "BTS의 2020-2023년 주요 활동을 시간순으로 요약해줘",
    mode="community"  # or "local", "global"
)
```

### 4. 하이브리드 쿼리 (Neo4j + GraphRAG)

```python
# 예: "JYP 소속 그룹들의 최근 3년 활동 비교"
result = engine.hybrid_query(
    cypher_query="MATCH (a:Agency {name: 'JYP'})<-[:MANAGED_BY]-(g:IdolGroup)...",
    graphrag_query="각 그룹의 활동 특징과 차이점 분석"
)
```

## 그래프 스키마

### 노드 타입

- **IdolGroup**: `group_id`, `name_ko`, `name_en`, `debut_date`, `status`
- **Member**: `member_id`, `stage_name`, `legal_name`, `birth_date`, `roles[]`
- **Agency**: `agency_id`, `name`
- **Content**: `content_id`, `content_type`, `title`, `release_date`, `summary`

### 관계 타입

- `(IdolGroup)-[:MANAGED_BY {from, to, confidence}]->(Agency)`
- `(Member)-[:MEMBER_OF {from, to, position, confidence}]->(IdolGroup)`
- `(IdolGroup)-[:HAS_ACTIVITY {confidence}]->(Content)`
- `(Member)-[:PARTICIPATED_IN {role, credit, confidence}]->(Content)`

### Content Type 분류

```
ALBUM | TRACK | MV | LIVE | BROADCAST | AWARD | COLLAB | BRAND | SOCIAL | ETC
```

## GraphRAG 커뮤니티 전략

### 그룹 중심 커뮤니티
- **구성**: 그룹 + 멤버 + 주요 활동
- **요약 템플릿**:
  ```
  ## {group_name} 활동 요약
  - 데뷔: {debut_date}
  - 멤버: {members_list}
  - 주요 활동 (연도순):
    • 앨범/싱글: ...
    • 방송/예능: ...
    • 수상: ...
  - 멤버 개인 활동: ...
  ```

### 기획사 중심 커뮤니티
- **구성**: 기획사 + 소속 그룹 + 변천사
- **요약 템플릿**:
  ```
  ## {agency_name} 소속 그룹
  - 현재 소속: {current_groups}
  - 과거 소속: {past_groups}
  - 기획사 주요 활동 패턴: ...
  - 그룹 간 협업: ...
  ```

## 예시 쿼리

### 질의응답 예시

1. **관계 탐색**: "BTS 멤버 중 솔로 앨범을 낸 멤버는?"
   - → Neo4j Cypher: `MATCH (m:Member)-[:MEMBER_OF]->(:IdolGroup {name_ko: "방탄소년단"})-[:PARTICIPATED_IN]->(c:Content {content_type: "ALBUM"})`

2. **시간적 분석**: "블랙핑크의 2022년 활동 정리"
   - → GraphRAG community query + 시간 필터

3. **비교 분석**: "SM과 JYP의 걸그룹 전략 차이"
   - → GraphRAG global query (다중 커뮤니티)

4. **트렌드 분석**: "최근 3년간 가장 많은 예능 출연을 한 그룹은?"
   - → Neo4j aggregation + GraphRAG 해석

## 성능 최적화

### 1. 추출 병렬화
- 위키 페이지별 독립 추출 → ThreadPoolExecutor

### 2. Neo4j 인덱싱
```cypher
CREATE INDEX group_id_index FOR (g:IdolGroup) ON (g.group_id);
CREATE INDEX member_id_index FOR (m:Member) ON (m.member_id);
CREATE INDEX content_type_index FOR (c:Content) ON (c.content_type);
```

### 3. GraphRAG 청크 크기 조정
- `config/graphrag_settings.yaml`:
  ```yaml
  chunk_size: 1200
  chunk_overlap: 100
  max_cluster_size: 10
  ```

## 전체 워크플로우

### 워크플로우 1: 자동 크롤링 → GraphRAG

```bash
# 전체 파이프라인 자동 실행
python scripts/run_full_pipeline.py --crawl-limit 20 --init-schema

# 결과:
# 1. 위키피디아에서 K-POP 그룹 페이지 20개 수집
# 2. Claude로 엔티티/관계 추출
# 3. Neo4j에 그래프 구축
# 4. GraphRAG 커뮤니티 인덱싱
```

### 워크플로우 2: 수동 데이터 추가

```bash
# 1. 위키 텍스트 저장
echo "블랙핑크는..." > data/raw/blackpink.txt

# 2. 추출
python scripts/run_extraction.py --input data/raw/blackpink.txt

# 3. 적재
python scripts/load_to_neo4j.py --input data/extracted/blackpink.json
```

### 워크플로우 3: API 쿼리

```python
import requests

# 질의응답
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "BTS의 2020년 활동은?", "mode": "hybrid"}
)
print(response.json()["answer"])

# 그룹 상세
response = requests.get("http://localhost:8000/groups/bangtansonyeondan")
group = response.json()
print(f"멤버: {[m['stage_name'] for m in group['members']]}")
```

---

## 문서

- **[QUICKSTART.md](QUICKSTART.md)**: 5분 빠른 시작 가이드
- **[API.md](API.md)**: REST API 상세 문서
- **config/schema.yaml**: Neo4j 스키마 및 Cypher 쿼리 예제
- **config/extraction_prompts.yaml**: 엔티티 추출 프롬프트

---

## 확장 계획

### 완료 ✅
- [x] 위키 텍스트 → 그래프 자동 변환
- [x] Neo4j 그래프 DB 구축
- [x] GraphRAG 커뮤니티 탐지 준비
- [x] REST API 서버
- [x] 위키피디아 자동 크롤러

### 진행 중 🚧
- [ ] Microsoft GraphRAG 완전 통합
- [ ] 벡터 검색 고도화

### 향후 계획 📋
- [ ] 실시간 업데이트 (위키 변경 감지)
- [ ] 다국어 지원 (영어 위키 통합)
- [ ] 소셜 미디어 데이터 추가 (YouTube, Twitter)
- [ ] 시각화 대시보드 (D3.js, vis.js)
- [ ] 추천 시스템 (유사 그룹/멤버 탐색)
- [ ] 모바일 앱 (React Native)

## 라이센스

MIT License

---

**Built for K-POP Research & Analysis**
