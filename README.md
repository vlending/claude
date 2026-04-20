# 블렌딩 Slack Q&A 봇 🤖

주식회사 블렌딩의 사내 사규, 신입사원 입사 매뉴얼 등을 기반으로 직원들의 질문에 자동으로 답변하는 Slack 봇입니다.

## 주요 기능

- 📚 **회사 문서 기반 답변**: 사내 사규, 입사 매뉴얼 등의 문서를 학습하여 정확한 답변 제공
- 🤖 **Claude AI 활용**: Anthropic의 Claude API를 사용한 자연스러운 대화
- 💬 **다양한 상호작용 방식**:
  - 봇 멘션 (@bot)
  - DM (Direct Message)
  - 슬래시 커맨드 (/handbook)
- 🇰🇷 **한국어 지원**: 한국어로 질문하고 답변 받기
- ⚡ **실시간 응답**: Socket Mode를 통한 빠른 응답

## 설치 및 실행

### 1. 필수 요구사항

- Node.js 18 이상
- npm 또는 yarn
- Slack 워크스페이스 관리자 권한
- Anthropic API 키

### 2. 프로젝트 설정

```bash
# 저장소 클론
git clone <repository-url>
cd claude

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 실제 값으로 수정
```

### 3. Slack 앱 설정

#### 3.1 Slack 앱 생성

1. [Slack API](https://api.slack.com/apps)에 접속
2. "Create New App" 클릭
3. "From scratch" 선택
4. 앱 이름 입력 (예: "블렌딩 Q&A 봇")
5. 워크스페이스 선택

#### 3.2 Socket Mode 활성화

1. 좌측 메뉴에서 "Socket Mode" 선택
2. "Enable Socket Mode" 토글 켜기
3. App Token 생성 (이름: "blending-qa-bot")
4. 생성된 토큰을 `.env` 파일의 `SLACK_APP_TOKEN`에 저장

#### 3.3 Bot Token Scopes 설정

1. 좌측 메뉴에서 "OAuth & Permissions" 선택
2. "Bot Token Scopes"에 다음 권한 추가:
   - `app_mentions:read` - 멘션 읽기
   - `chat:write` - 메시지 쓰기
   - `im:history` - DM 읽기
   - `im:read` - DM 접근
   - `im:write` - DM 쓰기
   - `commands` - 슬래시 커맨드

#### 3.4 이벤트 구독 설정

1. 좌측 메뉴에서 "Event Subscriptions" 선택
2. "Enable Events" 토글 켜기
3. "Subscribe to bot events"에 다음 이벤트 추가:
   - `app_mention` - 봇 멘션
   - `message.im` - DM 메시지

#### 3.5 슬래시 커맨드 추가 (선택사항)

1. 좌측 메뉴에서 "Slash Commands" 선택
2. "Create New Command" 클릭
3. 커맨드 정보 입력:
   - Command: `/handbook`
   - Short Description: "회사 사규 및 매뉴얼 검색"
   - Usage Hint: "[질문]"

#### 3.6 앱 설치

1. 좌측 메뉴에서 "Install App" 선택
2. "Install to Workspace" 클릭
3. 권한 승인
4. 생성된 "Bot User OAuth Token"을 `.env` 파일의 `SLACK_BOT_TOKEN`에 저장

### 4. Anthropic API 키 발급

1. [Anthropic Console](https://console.anthropic.com/)에 접속
2. API Keys 메뉴에서 새 키 생성
3. 생성된 키를 `.env` 파일의 `ANTHROPIC_API_KEY`에 저장

### 5. 봇 실행

```bash
# TypeScript 컴파일
npm run build

# 봇 실행
npm start

# 또는 개발 모드로 실행
npm run dev
```

성공적으로 실행되면 다음과 같은 메시지가 표시됩니다:

```
⚡️ Blending Q&A Bot is running!
📚 Loaded 2 documents
🤖 Bot is ready to answer questions!
```

## 사용 방법

### 1. 봇 멘션

채널에서 봇을 멘션하여 질문:

```
@블렌딩Q&A봇 연차는 몇 일인가요?
```

### 2. DM (Direct Message)

봇에게 직접 메시지를 보내서 질문:

```
재택근무 신청은 어떻게 하나요?
```

### 3. 슬래시 커맨드

```
/handbook 점심 식대는 얼마나 지원되나요?
```

## 예시 질문

- "연차는 몇 일인가요?"
- "재택근무 신청은 어떻게 하나요?"
- "점심 식대는 얼마나 지원되나요?"
- "교육비 지원 한도는?"
- "유연근무제가 가능한가요?"
- "첫 출근 때 준비물은?"
- "회의실 예약은 어떻게 하나요?"
- "장기 근속 포상은?"
- "경조사 휴가는 며칠인가요?"

## 문서 관리

### 문서 추가하기

`docs/` 폴더에 Markdown 파일(.md)을 추가하면 자동으로 봇이 학습합니다:

```
docs/
├── company-handbook.md      # 사내 사규
├── onboarding-guide.md      # 신입사원 매뉴얼
├── ogq-blending-karpathy-llm-wiki.md  # LLM Wiki 운영 가이드
└── new-document.md          # 새로운 문서 추가
```

### 문서 작성 가이드

1. **명확한 제목 사용**: 각 문서는 `# 제목` 형식으로 시작
2. **구조화된 내용**: Markdown 헤딩을 사용하여 섹션 구분
3. **구체적인 정보**: 숫자, 날짜, 연락처 등 구체적인 정보 포함
4. **일관된 형식**: 유사한 정보는 동일한 형식으로 작성

### 문서 업데이트

문서를 수정한 후 봇을 재시작하면 변경사항이 반영됩니다:

```bash
npm run build
npm start
```

## 프로젝트 구조

```
claude/
├── src/
│   ├── index.ts              # 메인 진입점 및 Slack 이벤트 핸들러
│   ├── claudeClient.ts       # Claude API 클라이언트
│   └── documentLoader.ts     # 문서 로더
├── docs/
│   ├── company-handbook.md   # 사내 사규
│   └── onboarding-guide.md   # 신입사원 매뉴얼
├── dist/                     # 컴파일된 JavaScript 파일
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

## 기술 스택

- **언어**: TypeScript
- **런타임**: Node.js
- **Slack SDK**: @slack/bolt (Socket Mode)
- **AI**: Anthropic Claude 3.5 Sonnet
- **기타**: dotenv, fs

## 주요 기능 설명

### Document Loader

`src/documentLoader.ts`는 `docs/` 폴더의 Markdown 파일을 읽어 메모리에 로드합니다.

- 파일 자동 탐색 및 로드
- 제목 추출
- 문서 검색 기능
- 컨텍스트 생성

### Claude Client

`src/claudeClient.ts`는 Anthropic Claude API와 통신하여 답변을 생성합니다.

- 문서 컨텍스트를 포함한 프롬프트 생성
- Claude 3.5 Sonnet 모델 사용
- 한국어 친절한 답변 생성
- 에러 핸들링

### Slack Bot

`src/index.ts`는 Slack 이벤트를 처리하고 사용자와 상호작용합니다.

- 앱 멘션 처리
- DM 메시지 처리
- 슬래시 커맨드 처리
- 로딩 상태 표시

## 커스터마이징

### 답변 스타일 변경

`src/claudeClient.ts`의 시스템 프롬프트를 수정하여 답변 스타일을 변경할 수 있습니다:

```typescript
system: `당신은 주식회사 블렌딩의 사내 Q&A 챗봇입니다.
// 여기에서 답변 가이드라인 수정
...`
```

### Claude 모델 변경

더 빠른 응답이 필요하면 모델을 변경할 수 있습니다:

```typescript
model: 'claude-3-haiku-20240307',  // 더 빠르고 저렴
// 또는
model: 'claude-3-5-sonnet-20241022',  // 더 정확하고 상세
```

### 추가 Slack 이벤트 처리

`src/index.ts`에 새로운 이벤트 핸들러를 추가할 수 있습니다:

```typescript
app.event('reaction_added', async ({ event }) => {
  // 리액션 이벤트 처리
});
```

## 트러블슈팅

### 봇이 응답하지 않아요

1. `.env` 파일의 토큰이 올바른지 확인
2. Slack 앱의 Socket Mode가 활성화되어 있는지 확인
3. 봇이 채널에 초대되어 있는지 확인
4. 콘솔 로그에서 에러 메시지 확인

### "Missing required environment variables" 에러

`.env` 파일에 다음 변수가 모두 설정되어 있는지 확인:

- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `ANTHROPIC_API_KEY`

### Claude API 에러

1. API 키가 유효한지 확인
2. API 사용량 한도를 확인
3. 네트워크 연결 상태 확인

### 문서가 로드되지 않아요

1. `docs/` 폴더가 존재하는지 확인
2. 파일 확장자가 `.md`인지 확인
3. 파일 인코딩이 UTF-8인지 확인

## 보안 고려사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키는 안전하게 관리하세요
- 프로덕션 환경에서는 환경 변수를 서버 설정에서 관리하세요
- 회사 기밀 정보는 문서에 포함하지 마세요

## 향후 개선 사항

- [ ] 벡터 데이터베이스 연동 (Pinecone, Weaviate 등)
- [ ] 더 정교한 문서 검색 (semantic search)
- [ ] 사용자 피드백 수집 (👍👎 리액션)
- [ ] 대화 히스토리 저장
- [ ] 다국어 지원 (영어, 일본어 등)
- [ ] 관리자 대시보드
- [ ] 질문 통계 및 분석

## 라이센스

MIT License

## 문의

문제가 발생하거나 제안 사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ by Blending**
