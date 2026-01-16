# ⚡ 5분 안에 외부 호스팅하기

가장 빠른 방법으로 외부에서 접속 가능한 공개 URL을 생성합니다.

---

## 🚀 Railway 배포 (가장 추천)

### 1. Railway 계정 만들기
👉 https://railway.app (GitHub 로그인)

### 2. 새 프로젝트 만들기
1. "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. 저장소: `vlending/claude`
4. 브랜치: `claude/idol-chatbot-prototype-mbnWY`

### 3. 환경 변수 설정
Variables 탭에서:
```
ANTHROPIC_API_KEY = (실제 API 키 입력)
PORT = 3000
```

### 4. 완료!
- 자동으로 빌드 시작
- 5-10분 후 공개 URL 생성
- Settings에서 "Generate Domain" 클릭해서 공개 도메인 받기

**예시 URL:** `https://idol-chatbot-production.up.railway.app`

---

## 💡 로컬에서 빠른 테스트 (임시)

공개 URL 즉시 생성 (임시 URL, 테스트용):

```bash
# 1. 서버 실행
npm run idol:web

# 2. 새 터미널에서 터널 시작
./start-tunnel.sh
```

또는 수동으로:
```bash
npx localtunnel --port 3000
```

**주의:** 이 URL은 임시이며 서버 재시작 시 변경됩니다.

---

## 📱 접속 확인

배포 완료 후:
1. ✅ 공개 URL 접속
2. ✅ "대화 시작하기" 클릭
3. ✅ 아이돌과 대화 테스트
4. ✅ 모바일에서도 접속 테스트

---

## 🔗 더 자세한 가이드

`DEPLOYMENT.md` 파일 참조:
- Render 배포
- Vercel 배포
- 트러블슈팅
- 비용 정보

---

## ⚡ 지금 바로 시작!

**가장 빠른 방법:**
1. Railway.app 접속 (1분)
2. GitHub 저장소 연결 (2분)
3. 환경 변수 설정 (1분)
4. 자동 배포 대기 (5분)

**총 소요 시간: 약 10분**

---

**Railway 무료 티어:** 월 $5 크레딧 (취미 프로젝트 충분)
