# K-POP GraphRAG 실행 가이드 (초보자용)

## 🚀 가장 빠른 방법 (윈도우/맥/리눅스 공통)

### 필요한 것
1. **Python 3.11 이상** - [다운로드](https://www.python.org/downloads/)
2. **Docker Desktop** - [다운로드](https://www.docker.com/products/docker-desktop/)
3. **Anthropic API 키** - [발급](https://console.anthropic.com/)

---

## 📋 1단계: 프로젝트 준비

### 프로젝트 다운로드/클론

```bash
# Git으로 클론하는 경우
git clone <repository-url>
cd kpop-graphrag

# 또는 ZIP 파일 다운로드 후 압축 해제
cd kpop-graphrag
```

---

## ⚙️ 2단계: 환경 설정 (1번만)

### Windows (PowerShell)

```powershell
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
.\venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. .env 파일 생성
copy .env.example .env

# 5. .env 파일 편집 (메모장으로)
notepad .env
```

### Mac/Linux (터미널)

```bash
# 1. 가상환경 생성
python3 -m venv venv

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. .env 파일 생성
cp .env.example .env

# 5. .env 파일 편집
nano .env
# 또는
open .env  # Mac
```

### .env 파일에 API 키 추가

`.env` 파일을 열어서 다음 줄을 수정:

```env
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE
```

**API 키 발급 방법:**
1. https://console.anthropic.com/ 접속
2. 로그인 (계정 없으면 가입)
3. API Keys 메뉴 클릭
4. "Create Key" 클릭
5. 생성된 키 복사해서 붙여넣기

---

## 🐳 3단계: Neo4j 실행

### Docker Desktop 확인
- Docker Desktop이 실행 중인지 확인 (트레이 아이콘)
- 실행 안 되어 있으면 실행

### Neo4j 컨테이너 시작

```bash
# Windows/Mac/Linux 공통
docker compose up -d neo4j
```

**또는 (구버전 Docker)**
```bash
docker-compose up -d neo4j
```

### Neo4j 접속 확인

브라우저에서 http://localhost:7474 접속

- **Username**: neo4j
- **Password**: kpop_graphrag_2024

"Connect" 클릭 → 연결 성공하면 OK!

---

## 🎯 4단계: 샘플 데이터로 테스트

### 방법 1: 단계별 실행 (추천)

```bash
# 가상환경이 활성화된 상태에서

# 1. 위키 텍스트 → JSON 추출
python scripts/run_extraction.py \
    --input data/raw/sample_bts.txt \
    --title "방탄소년단"
```

**예상 결과:**
```
추출 완료!
  그룹: 1개
  멤버: 7개
  기획사: 2개
  콘텐츠: 18개
출력 파일: data/extracted/sample_bts.json
```

```bash
# 2. JSON → Neo4j 적재
python scripts/load_to_neo4j.py \
    --input data/extracted/sample_bts.json \
    --init-schema
```

**예상 결과:**
```
✓ Neo4j 연결 성공
✓ 스키마 초기화 완료
적재 완료!
  총 그룹: 1개
  총 멤버: 7개
```

### 방법 2: 자동 스크립트 실행 (Mac/Linux)

```bash
# run.sh 실행
./run.sh
```

**Windows는 수동으로 단계별 실행 권장**

---

## 🔍 5단계: 결과 확인

### Neo4j 브라우저에서 쿼리

http://localhost:7474 에서 다음 쿼리 실행:

```cypher
// 1. 전체 그래프 보기
MATCH (n)
RETURN n
LIMIT 50
```

```cypher
// 2. BTS 활동 타임라인
MATCH (g:IdolGroup {name_ko: "방탄소년단"})-[:HAS_ACTIVITY]->(c:Content)
RETURN c.title AS 제목,
       c.release_date AS 날짜,
       c.content_type AS 유형
ORDER BY c.release_date
```

```cypher
// 3. 멤버 목록
MATCH (m:Member)-[:MEMBER_OF]->(g:IdolGroup {name_ko: "방탄소년단"})
RETURN m.stage_name AS 활동명,
       m.legal_name AS 본명,
       m.roles AS 역할
```

```cypher
// 4. 멤버 개인 활동
MATCH (m:Member)-[:PARTICIPATED_IN]->(c:Content)
WHERE c.content_type = "ALBUM"
RETURN m.stage_name AS 멤버,
       c.title AS 앨범,
       c.release_date AS 발매일
ORDER BY c.release_date
```

---

## 🌐 6단계: API 서버 실행

```bash
# 새 터미널 열기 (가상환경 활성화 필요)
python src/api/server.py
```

**예상 출력:**
```
🚀 서버 준비 완료!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### API 문서 확인

브라우저에서:
- **Swagger UI**: http://localhost:8000/docs

### API 테스트

**새 터미널에서:**

```bash
# 질의응답 테스트
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "BTS 멤버는?", "mode": "hybrid"}'
```

**또는 Swagger UI에서:**
1. http://localhost:8000/docs 접속
2. `/query` 엔드포인트 클릭
3. "Try it out" 클릭
4. Request body에 입력:
   ```json
   {
     "question": "BTS의 2020년 활동은?",
     "mode": "hybrid",
     "k": 10
   }
   ```
5. "Execute" 클릭

---

## 📊 7단계: 더 많은 데이터 수집 (선택)

### 위키피디아에서 K-POP 그룹 자동 수집

```bash
# 10개 그룹 크롤링
python scripts/crawl_wikipedia.py --limit 10
```

**예상 결과:**
```
크롤링 완료! 총 10개 파일 저장
출력 디렉토리: data/raw
```

### 전체 파이프라인 실행

```bash
# 크롤링 → 추출 → 적재 → 인덱싱 (한 번에)
python scripts/run_full_pipeline.py \
    --crawl-limit 5 \
    --init-schema
```

---

## 🐛 문제 해결

### "ANTHROPIC_API_KEY가 설정되지 않았습니다"

→ `.env` 파일 확인:
```bash
cat .env  # Mac/Linux
type .env  # Windows
```

API 키가 제대로 입력되었는지 확인

### "Neo4j 연결 실패"

→ Docker 실행 확인:
```bash
docker ps
```

`kpop-neo4j` 컨테이너가 보이면 정상

안 보이면:
```bash
docker compose up -d neo4j
```

### "ModuleNotFoundError"

→ 가상환경 활성화 확인:

**Windows:**
```powershell
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

활성화되면 프롬프트 앞에 `(venv)` 표시됨

→ 의존성 재설치:
```bash
pip install -r requirements.txt
```

### "docker: command not found"

→ Docker Desktop 설치 확인
- https://www.docker.com/products/docker-desktop/

설치 후 재시작

---

## ✅ 체크리스트

실행 전 확인:

- [ ] Python 3.11+ 설치됨
- [ ] Docker Desktop 설치 및 실행 중
- [ ] Anthropic API 키 발급함
- [ ] 프로젝트 다운로드/클론함
- [ ] 가상환경 생성 및 활성화
- [ ] 의존성 설치 완료
- [ ] .env 파일에 API 키 입력
- [ ] Neo4j 컨테이너 실행 중
- [ ] http://localhost:7474 접속 가능

---

## 💡 추천 학습 순서

1. **샘플 데이터 실행** (단계 1-5) ← 여기서 시작!
2. **Neo4j 쿼리 연습** (단계 5)
3. **API 서버 실행** (단계 6)
4. **데이터 추가 수집** (단계 7)
5. **커스터마이징** (프롬프트 수정 등)

---

## 📞 도움이 필요하면

1. **에러 메시지 전체** 복사
2. **실행한 명령어** 기록
3. **환경 정보** (OS, Python 버전 등)

위 정보와 함께 질문하시면 빠르게 도와드릴 수 있습니다!

---

**지금 바로 시작하세요!** 🚀

```bash
# 1단계부터 순서대로!
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```
