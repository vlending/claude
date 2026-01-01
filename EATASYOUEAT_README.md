# 먹은대로 (Eat-As-You-Eat) Health Meal Coach 🍽️

**개인 맞춤 식단 코칭 앱 - 건강검진 수치 기반 식사 전후 가이드**

> 검진표를 넣으면, 매 끼니 식전엔 "먹으면 안 되는지/대체 메뉴"를 경고성으로 알려주고,
> 식후엔 자동으로 칼로리·영양·기록까지 끝내주는 개인 맞춤 식단 코치

---

## 📱 프로젝트 개요

### 핵심 가치

- **개인화**: 건강검진 수치 기반 맞춤 판정 (체중/혈압/콜레스테롤/혈당/위장)
- **예방적**: 식사 전에 경고 (먹지 말라고 명확히)
- **편리함**: 사진 1장으로 자동 분석 및 기록
- **동기부여**: 게임화 요소 (스트릭, 배지, 목표별 점수)

### 주요 기능

#### 1️⃣ 건강검진 기반 개인화
- 검진표 업로드 → OCR 자동 파싱
- 혈압/혈당/지질/간기능 등 수치 자동 추출
- 개인별 리스크 프로필 생성

#### 2️⃣ 식사 전 코칭 (Pre-Meal)
- 사진 업로드 → AI 분석 (3초 내)
- **RED/YELLOW/GREEN 판정**
- 먹으면 안 되는 이유 (검진 수치와 연결)
- 피해 최소화 팁 (양/조리법/소스)
- 대체 메뉴 3개 추천

#### 3️⃣ 식사 후 자동 기록 (Post-Meal)
- 사진 1장 → 영양 성분 자동 추정
- 칼로리, 탄단지, 당, 나트륨 계산
- 하루 누적 자동 업데이트
- 다음 끼니 가이드 제공

#### 4️⃣ 게임화 & 리포트
- **스트릭**: 연속 기록 일수 (3/7/14/30일 배지)
- **목표별 점수**: 체중/혈압/지질/혈당/위장 독립 점수 (0~100)
- **주간 리포트**: TOP3 문제점 + 잘한 습관 + 다음 주 미션
- **푸시 알림**: 일일 요약 (21시)

---

## 🏗️ 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 + SQLAlchemy + Alembic
- **Cache**: Redis
- **Storage**: AWS S3 (or MinIO for local dev)
- **AI/ML**: Anthropic Claude 3.5 Sonnet
- **OCR**: Tesseract + GPT-4 Vision

### Frontend
- **Framework**: React Native (Expo)
- **Language**: TypeScript
- **Navigation**: React Navigation
- **State**: React Hooks + Async Storage
- **Charts**: React Native Chart Kit

### Infrastructure
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Cloud**: AWS (ECS, RDS, S3, ElastiCache)

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Anthropic API Key

### 1. Clone Repository
```bash
git clone <repository-url>
cd claude
```

### 2. Start Services
```bash
# Start backend + database + redis + minio
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Start Mobile App
```bash
cd mobile
npm install
npm start

# Press 'a' for Android, 'i' for iOS, 'w' for web
```

### 4. Test API
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/v1/docs
```

**📖 자세한 개발 가이드**: [DEVELOPMENT.md](./DEVELOPMENT.md)

---

## 📁 Project Structure

```
claude/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   └── routes/     # Auth, Meals, Reports, etc.
│   │   ├── core/           # Configuration
│   │   ├── db/             # Database connection
│   │   ├── ml/             # AI/ML logic (Claude API)
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── services/       # Business logic
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   └── requirements.txt
│
├── mobile/                  # React Native Mobile App (Expo)
│   ├── App.tsx             # Main entry point
│   ├── screens/            # Screen components
│   ├── components/         # Reusable UI components
│   ├── services/           # API client
│   └── package.json
│
├── docs/                    # Design Documents
│   ├── PRD_먹은대로_MVP.md        # Product Requirements
│   ├── DB_Schema.sql               # Database schema
│   ├── API_Spec.yaml               # OpenAPI specification
│   ├── Prompts.md                  # AI prompt templates
│   └── Sprint_Backlog.md           # Development backlog
│
├── docker-compose.yml       # Local dev environment
├── DEVELOPMENT.md           # Developer guide
└── README.md
```

---

## 📊 Key Features Deep Dive

### Health Risk Classification

건강검진 수치를 3단계로 자동 분류:

| 목표 | Normal | Borderline | High |
|-----|--------|-----------|------|
| 혈압 | <120/80 | 120-139/80-89 | ≥140/90 |
| 공복혈당 | <100 | 100-125 | ≥126 |
| LDL | <130 | 130-159 | ≥160 |
| BMI | 18.5-22.9 | 23-24.9 | ≥25 |

### Decision Logic (RED/YELLOW/GREEN)

**RED (절대 비추)**:
- 나트륨 >800mg (고혈압 시 >400mg)
- 포화지방 >10g (고지혈증 시 >5g)
- 당 >20g (당뇨 시 >10g)
- 알레르기 식품 포함
- 야식 (역류성 식도염 + 21시 이후)

**YELLOW (주의)**:
- RED 기준의 70~100%
- 영양 불균형 (채소 부족 등)

**GREEN (OK)**:
- 모든 기준 통과

### AI Prompt Architecture

1. **System Prompt**: 경고성 톤, 개인화 우선, 근거 명시
2. **Pre-Meal Prompt**: 이미지 → 판정 + 이유 + 대안 (JSON)
3. **Post-Meal Prompt**: 이미지 → 영양 성분 (JSON)
4. **Weekly Report Prompt**: 7일 데이터 → TOP3 분석 + 미션

**Confidence Level**:
- 0.9~1.0: Very High (표준 메뉴)
- 0.7~0.9: High (일반 음식)
- 0.5~0.7: Medium (복잡한 요리)
- <0.5: Low (사용자 확인 필요)

---

## 🧪 Testing

### Backend API
```bash
cd backend

# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Format code
black app/
isort app/
```

### Mobile App
```bash
cd mobile

# Run tests
npm test

# Lint
npm run lint

# Format
npm run format
```

### End-to-End Testing
```bash
# 1. Start backend
docker-compose up -d

# 2. Run E2E tests
cd backend
pytest tests/e2e/

# 3. Manual testing
# - 회원가입 → 건강검진 업로드 → 식사 전 분석 → 식사 후 기록
```

---

## 🗓️ Development Roadmap

### Sprint 0 (Week 1) - Infrastructure ✅
- [x] Project structure
- [x] Docker Compose setup
- [x] FastAPI + PostgreSQL + Redis
- [x] React Native (Expo) initialization
- [x] Hello World API

### Sprint 1 (Weeks 2-3) - Onboarding & Health Check
- [ ] User authentication (JWT)
- [ ] Health check OCR (Tesseract + Claude Vision)
- [ ] Risk profile calculation
- [ ] Onboarding screens

### Sprint 2 (Weeks 4-5) - Meal Coaching
- [ ] Pre-meal analysis API
- [ ] Post-meal logging API
- [ ] AI prompt integration (Claude 3.5 Sonnet)
- [ ] Daily summary

### Sprint 3 (Weeks 6-7) - Gamification & Reports
- [ ] Streak & badges system
- [ ] Goal-based scoring (5 goals)
- [ ] Weekly report generation
- [ ] Push notifications

### Sprint 4 (Weeks 8-9) - QA & Polish
- [ ] 100 food images testing (accuracy >85%)
- [ ] E2E testing
- [ ] Security audit
- [ ] Beta testing (20 users)

---

## 🎯 Success Metrics

### User Engagement
- DAU/MAU > 40%
- Average streak ≥ 7 days
- Pre-meal upload rate > 60%

### Health Impact (User Survey at 4 weeks)
- "Improved" response > 70%
- "Avoiding RED foods" increase > 50%

### Technical Performance
- Image recognition accuracy > 85%
- Nutrition estimation error ± 15%
- API response time < 500ms (P95)
- AI analysis time < 3 seconds

---

## 📚 Documentation

- **[PRD](./docs/PRD_먹은대로_MVP.md)**: Complete product requirements
- **[Database Schema](./docs/DB_Schema.sql)**: PostgreSQL schema
- **[API Spec](./docs/API_Spec.yaml)**: OpenAPI 3.0 specification
- **[AI Prompts](./docs/Prompts.md)**: Prompt templates & logic
- **[Sprint Backlog](./docs/Sprint_Backlog.md)**: Development plan
- **[Development Guide](./DEVELOPMENT.md)**: Developer setup guide

---

## 🔐 Security & Privacy

- **Data Encryption**: AES-256 for health data at rest
- **Transport Security**: TLS 1.3 for all API calls
- **Authentication**: JWT with refresh tokens
- **GDPR/HIPAA Compliance**: Anonymization options
- **Disclaimer**: "식단 가이드이며 의료 진단/치료를 대체하지 않습니다"

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/sprint-X-name`
2. Make changes and commit: `git commit -m "Add feature"`
3. Push to remote: `git push origin feature/sprint-X-name`
4. Create Pull Request

### Code Style
- Backend: Black + isort + mypy
- Frontend: Prettier + ESLint
- Commit messages: Conventional Commits format

---

## 📧 Contact

- **Issues**: GitHub Issues
- **Email**: dev@eatasyoueat.com (TBD)

---

## 📄 License

MIT License

---

**Made with ❤️ for better health**
