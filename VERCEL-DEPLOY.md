# 🚀 Vercel 배포 가이드

Vercel에 아이돌 챗봇을 배포하는 단계별 가이드입니다.

---

## ⚡ 빠른 시작 (5분)

### 1단계: Vercel 계정 생성

1. https://vercel.com 접속
2. "Sign Up" 클릭
3. **GitHub 계정으로 로그인** (추천)

---

### 2단계: 새 프로젝트 Import

1. Vercel 대시보드에서 **"Add New..."** 클릭
2. **"Project"** 선택
3. **"Import Git Repository"** 클릭
4. GitHub 저장소 검색: `vlending/claude`
5. **"Import"** 클릭

---

### 3단계: 프로젝트 설정

#### Build Settings:
```
Framework Preset: Other
Root Directory: ./
Build Command: npm run build
Output Directory: (비워두기)
Install Command: npm install
```

#### Branch 선택:
```
Branch: claude/idol-chatbot-prototype-mbnWY
```

---

### 4단계: 환경 변수 설정 ⚠️ 중요!

**Environment Variables** 섹션에서:

```
Name: ANTHROPIC_API_KEY
Value: your-actual-api-key-here
```

**Environment 선택:**
- ✅ Production
- ✅ Preview
- ✅ Development

모두 체크!

---

### 5단계: 배포!

1. **"Deploy"** 버튼 클릭
2. 빌드 진행 상황 확인 (3-5분)
3. 배포 완료! 🎉

---

## 🌐 배포 완료 후

### 공개 URL 확인

배포가 완료되면 다음과 같은 URL을 받게 됩니다:

```
https://idol-chatbot-[random].vercel.app
```

또는 커스텀 도메인:
```
https://your-custom-domain.com
```

---

## ✅ 테스트하기

1. 공개 URL 접속
2. "대화 시작하기" 버튼 클릭
3. 아이돌과 대화 테스트
4. 모바일에서도 접속 테스트

---

## 🔄 자동 배포

설정 후에는:
- Git에 push할 때마다 **자동 배포**
- 브랜치별 **Preview 배포** 지원
- Production은 main 브랜치 기준

---

## 🛠️ 문제 해결

### 빌드 실패 시

**로그 확인:**
1. Vercel 대시보드에서 프로젝트 클릭
2. "Deployments" 탭
3. 실패한 배포 클릭
4. 빌드 로그 확인

**흔한 원인:**
- ❌ 환경 변수 누락 (ANTHROPIC_API_KEY)
- ❌ 빌드 명령 오류
- ❌ 브랜치 선택 오류

**해결 방법:**
```bash
# 로컬에서 빌드 테스트
npm install
npm run build

# 성공하면 Vercel 설정 확인
```

---

### API 키 오류

**증상:**
- 배포는 성공했지만 채팅이 작동하지 않음
- API 오류 메시지

**해결:**
1. Vercel 프로젝트 → **Settings** → **Environment Variables**
2. `ANTHROPIC_API_KEY` 확인
3. 값이 올바른지 확인
4. Production, Preview, Development 모두 체크되었는지 확인
5. **Redeploy** 클릭

---

### 정적 파일 404 오류

**증상:**
- 웹페이지가 로드되지 않음
- CSS/JS 파일 404

**해결:**
`vercel.json` 파일이 올바르게 설정되었는지 확인

---

## 📊 Vercel 장점

- ✅ **무료 티어**: 취미 프로젝트에 충분
- ✅ **자동 HTTPS**: SSL 인증서 자동 적용
- ✅ **글로벌 CDN**: 전 세계 빠른 접속
- ✅ **자동 배포**: Git push만 하면 배포
- ✅ **Preview 배포**: PR마다 Preview URL 생성
- ✅ **서버리스**: 관리 불필요

---

## 💰 비용

### Free Tier (Hobby):
- ✅ 무제한 프로젝트
- ✅ 무제한 API 요청
- ✅ 100GB 대역폭/월
- ✅ HTTPS + CDN 포함
- ✅ 자동 배포

### 제한사항:
- ⚠️ 함수 실행 시간: 10초 (충분함)
- ⚠️ 함수 메모리: 1024MB (충분함)

**아이돌 챗봇은 Free Tier로 충분합니다!**

---

## 🎯 다음 단계

배포 완료 후:

1. **커스텀 도메인 연결** (선택)
   - Vercel 프로젝트 → Settings → Domains
   - 원하는 도메인 추가

2. **Analytics 확인** (선택)
   - Vercel 대시보드에서 트래픽 확인
   - 실시간 방문자 수 모니터링

3. **환경 변수 추가** (선택)
   - 추가 API 키
   - Feature flags
   - 기타 설정

---

## 📞 도움말

- **Vercel 문서**: https://vercel.com/docs
- **문제 발생 시**: GitHub Issues에 문의
- **커뮤니티**: Vercel Discord

---

## 🔗 빠른 링크

- **Vercel 대시보드**: https://vercel.com/dashboard
- **프로젝트 설정**: https://vercel.com/[username]/[project]/settings
- **배포 로그**: https://vercel.com/[username]/[project]/deployments

---

**배포 소요 시간: 약 5분**

**지금 시작하세요!** 👉 https://vercel.com
