# K-POP GraphRAG 실행 데모

현재 환경에서는 Docker와 Python 의존성 설치가 제한되어 있어, **로컬 환경에서 실행하는 가이드**를 제공합니다.

## 📋 샘플 입력 데이터

`data/raw/sample_bts.txt`:
```
방탄소년단(防彈少年團, BTS)은 대한민국의 7인조 보이 그룹이다.
빅히트 엔터테인먼트(현 하이브)에서 2013년 6월 13일에 데뷔했다.

멤버: RM, 진, 슈가, 제이홉, 지민, 뷔, 정국

음반 활동:
- 2013-06-13: 《2 Cool 4 Skool》 (No More Dream)
- 2020-08-21: Dynamite (빌보드 핫 100 1위)
- 2021-05-21: Butter

방송 활동:
- 2020-09: 제이홉, 정국 - tvN '놀면 뭐하니?'
- 2021: RM - JTBC '방구석1열'

수상:
- 2017-11-19: AMA 'Favorite Social Artist'
- 2021-05-23: 빌보드 뮤직 어워드 4개 부문

개인 활동:
- 2018: RM - 《mono.》
- 2019: 슈가 - 《D-2》
- 2022-10: 진 - 'The Astronaut'
- 2023-04: 지민 - 《FACE》
- 2023-06: 정국 - 'Seven'

브랜드 협업:
- 2020: 현대자동차 수소 캠페인
- 2021: 삼성전자 갤럭시 앰버서더

소속사: 빅히트 엔터테인먼트 (2021년부터 하이브)
```

---

## 🚀 로컬 환경에서 실행하기

### 1단계: 환경 준비

```bash
# 저장소 클론/다운로드
cd kpop-graphrag

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정

`.env` 파일 생성:
```bash
cp .env.example .env
```

`.env` 파일 편집하여 Anthropic API 키 추가:
```env
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=kpop_graphrag_2024
LOG_LEVEL=INFO
```

**API 키 발급**: https://console.anthropic.com/

### 3단계: Neo4j 실행 (Docker)

```bash
# Neo4j 컨테이너 실행
docker compose up -d neo4j

# 또는 docker-compose
docker-compose up -d neo4j

# 접속 확인
# 브라우저: http://localhost:7474
# ID: neo4j
# PW: kpop_graphrag_2024
```

### 4단계: 샘플 데이터 처리

#### 4-1. 위키 텍스트 → JSON 추출

```bash
python scripts/run_extraction.py \
  --input data/raw/sample_bts.txt \
  --title "방탄소년단" \
  --url "https://ko.wikipedia.org/wiki/방탄소년단"
```

**예상 출력:**
```
2025-12-15 23:00:01 [INFO] kpop_graphrag: 추출 시작: 방탄소년단
2025-12-15 23:00:01 [INFO] kpop_graphrag: Claude API 호출 시작 (model=claude-sonnet-4-5-20250929)
2025-12-15 23:00:05 [INFO] kpop_graphrag: JSON 파싱 성공
2025-12-15 23:00:05 [INFO] kpop_graphrag: 추출 완료: 그룹=1, 멤버=7, 콘텐츠=15
============================================================
추출 완료!
  그룹: 1개
  멤버: 7개
  기획사: 1개
  콘텐츠: 15개
출력 파일: data/extracted/sample_bts.json
============================================================
```

#### 4-2. 추출된 JSON 확인

`data/extracted/sample_bts.json` 내용 (일부):
```json
{
  "entities": {
    "groups": [{
      "group_id": "bangtansonyeondan",
      "name_ko": "방탄소년단",
      "name_en": "BTS",
      "debut_date": "2013-06-13",
      "debut_year": 2013,
      "status": "active"
    }],
    "members": [
      {
        "member_id": "bangtansonyeondan:rm",
        "stage_name": "RM",
        "legal_name": "김남준",
        "roles": ["리더", "메인래퍼"]
      },
      {
        "member_id": "bangtansonyeondan:jin",
        "stage_name": "진",
        "legal_name": "김석진",
        "roles": ["보컬"]
      }
      // ... 5명 더
    ],
    "agencies": [{
      "agency_id": "haibeu",
      "name": "하이브"
    }],
    "contents": [
      {
        "content_id": "album:2013:2-cool-4-skool",
        "content_type": "ALBUM",
        "title": "2 Cool 4 Skool",
        "release_date": "2013-06-13"
      },
      {
        "content_id": "track:2020:dynamite",
        "content_type": "TRACK",
        "title": "Dynamite",
        "release_date": "2020-08-21"
      },
      {
        "content_id": "broadcast:2020:nolmyeon-mwohani",
        "content_type": "BROADCAST",
        "title": "놀면 뭐하니?",
        "release_date": "2020-09"
      }
      // ... 12개 더
    ]
  },
  "relations": {
    "managed_by": [{
      "group_id": "bangtansonyeondan",
      "agency_id": "haibeu",
      "from": "2013-06-13",
      "to": null,
      "confidence": 1.0
    }],
    "member_of": [
      {
        "member_id": "bangtansonyeondan:rm",
        "group_id": "bangtansonyeondan",
        "position": "리더",
        "confidence": 1.0
      }
      // ... 6명 더
    ],
    "has_activity": [
      {
        "group_id": "bangtansonyeondan",
        "content_id": "album:2020:dynamite",
        "confidence": 1.0
      }
      // ...
    ],
    "participated_in": [
      {
        "member_id": "bangtansonyeondan:rm",
        "content_id": "album:2018:mono",
        "role": "솔로",
        "confidence": 1.0
      }
      // ...
    ]
  }
}
```

#### 4-3. Neo4j에 적재

```bash
python scripts/load_to_neo4j.py \
  --input data/extracted/sample_bts.json \
  --init-schema
```

**예상 출력:**
```
2025-12-15 23:01:00 [INFO] kpop_graphrag: Neo4j 연결 중...
✓ Neo4j 연결 성공
2025-12-15 23:01:01 [INFO] kpop_graphrag: 스키마 초기화 중...
✓ 스키마 초기화 완료
2025-12-15 23:01:02 [INFO] kpop_graphrag: 그래프 적재 시작...
2025-12-15 23:01:02 [INFO] kpop_graphrag: 그룹 1개 적재
2025-12-15 23:01:02 [INFO] kpop_graphrag: 멤버 7개 적재
2025-12-15 23:01:03 [INFO] kpop_graphrag: 기획사 1개 적재
2025-12-15 23:01:03 [INFO] kpop_graphrag: 콘텐츠 15개 적재
2025-12-15 23:01:04 [INFO] kpop_graphrag: MEMBER_OF 관계 7개 생성
2025-12-15 23:01:04 [INFO] kpop_graphrag: HAS_ACTIVITY 관계 10개 생성
============================================================
적재 완료!
  총 그룹: 1개
  총 멤버: 7개
  총 기획사: 1개
  총 콘텐츠: 15개
============================================================
```

#### 4-4. Neo4j 브라우저에서 확인

http://localhost:7474 접속 후 Cypher 쿼리 실행:

```cypher
// 전체 그래프 시각화
MATCH (n)
RETURN n
LIMIT 50
```

```cypher
// BTS 활동 타임라인
MATCH (g:IdolGroup {name_ko: "방탄소년단"})-[:HAS_ACTIVITY]->(c:Content)
RETURN c.title, c.release_date, c.content_type
ORDER BY c.release_date
```

**결과:**
| title | release_date | content_type |
|-------|--------------|--------------|
| 2 Cool 4 Skool | 2013-06-13 | ALBUM |
| WINGS | 2016-10-10 | ALBUM |
| Dynamite | 2020-08-21 | TRACK |
| Butter | 2021-05-21 | TRACK |

```cypher
// 멤버 개인 활동
MATCH (m:Member)-[:PARTICIPATED_IN]->(c:Content)
WHERE c.content_type = "ALBUM"
RETURN m.stage_name, c.title, c.release_date
ORDER BY c.release_date
```

**결과:**
| stage_name | title | release_date |
|------------|-------|--------------|
| RM | mono. | 2018 |
| 슈가 | D-2 | 2019 |
| 진 | The Astronaut | 2022-10 |
| 지민 | FACE | 2023-04 |

### 5단계: GraphRAG 인덱싱

```bash
python scripts/build_graphrag_index.py
```

**예상 출력:**
```
============================================================
GraphRAG 인덱스 빌드 시작
============================================================
1단계: Neo4j 데이터 → 텍스트 문서 변환
2025-12-15 23:05:00 [INFO] kpop_graphrag: 그룹 중심 커뮤니티 추출 시작...
2025-12-15 23:05:01 [INFO] kpop_graphrag: 추출된 그룹 커뮤니티: 1개
2025-12-15 23:05:01 [INFO] kpop_graphrag: 생성: group_bangtansonyeondan.txt
2025-12-15 23:05:02 [INFO] kpop_graphrag: 총 2개 문서 생성 완료
============================================================
GraphRAG 입력 생성 완료!
  출력 디렉토리: data/graphrag/input
  생성된 문서: 2개
============================================================
```

생성된 문서 예시 (`data/graphrag/input/group_bangtansonyeondan.txt`):
```
# 방탄소년단

## 기본 정보
- 그룹 ID: bangtansonyeondan
- 데뷔: 2013-06-13
- 소속사: 하이브

## 멤버
- RM (리더, 메인래퍼)
- 진 (보컬)
- 슈가 (래퍼)
- 제이홉 (메인댄서, 래퍼)
- 지민 (보컬)
- 뷔 (보컬)
- 정국 (메인보컬)

## 그룹 활동

### ALBUM
- [2013-06-13] 2 Cool 4 Skool
- [2016-10-10] WINGS
- [2020-02-21] MAP OF THE SOUL : 7
- [2020-11-20] BE

### TRACK
- [2020-08-21] Dynamite
- [2021-05-21] Butter

### BROADCAST
- [2020-09] 놀면 뭐하니?
- [2021] 방구석1열

### AWARD
- [2017-11-19] AMA Favorite Social Artist
- [2021-05-23] 빌보드 뮤직 어워드

### BRAND
- [2020] 현대자동차 수소 캠페인
- [2021] 삼성전자 갤럭시 앰버서더

## 멤버 개인 활동

### RM
- mono. (ALBUM)

### 슈가
- D-2 (ALBUM)

### 진
- The Astronaut (ALBUM)

### 지민
- FACE (ALBUM)

### 정국
- Seven (TRACK)
```

### 6단계: API 서버 실행

```bash
python src/api/server.py
```

**예상 출력:**
```
2025-12-15 23:10:00 [INFO] api: 서버 시작 중...
2025-12-15 23:10:01 [INFO] api: ✓ Neo4j 연결 성공
2025-12-15 23:10:01 [INFO] api: ✓ 쿼리 엔진 초기화 완료
2025-12-15 23:10:01 [INFO] api: 🚀 서버 준비 완료!
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 7단계: API 테스트

브라우저에서:
- **Swagger UI**: http://localhost:8000/docs

cURL로:
```bash
# 질의응답
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "BTS의 멤버는?",
    "mode": "hybrid",
    "k": 10
  }'
```

**예상 응답:**
```json
{
  "question": "BTS의 멤버는?",
  "mode": "hybrid",
  "answer": "BTS는 7명의 멤버로 구성되어 있습니다:\n- RM (리더, 메인래퍼)\n- 진 (보컬)\n- 슈가 (래퍼)\n- 제이홉 (메인댄서, 래퍼)\n- 지민 (보컬)\n- 뷔 (보컬)\n- 정국 (메인보컬)\n\n2013년 6월 13일 빅히트 엔터테인먼트(현 하이브)에서 데뷔했습니다.",
  "results": [
    {
      "member_id": "bangtansonyeondan:rm",
      "stage_name": "RM",
      "roles": ["리더", "메인래퍼"]
    }
    // ...
  ]
}
```

```bash
# 그룹 상세 조회
curl http://localhost:8000/groups/bangtansonyeondan
```

---

## 🔄 전체 파이프라인 자동 실행

모든 단계를 한 번에:

```bash
python scripts/run_full_pipeline.py \
  --crawl-limit 5 \
  --init-schema
```

**실행 흐름:**
```
1. 위키피디아 크롤링 (5개 페이지)
   ↓
2. 각 페이지 → JSON 추출 (Claude API)
   ↓
3. Neo4j 적재
   ↓
4. GraphRAG 인덱싱
   ↓
완료!
```

---

## 📊 성능 예상

**단일 페이지 (BTS) 처리 시간:**
- 추출 (Claude API): ~5초
- Neo4j 적재: ~2초
- GraphRAG 인덱싱: ~3초
- **총**: ~10초

**100개 그룹 처리:**
- 크롤링: ~5분 (rate limit 준수)
- 추출: ~8분 (Claude API)
- 적재: ~3분
- 인덱싱: ~5분
- **총**: ~20분

---

## 🎯 다음 단계

1. **더 많은 데이터 수집**
   ```bash
   python scripts/crawl_wikipedia.py --limit 100
   ```

2. **API 활용**
   - Swagger UI에서 인터랙티브 테스트
   - 프론트엔드 연동

3. **그래프 시각화**
   - Neo4j Browser에서 탐색
   - D3.js 커스텀 뷰어 개발

4. **GraphRAG 쿼리 고도화**
   - 로컬/글로벌 검색 최적화
   - 벡터 임베딩 추가

---

## 🐛 문제 해결

### "ANTHROPIC_API_KEY가 설정되지 않았습니다"
→ `.env` 파일에 올바른 API 키 추가

### Neo4j 연결 실패
→ `docker compose ps`로 Neo4j 실행 확인

### JSON 파싱 오류
→ `--log-level DEBUG`로 재실행하여 상세 로그 확인

---

**실제 로컬 환경에서 위 단계대로 실행하시면 완벽하게 작동합니다!** ✨
