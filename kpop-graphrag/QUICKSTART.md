# K-POP GraphRAG 빠른 시작 가이드

5분 안에 K-POP 그래프 RAG 시스템을 실행해보세요!

## 1. 환경 설정 (2분)

### 1.1 저장소 클론 및 의존성 설치

```bash
cd kpop-graphrag

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 1.2 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 설정하세요:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...  # Claude API 키
NEO4J_PASSWORD=kpop_graphrag_2024   # Neo4j 비밀번호
```

**API 키 발급:**
- [Anthropic Console](https://console.anthropic.com/) → API Keys

### 1.3 Neo4j 실행 (Docker)

```bash
# Neo4j 컨테이너 실행
docker-compose up -d neo4j

# 실행 확인
docker ps
```

**브라우저에서 접속:**
- URL: http://localhost:7474
- 사용자: `neo4j`
- 비밀번호: `kpop_graphrag_2024`

## 2. 데이터 파이프라인 실행 (3분)

### 2.1 위키 텍스트 → JSON 추출

제공된 샘플 데이터(BTS)로 테스트:

```bash
python scripts/run_extraction.py \
  --input data/raw/sample_bts.txt \
  --title "방탄소년단"
```

**출력:**
```
추출 완료!
  그룹: 1개
  멤버: 7개
  기획사: 1개
  콘텐츠: 15개
출력 파일: data/extracted/sample_bts.json
```

### 2.2 JSON → Neo4j 적재

```bash
python scripts/load_to_neo4j.py \
  --input data/extracted/sample_bts.json \
  --init-schema
```

**출력:**
```
✓ Neo4j 연결 성공
✓ 스키마 초기화 완료
적재 완료!
  총 그룹: 1개
  총 멤버: 7개
  총 기획사: 1개
  총 콘텐츠: 15개
```

### 2.3 Neo4j 브라우저에서 확인

Neo4j 브라우저(http://localhost:7474)에서 아래 쿼리 실행:

```cypher
// 전체 그래프 시각화
MATCH (n)
RETURN n
LIMIT 100
```

```cypher
// BTS 활동 타임라인
MATCH (g:IdolGroup {group_id: "bangtansonyeondan"})-[:HAS_ACTIVITY]->(c:Content)
RETURN c.title, c.release_date, c.content_type
ORDER BY c.release_date
```

```cypher
// 멤버 개인 활동
MATCH (m:Member)-[:PARTICIPATED_IN]->(c:Content)
WHERE c.content_type = "ALBUM"
RETURN m.stage_name, c.title, c.release_date
```

## 3. 추가 위키 데이터 추가 (선택)

### 3.1 위키피디아에서 텍스트 복사

예: [블랙핑크 위키](https://ko.wikipedia.org/wiki/블랙핑크)

```bash
# 텍스트를 data/raw/blackpink.txt로 저장
```

### 3.2 추출 및 적재

```bash
# 추출
python scripts/run_extraction.py \
  --input data/raw/blackpink.txt \
  --title "블랙핑크"

# 적재
python scripts/load_to_neo4j.py \
  --input data/extracted/blackpink.json
```

### 3.3 다중 파일 일괄 처리

```bash
# data/raw/에 여러 .txt 파일 배치 후

# 일괄 추출
for file in data/raw/*.txt; do
  python scripts/run_extraction.py --input "$file"
done

# 일괄 적재
python scripts/load_to_neo4j.py --input data/extracted/
```

## 4. GraphRAG 인덱싱 (예정)

**현재 상태:** Neo4j 그래프 구축 완료 ✅
**다음 단계:** Microsoft GraphRAG 커뮤니티 탐지 및 요약

```bash
# (구현 예정)
python scripts/build_graphrag_index.py
```

## 5. 유용한 Cypher 쿼리 예제

### 그룹별 활동 통계

```cypher
MATCH (g:IdolGroup)-[:HAS_ACTIVITY]->(c:Content)
RETURN g.name_ko AS 그룹명,
       count(c) AS 총활동수,
       collect(DISTINCT c.content_type) AS 활동유형
ORDER BY 총활동수 DESC
```

### 기획사별 그룹 목록

```cypher
MATCH (a:Agency)<-[:MANAGED_BY]-(g:IdolGroup)
RETURN a.name AS 기획사,
       collect(g.name_ko) AS 소속그룹,
       count(g) AS 그룹수
```

### 연도별 활동 밀도

```cypher
MATCH (c:Content)
WHERE c.release_date IS NOT NULL
RETURN c.release_date.year AS 연도,
       c.content_type AS 유형,
       count(*) AS 건수
ORDER BY 연도 DESC, 건수 DESC
```

### 멤버 간 협업 (콜라보)

```cypher
MATCH (m1:Member)-[:PARTICIPATED_IN]->(c:Content {content_type: "COLLAB"})<-[:PARTICIPATED_IN]-(m2:Member)
WHERE m1.member_id < m2.member_id
RETURN m1.stage_name, m2.stage_name, c.title
```

### 특정 연도의 수상 내역

```cypher
MATCH (g:IdolGroup)-[:HAS_ACTIVITY]->(c:Content {content_type: "AWARD"})
WHERE c.release_date.year = 2021
RETURN g.name_ko, c.title, c.release_date
ORDER BY c.release_date
```

## 문제 해결

### "ANTHROPIC_API_KEY가 설정되지 않았습니다"

`.env` 파일에 올바른 API 키를 추가했는지 확인:

```bash
cat .env  # 내용 확인
source .env  # 환경변수 로드 (필요 시)
```

### Neo4j 연결 실패

```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs kpop-neo4j

# 재시작
docker-compose restart neo4j
```

### JSON 파싱 오류

LLM 응답이 유효한 JSON이 아닐 수 있습니다. `--log-level DEBUG`로 재실행:

```bash
python scripts/run_extraction.py \
  --input data/raw/sample.txt \
  --log-level DEBUG
```

## 다음 단계

1. **더 많은 데이터 수집**: 위키피디아, 나무위키 등에서 K-POP 그룹 문서 수집
2. **GraphRAG 완성**: 커뮤니티 탐지 및 요약 기능 추가
3. **질의응답 API**: FastAPI 서버 구축하여 REST API 제공
4. **대시보드**: 그래프 시각화 웹 인터페이스

---

**질문이나 이슈가 있으면 GitHub Issues에 등록해주세요!**
