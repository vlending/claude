# Slack 봇 설정 가이드 📖

이 문서는 블렌딩 Slack Q&A 봇을 처음부터 설정하는 방법을 단계별로 안내합니다.

## 목차

1. [Slack 앱 생성](#1-slack-앱-생성)
2. [Socket Mode 설정](#2-socket-mode-설정)
3. [권한 설정](#3-권한-설정)
4. [이벤트 구독](#4-이벤트-구독)
5. [슬래시 커맨드 추가](#5-슬래시-커맨드-추가)
6. [앱 설치](#6-앱-설치)
7. [환경 변수 설정](#7-환경-변수-설정)
8. [봇 실행](#8-봇-실행)

## 1. Slack 앱 생성

### 1.1 Slack API 웹사이트 접속

1. 브라우저에서 https://api.slack.com/apps 접속
2. Slack 워크스페이스 계정으로 로그인

### 1.2 새 앱 만들기

1. **"Create New App"** 버튼 클릭
2. **"From scratch"** 선택
3. 다음 정보 입력:
   - **App Name**: `블렌딩 Q&A 봇` (또는 원하는 이름)
   - **Pick a workspace**: 봇을 설치할 워크스페이스 선택
4. **"Create App"** 클릭

## 2. Socket Mode 설정

Socket Mode를 사용하면 공개 URL 없이도 Slack 이벤트를 실시간으로 받을 수 있습니다.

### 2.1 Socket Mode 활성화

1. 좌측 사이드바에서 **"Socket Mode"** 클릭
2. **"Enable Socket Mode"** 토글을 **ON**으로 변경
3. Token 이름 입력: `blending-qa-bot-token`
4. **"Generate"** 클릭
5. 생성된 토큰 복사 (나중에 사용할 예정)
   - 형식: `xapp-1-...`
   - ⚠️ 이 토큰은 한 번만 표시되므로 안전한 곳에 저장!

## 3. 권한 설정

### 3.1 OAuth & Permissions

1. 좌측 사이드바에서 **"OAuth & Permissions"** 클릭
2. **"Scopes"** 섹션으로 스크롤
3. **"Bot Token Scopes"** 아래 **"Add an OAuth Scope"** 클릭

### 3.2 필요한 권한 추가

다음 권한들을 하나씩 추가합니다:

| Scope | 설명 |
|-------|------|
| `app_mentions:read` | 봇이 멘션된 메시지 읽기 |
| `chat:write` | 메시지 전송 |
| `im:history` | DM 메시지 히스토리 읽기 |
| `im:read` | DM 접근 |
| `im:write` | DM 전송 |
| `commands` | 슬래시 커맨드 사용 |

## 4. 이벤트 구독

### 4.1 Event Subscriptions 활성화

1. 좌측 사이드바에서 **"Event Subscriptions"** 클릭
2. **"Enable Events"** 토글을 **ON**으로 변경

### 4.2 Bot Events 추가

**"Subscribe to bot events"** 섹션에서 **"Add Bot User Event"** 클릭 후 다음 이벤트 추가:

| Event | 설명 |
|-------|------|
| `app_mention` | 봇이 멘션될 때 |
| `message.im` | DM 메시지를 받을 때 |

### 4.3 저장

- 페이지 하단의 **"Save Changes"** 클릭

## 5. 슬래시 커맨드 추가

슬래시 커맨드는 선택사항이지만 추가하면 더 편리하게 사용할 수 있습니다.

### 5.1 새 커맨드 만들기

1. 좌측 사이드바에서 **"Slash Commands"** 클릭
2. **"Create New Command"** 클릭

### 5.2 커맨드 정보 입력

| 필드 | 값 |
|------|-----|
| **Command** | `/handbook` |
| **Short Description** | `회사 사규 및 매뉴얼 검색` |
| **Usage Hint** | `[질문]` |

예시:
```
Command: /handbook
Short Description: 회사 사규 및 매뉴얼 검색
Usage Hint: [질문]
```

3. **"Save"** 클릭

## 6. 앱 설치

### 6.1 워크스페이스에 설치

1. 좌측 사이드바에서 **"Install App"** 클릭
2. **"Install to Workspace"** 버튼 클릭
3. 권한 승인 화면에서 **"허용"** 클릭

### 6.2 Bot Token 복사

설치가 완료되면 **"Bot User OAuth Token"**이 표시됩니다.

- 형식: `xoxb-...`
- 이 토큰을 복사 (나중에 사용할 예정)

## 7. 환경 변수 설정

### 7.1 Anthropic API 키 발급

1. https://console.anthropic.com/ 접속
2. 로그인 또는 회원가입
3. 좌측 메뉴에서 **"API Keys"** 선택
4. **"Create Key"** 클릭
5. 키 이름 입력 (예: `blending-slack-bot`)
6. 생성된 API 키 복사
   - 형식: `sk-ant-...`

### 7.2 .env 파일 생성

프로젝트 루트 디렉토리에서:

```bash
cp .env.example .env
```

### 7.3 .env 파일 편집

`.env` 파일을 열어 다음과 같이 수정:

```env
# Slack 설정
SLACK_BOT_TOKEN=xoxb-여기에-Bot-Token-입력
SLACK_APP_TOKEN=xapp-여기에-App-Token-입력

# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-여기에-API-Key-입력

# 선택 사항
PORT=3000
```

**예시:**
```env
SLACK_BOT_TOKEN=xoxb-YOUR-BOT-TOKEN-HERE
SLACK_APP_TOKEN=xapp-YOUR-APP-TOKEN-HERE
ANTHROPIC_API_KEY=sk-ant-YOUR-API-KEY-HERE
PORT=3000
```

⚠️ **중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!

## 8. 봇 실행

### 8.1 의존성 설치

```bash
npm install
```

### 8.2 TypeScript 컴파일

```bash
npm run build
```

### 8.3 봇 시작

```bash
npm start
```

성공하면 다음과 같은 메시지가 표시됩니다:

```
✅ Loaded 2 documents
⚡️ Blending Q&A Bot is running!
📚 Loaded 2 documents
🤖 Bot is ready to answer questions!
```

## 9. 테스트

### 9.1 Slack에서 봇 찾기

1. Slack 워크스페이스 열기
2. 좌측 사이드바에서 **"앱"** 섹션 찾기
3. **"블렌딩 Q&A 봇"** 찾기

### 9.2 DM으로 테스트

1. 봇을 클릭하여 DM 시작
2. 메시지 입력: `안녕`
3. 봇이 환영 메시지로 응답하는지 확인

### 9.3 채널에서 테스트

1. 봇을 채널에 초대: `/invite @블렌딩Q&A봇`
2. 봇 멘션으로 질문: `@블렌딩Q&A봇 연차는 몇 일인가요?`
3. 봇이 답변하는지 확인

### 9.4 슬래시 커맨드 테스트

1. 채널이나 DM에서 입력: `/handbook 재택근무는 가능한가요?`
2. 봇이 답변하는지 확인

## 문제 해결

### 봇이 응답하지 않아요

**체크리스트:**
- [ ] 봇이 실행 중인가요? (터미널에서 확인)
- [ ] `.env` 파일의 토큰들이 올바른가요?
- [ ] Socket Mode가 활성화되어 있나요?
- [ ] 필요한 권한이 모두 추가되었나요?
- [ ] 이벤트 구독이 활성화되어 있나요?
- [ ] 봇이 채널에 초대되어 있나요?

### "Missing required environment variables" 에러

`.env` 파일에 다음 세 가지가 모두 설정되어 있는지 확인:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `ANTHROPIC_API_KEY`

### Socket Mode 연결 실패

1. `SLACK_APP_TOKEN`이 올바른지 확인
2. Socket Mode가 활성화되어 있는지 확인
3. 방화벽이 WebSocket 연결을 차단하지 않는지 확인

### Claude API 에러

1. `ANTHROPIC_API_KEY`가 올바른지 확인
2. API 사용량 한도를 확인
3. 결제 정보가 등록되어 있는지 확인 (Anthropic Console에서)

## 다음 단계

✅ 설정이 완료되었습니다!

이제 다음을 할 수 있습니다:

1. **문서 추가**: `docs/` 폴더에 새로운 `.md` 파일 추가
2. **답변 스타일 커스터마이징**: `src/claudeClient.ts` 수정
3. **추가 기능 개발**: 새로운 Slack 이벤트 핸들러 추가

더 자세한 정보는 [README.md](README.md)를 참고하세요.

## 참고 자료

- [Slack Bolt SDK 문서](https://slack.dev/bolt-js/)
- [Slack API 문서](https://api.slack.com/)
- [Anthropic API 문서](https://docs.anthropic.com/)
- [Socket Mode 가이드](https://api.slack.com/apis/connections/socket)

---

설정 중 문제가 있으시면 이슈를 등록해주세요!
