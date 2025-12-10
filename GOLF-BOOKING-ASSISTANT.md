# AI 골프 부킹 어시스턴트 🏌️

수도권 골프장 예약 성공 확률을 극적으로 올려주는 AI 기반 웹 애플리케이션

## 🎯 핵심 가치 제안

**자동 예약 (X)** → 불법
**예약 성공 확률을 극적으로 올려주는 서비스 (O)** → 합법

## 📋 주요 기능

### 1. 개인 맞춤 티타임 추천 🎯
- 거주지 기반 접근성 분석
- 선호 골프장, 시간대, 플레이 스타일
- 스코어 수준별 코스 난이도 매칭
- 예산 기반 필터링

### 2. 오픈 시간 자동 모니터링 ⏰
- 골프장별 오픈 시간 추적
- 오픈 5분 전 알림
- 자동 브라우저 오픈 (예약 페이지로 이동)
- **클릭은 사용자가 직접** → 법적 문제 없음

### 3. 취소 티타임 실시간 발견 🔔
- 실시간 모니터링 시스템
- 취소 티타임 즉시 푸시 알림
- 속도 경쟁력 = 핵심 차별점
- 유료 회원 우선 알림

### 4. 예약 성공 확률 AI 📊
- 시간대별 성공 확률 분석
- 대체 골프장 추천
- 요일별 예약 난이도 예측
- 과거 데이터 기반 학습

### 5. 구독 모델 💳
- **무료 티어**: 기본 알림, 일일 추천
- **프리미엄 티어** (월 9,900원):
  - 초고속 취소 티타임 알림 (실시간)
  - 성공률 예측 AI
  - 무제한 개인 맞춤 추천
  - 자동 브라우저 오픈
  - 다중 골프장 동시 모니터링

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (Next.js)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ 사용자    │  │ 티타임   │  │ 알림 센터        │  │
│  │ 프로필    │  │ 추천     │  │                  │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              Backend API (Next.js API)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ User API │  │ Golf API │  │ Monitoring API   │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────┐  ┌──────────────────┐
│ PostgreSQL   │  │  Redis   │  │ Anthropic Claude │
│ (Main DB)    │  │ (Cache)  │  │     (AI)         │
└──────────────┘  └──────────┘  └──────────────────┘
        ▲                ▲
        │                │
        └────────────────┘
   ┌──────────────────────┐
   │  Background Workers  │
   │  - 골프장 모니터링    │
   │  - 취소 티타임 감지   │
   │  - 푸시 알림 발송     │
   └──────────────────────┘
```

## 🗂️ 프로젝트 구조

```
golf-booking-assistant/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (dashboard)/
│   │   │   ├── profile/
│   │   │   ├── recommendations/
│   │   │   ├── alerts/
│   │   │   └── subscription/
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   ├── users/
│   │   │   ├── golf-courses/
│   │   │   ├── recommendations/
│   │   │   ├── monitoring/
│   │   │   └── predictions/
│   │   └── layout.tsx
│   ├── components/               # React Components
│   │   ├── ui/                   # Shadcn/ui components
│   │   ├── forms/
│   │   ├── dashboard/
│   │   └── alerts/
│   ├── lib/
│   │   ├── db/                   # Prisma client
│   │   ├── redis/                # Redis client
│   │   ├── ai/                   # Claude AI integration
│   │   ├── monitoring/           # Golf course monitoring
│   │   ├── notifications/        # Push notifications
│   │   └── utils/
│   ├── types/
│   └── workers/                  # Background jobs
│       ├── monitor-courses.ts
│       ├── detect-cancellations.ts
│       └── send-notifications.ts
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── public/
├── .env.example
├── next.config.js
├── tailwind.config.js
└── package.json
```

## 📊 데이터베이스 스키마

### Users (사용자)
```prisma
model User {
  id              String   @id @default(cuid())
  email           String   @unique
  name            String
  phone           String?

  // 프로필 정보
  address         String?      // 거주지
  latitude        Float?
  longitude       Float?

  // 골프 정보
  averageScore    Int?         // 평균 스코어
  skillLevel      SkillLevel?  // BEGINNER, INTERMEDIATE, ADVANCED

  // 선호 정보
  preferredDays   String[]     // ["MON", "SAT", "SUN"]
  preferredTimes  String[]     // ["MORNING", "AFTERNOON"]
  budgetMin       Int?
  budgetMax       Int?

  // 구독
  subscriptionTier SubscriptionTier @default(FREE)
  subscriptionEnd  DateTime?

  // 알림 설정
  notificationsEnabled Boolean @default(true)
  pushToken            String?

  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  // Relations
  favorites       FavoriteGolfCourse[]
  alerts          Alert[]
  predictions     BookingPrediction[]
}
```

### GolfCourses (골프장)
```prisma
model GolfCourse {
  id              String   @id @default(cuid())
  name            String
  region          String   // "경기북부", "경기남부", "인천" 등
  city            String
  address         String
  latitude        Float
  longitude       Float

  // 코스 정보
  holes           Int      // 18, 27, 36
  par             Int
  difficulty      Int      // 1-5

  // 가격 정보
  weekdayPrice    Int
  weekendPrice    Int

  // 예약 정보
  bookingUrl      String
  bookingOpenTime String   // "07:00"
  bookingOpenDays Int      // 예약 오픈 일수 (예: 7일 전)

  // 평가
  rating          Float?
  reviewCount     Int      @default(0)

  // 시설
  facilities      String[] // ["캐디", "카트", "연습장"]

  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  // Relations
  availableSlots  TeeTimeSlot[]
  favorites       FavoriteGolfCourse[]
  alerts          Alert[]
}
```

### TeeTimeSlots (티타임)
```prisma
model TeeTimeSlot {
  id              String   @id @default(cuid())
  golfCourseId    String
  golfCourse      GolfCourse @relation(fields: [golfCourseId], references: [id])

  date            DateTime
  time            String   // "08:00"
  price           Int

  status          SlotStatus // AVAILABLE, BOOKED, CANCELLED
  lastChecked     DateTime

  // 취소 티타임 추적
  wasCancelled    Boolean  @default(false)
  cancelledAt     DateTime?

  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  @@index([golfCourseId, date, status])
}
```

### Alerts (알림)
```prisma
model Alert {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation(fields: [userId], references: [id])

  type            AlertType // OPENING_SOON, CANCELLATION, RECOMMENDATION

  golfCourseId    String?
  golfCourse      GolfCourse? @relation(fields: [golfCourseId], references: [id])

  title           String
  message         String
  actionUrl       String?

  isRead          Boolean  @default(false)
  sentAt          DateTime @default(now())

  @@index([userId, isRead])
}
```

### BookingPredictions (예약 예측)
```prisma
model BookingPrediction {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation(fields: [userId], references: [id])

  targetDate      DateTime
  targetTime      String

  // AI 예측
  successRate     Float    // 0.0 - 1.0
  recommendedTime String   // "07:00" (대기 시작 추천 시간)
  alternatives    Json     // 대체 골프장 추천

  factors         Json     // 예측 근거

  createdAt       DateTime @default(now())
}
```

## 🚀 MVP 개발 로드맵

### Phase 1: 기반 구조 (1-2주)
- [x] Next.js 프로젝트 셋업
- [ ] 데이터베이스 스키마 설계 및 마이그레이션
- [ ] 사용자 인증 (NextAuth.js)
- [ ] 기본 UI 컴포넌트 (Shadcn/ui)

### Phase 2: 골프장 데이터 (1-2주)
- [ ] 수도권 골프장 데이터 수집
- [ ] 골프장 정보 관리 시스템
- [ ] 지도 기반 검색 (위치 기반)
- [ ] 골프장 상세 페이지

### Phase 3: AI 추천 시스템 (2주)
- [ ] Claude API 통합
- [ ] 사용자 프로필 기반 추천 알고리즘
- [ ] 거리, 가격, 난이도 가중치 계산
- [ ] 추천 결과 UI

### Phase 4: 모니터링 시스템 (2주)
- [ ] 골프장 웹사이트 크롤러 (Puppeteer)
- [ ] Redis 기반 실시간 모니터링
- [ ] 취소 티타임 감지 로직
- [ ] Background worker 구현

### Phase 5: 알림 시스템 (1주)
- [ ] Web Push 알림 구현
- [ ] 알림 센터 UI
- [ ] 알림 설정 관리
- [ ] 자동 브라우저 오픈 기능

### Phase 6: 예측 AI (2주)
- [ ] 과거 예약 데이터 수집
- [ ] 성공률 예측 모델
- [ ] 대체 골프장 추천 로직
- [ ] 예측 결과 시각화

### Phase 7: 구독 & 결제 (1주)
- [ ] 구독 플랜 관리
- [ ] 결제 연동 (토스페이먼츠)
- [ ] 프리미엄 기능 제한
- [ ] 결제 내역 관리

## 🎨 주요 화면

1. **랜딩 페이지**: 서비스 소개, 주요 기능
2. **회원가입/로그인**: 이메일/소셜 로그인
3. **프로필 설정**: 거주지, 선호 정보, 스코어
4. **대시보드**: 오늘의 추천, 알림, 모니터링 상태
5. **티타임 추천**: AI 기반 맞춤 추천 리스트
6. **알림 센터**: 실시간 알림 모아보기
7. **구독 관리**: 플랜 선택, 결제

## 🔒 법적 고려사항

### ✅ 합법적인 기능
- 공개된 골프장 정보 수집
- 사용자 맞춤 추천
- 예약 오픈 시간 알림
- 취소 티타임 알림
- 브라우저 자동 오픈 (예약 페이지로 이동)

### ❌ 불법 기능 (절대 구현 금지)
- 자동 예약 클릭
- 매크로 프로그램
- 예약 시스템 우회
- 서버 과부하 유발

### 📋 준수 사항
- 각 골프장의 robots.txt 준수
- 합리적인 크롤링 간격 (최소 10초)
- User-Agent 명시
- 이용약관 명시: "사용자가 직접 예약해야 함"

## 📈 수익 모델

### 무료 티어
- 기본 티타임 추천 (일 3회)
- 오픈 시간 알림 (1개 골프장)
- 취소 티타임 알림 (30분 지연)

### 프리미엄 티어 (월 9,900원)
- 무제한 AI 추천
- 다중 골프장 모니터링 (최대 5개)
- 실시간 취소 티타임 알림
- 예약 성공 확률 AI
- 자동 브라우저 오픈
- 우선 알림 (일반 회원보다 빠름)

### 예상 KPI
- MAU (월간 활성 사용자): 1,000명
- 유료 전환율: 10%
- 월 매출: 990,000원

## 🛠️ 기술 스택 상세

### Frontend
- **Framework**: Next.js 14 (App Router, Server Components)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn/ui (Radix UI)
- **State Management**: React Query, Zustand
- **Forms**: React Hook Form + Zod
- **Maps**: Kakao Maps API

### Backend
- **API**: Next.js API Routes
- **Database**: PostgreSQL (Supabase or Railway)
- **ORM**: Prisma
- **Cache**: Redis (Upstash)
- **Background Jobs**: BullMQ or Inngest
- **File Storage**: S3 or Cloudflare R2

### AI & ML
- **LLM**: Anthropic Claude 3.5 Sonnet
- **Vector DB**: Pinecone (선택사항)
- **Analytics**: 자체 구현 (PostgreSQL)

### DevOps
- **Hosting**: Vercel
- **Database**: Supabase
- **Cache**: Upstash Redis
- **Monitoring**: Sentry
- **Analytics**: Vercel Analytics

### External APIs
- **Maps**: Kakao Maps
- **Payment**: 토스페이먼츠
- **Push Notifications**: OneSignal or Firebase
- **SMS**: SENS (네이버 클라우드)

## 📝 다음 단계

1. **환경 설정**
   - Next.js 프로젝트 생성
   - Prisma + PostgreSQL 연결
   - 기본 UI 컴포넌트 셋업

2. **골프장 데이터 수집**
   - 수도권 주요 골프장 리스트 (50-100개)
   - 골프장 정보 크롤링/API 수집
   - 데이터베이스에 시드 데이터 입력

3. **MVP 기능 구현**
   - 사용자 프로필
   - 티타임 추천 AI
   - 취소 티타임 알림

시작할까요? 🚀
