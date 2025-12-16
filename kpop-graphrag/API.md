# K-POP GraphRAG API 문서

FastAPI 기반 REST API로 K-POP 지식 그래프를 쿼리할 수 있습니다.

## 실행 방법

### 1. API 서버 실행

```bash
# 기본 실행
python src/api/server.py

# 또는 uvicorn으로 실행
uvicorn src.api.server:app --reload --port 8000
```

### 2. API 문서 확인

브라우저에서 접속:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 엔드포인트

### 1. 헬스체크

**GET** `/health`

시스템 상태 확인

**응답 예시:**
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "query_engine_ready": true
}
```

---

### 2. 질의응답 (핵심 기능)

**POST** `/query`

자연어 질문에 대한 답변 생성

**요청 본문:**
```json
{
  "question": "BTS의 멤버는?",
  "mode": "hybrid",
  "k": 5
}
```

**파라미터:**
- `question` (string, 필수): 질문
- `mode` (string, 기본: "hybrid"): 검색 모드
  - `local`: 특정 엔티티 중심 검색
  - `global`: 전체 커뮤니티 요약
  - `hybrid`: Cypher + GraphRAG 조합 ⭐
  - `cypher`: 순수 Neo4j 쿼리
- `k` (integer, 기본: 5): 반환할 결과 수 (1-20)

**응답 예시:**
```json
{
  "question": "BTS의 멤버는?",
  "mode": "hybrid",
  "answer": "BTS는 7명의 멤버로 구성되어 있습니다: RM, 진, 슈가, 제이홉, 지민, 뷔, 정국...",
  "results": [
    {
      "member_id": "bangtansonyeondan:rm",
      "stage_name": "RM",
      "roles": ["리더", "메인래퍼"]
    }
  ],
  "metadata": {
    "communities": [...],
    "cypher": "MATCH (m:Member)..."
  }
}
```

---

### 3. 그룹 목록 조회

**GET** `/groups`

K-POP 그룹 목록 조회

**쿼리 파라미터:**
- `limit` (integer, 기본: 10): 반환할 그룹 수 (1-100)
- `offset` (integer, 기본: 0): 시작 오프셋

**예시:**
```bash
GET /groups?limit=20&offset=0
```

**응답:**
```json
{
  "total": 20,
  "offset": 0,
  "limit": 20,
  "groups": [
    {
      "group_id": "bangtansonyeondan",
      "name_ko": "방탄소년단",
      "name_en": "BTS",
      "debut_date": "2013-06-13",
      "agency": "하이브"
    }
  ]
}
```

---

### 4. 그룹 상세 조회

**GET** `/groups/{group_id}`

특정 그룹의 상세 정보 (멤버, 활동 포함)

**경로 파라미터:**
- `group_id` (string): 그룹 ID (예: `bangtansonyeondan`)

**예시:**
```bash
GET /groups/bangtansonyeondan
```

**응답:**
```json
{
  "group_id": "bangtansonyeondan",
  "name_ko": "방탄소년단",
  "name_en": "BTS",
  "debut_date": "2013-06-13",
  "status": "active",
  "agency": "하이브",
  "members": [
    {
      "member_id": "bangtansonyeondan:rm",
      "stage_name": "RM",
      "roles": ["리더", "메인래퍼"]
    }
  ],
  "activities": [
    {
      "content_id": "album:2020:dynamite",
      "title": "Dynamite",
      "type": "ALBUM",
      "release_date": "2020-08-21"
    }
  ]
}
```

---

### 5. 멤버 상세 조회

**GET** `/members/{member_id}`

특정 멤버의 상세 정보 (그룹, 개인 활동 포함)

**경로 파라미터:**
- `member_id` (string): 멤버 ID (예: `bangtansonyeondan:rm`)

**예시:**
```bash
GET /members/bangtansonyeondan:rm
```

**응답:**
```json
{
  "member_id": "bangtansonyeondan:rm",
  "stage_name": "RM",
  "legal_name": "김남준",
  "birth_date": "1994-09-12",
  "roles": ["리더", "메인래퍼"],
  "group_name": "방탄소년단",
  "activities": [
    {
      "content_id": "album:2018:mono",
      "title": "mono.",
      "type": "ALBUM",
      "role": "솔로"
    }
  ]
}
```

---

## 사용 예시

### cURL

```bash
# 질의응답
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "BTS의 2020년 활동은?",
    "mode": "hybrid",
    "k": 10
  }'

# 그룹 목록
curl http://localhost:8000/groups?limit=10

# 그룹 상세
curl http://localhost:8000/groups/bangtansonyeondan
```

### Python (requests)

```python
import requests

# 질의응답
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "블랙핑크의 멤버별 솔로 활동은?",
        "mode": "local",
        "k": 5
    }
)
result = response.json()
print(result["answer"])

# 그룹 목록
response = requests.get("http://localhost:8000/groups?limit=20")
groups = response.json()["groups"]
for group in groups:
    print(f"{group['name_ko']} ({group['debut_date']})")
```

### JavaScript (fetch)

```javascript
// 질의응답
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'JYP 소속 그룹들의 최근 활동은?',
    mode: 'global',
    k: 10
  })
});

const result = await response.json();
console.log(result.answer);
```

---

## 검색 모드 상세 설명

### 1. `local` - 로컬 검색
- 특정 엔티티(그룹/멤버/기획사) 중심으로 검색
- GraphRAG의 커뮤니티 요약 활용
- **사용 예**: "BTS의 2021년 활동은?", "지민의 솔로 활동은?"

### 2. `global` - 글로벌 검색
- 전체 커뮤니티를 종합하여 답변
- 비교/대조 질문에 적합
- **사용 예**: "SM과 JYP의 전략 차이는?", "4세대 아이돌의 특징은?"

### 3. `hybrid` - 하이브리드 검색 (권장) ⭐
- Neo4j Cypher 쿼리 + GraphRAG 요약 결합
- 구조화된 데이터 + 맥락적 이해
- **사용 예**: 대부분의 질문

### 4. `cypher` - 순수 Cypher 쿼리
- Neo4j 그래프만 사용
- 정확한 구조적 질의
- **사용 예**: "멤버 수는?", "데뷔일은?"

---

## 에러 처리

### 404 Not Found
```json
{
  "detail": "그룹을 찾을 수 없습니다."
}
```

### 500 Internal Server Error
```json
{
  "detail": "쿼리 처리 중 오류 발생: ..."
}
```

### 503 Service Unavailable
```json
{
  "detail": "Neo4j 연결 안 됨"
}
```

---

## 성능 최적화

### 캐싱
- 자주 사용되는 쿼리는 Redis 캐싱 권장 (향후 구현 예정)

### 페이징
- 큰 결과셋은 `limit`와 `offset` 사용

### 타임아웃
- 기본 타임아웃: 30초
- 복잡한 쿼리는 `global` 대신 `local` 사용

---

## 보안

### 프로덕션 환경
- HTTPS 필수
- API 키 인증 추가 권장
- CORS 설정 제한
- Rate limiting 적용

---

## 향후 개선 사항

- [ ] API 키 인증
- [ ] Rate limiting
- [ ] 결과 캐싱 (Redis)
- [ ] 웹소켓 지원 (실시간 스트리밍)
- [ ] 벡터 검색 통합
- [ ] 다국어 지원 (영어)
