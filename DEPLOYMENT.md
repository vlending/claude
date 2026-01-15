# 🚀 아이돌 챗봇 배포 가이드

외부에서 접속 가능한 공개 URL로 배포하는 방법입니다.

## 방법 1: Railway 배포 (추천) ⭐

Railway는 무료 티어가 있고 매우 간단하게 배포할 수 있습니다.

### 1단계: Railway 계정 생성
1. [railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인

### 2단계: 새 프로젝트 생성
1. "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. 이 저장소 선택: `vlending/claude`
4. 브랜치 선택: `claude/idol-chatbot-prototype-mbnWY`

### 3단계: 환경 변수 설정
Railway 프로젝트 설정에서:
```
ANTHROPIC_API_KEY=your-actual-api-key-here
PORT=3000
```

### 4단계: 배포 완료!
- 자동으로 빌드되고 배포됩니다
- 공개 URL이 생성됩니다 (예: `https://idol-chatbot-production.up.railway.app`)
- 이 URL을 공유하면 누구나 접속 가능합니다!

---

## 방법 2: Render 배포

Render도 무료 티어가 있습니다.

### 1단계: Render 계정 생성
1. [render.com](https://render.com) 접속
2. GitHub 계정으로 로그인

### 2단계: 새 Web Service 생성
1. "New +" → "Web Service" 클릭
2. GitHub 저장소 연결: `vlending/claude`
3. 브랜치 선택: `claude/idol-chatbot-prototype-mbnWY`

### 3단계: 설정
```
Name: idol-chatbot
Environment: Node
Region: Singapore (가장 가까운 지역)
Branch: claude/idol-chatbot-prototype-mbnWY
Build Command: npm install && npm run build
Start Command: npm start
```

### 4단계: 환경 변수 설정
```
ANTHROPIC_API_KEY=your-actual-api-key-here
PORT=3000
```

### 5단계: 배포!
- "Create Web Service" 클릭
- 자동으로 배포됩니다 (5-10분 소요)
- 공개 URL: `https://idol-chatbot.onrender.com`

---

## 방법 3: Vercel 배포 (Serverless)

Vercel은 매우 빠르지만 Serverless 환경입니다.

### 1단계: Vercel 계정 생성
1. [vercel.com](https://vercel.com) 접속
2. GitHub 계정으로 로그인

### 2단계: 프로젝트 Import
1. "Add New..." → "Project" 클릭
2. GitHub 저장소 선택
3. 브랜치: `claude/idol-chatbot-prototype-mbnWY`

### 3단계: 설정
```
Framework Preset: Other
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 4단계: 환경 변수
```
ANTHROPIC_API_KEY=your-actual-api-key-here
```

### 5단계: 배포
- "Deploy" 클릭
- 공개 URL: `https://idol-chatbot.vercel.app`

---

## 방법 4: 로컬 터널 (임시 테스트용)

빠르게 테스트하고 싶다면 localtunnel 사용:

```bash
# 서버 실행 (이미 실행 중이라면 건너뛰기)
npm run idol:web

# 새 터미널에서
npx localtunnel --port 3000
```

공개 URL이 생성됩니다 (예: `https://silly-cat-12.loca.lt`)

**주의:**
- 이 URL은 임시적이며, 서버를 재시작하면 변경됩니다
- 프로덕션용이 아닙니다

---

## 추천 순서

1. **빠른 테스트**: localtunnel (5분)
2. **영구 배포**: Railway (10분) ⭐
3. **무료 티어**: Render (15분)
4. **Serverless**: Vercel (10분)

---

## 배포 후 확인 사항

배포가 완료되면:

1. ✅ 공개 URL 접속 확인
2. ✅ "대화 시작하기" 버튼 클릭
3. ✅ 아이돌과 대화 테스트
4. ✅ 모바일에서도 접속 테스트

---

## 트러블슈팅

### 빌드 실패
```
npm install
npm run build
```
로컬에서 먼저 테스트

### API 키 오류
환경 변수가 제대로 설정되었는지 확인

### 포트 오류
Railway/Render는 자동으로 PORT 환경 변수를 설정합니다.
코드에서 `process.env.PORT || 3000` 사용 확인

---

## 보안 주의사항

⚠️ **API 키 보안**
- `.env` 파일은 Git에 커밋되지 않습니다 (`.gitignore` 확인)
- 환경 변수로만 API 키 설정
- 공개 저장소에 API 키 노출 금지

---

## 비용

- **Railway**: 월 $5 무료 크레딧
- **Render**: 750시간 무료 (sleep 모드 있음)
- **Vercel**: 취미 프로젝트 무료
- **localtunnel**: 완전 무료 (테스트용)

---

**가장 추천: Railway** ⭐
- 설정이 가장 간단
- 자동 배포
- 빠른 속도
- Sleep 모드 없음
