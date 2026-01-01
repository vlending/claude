# 먹은대로 개발 가이드

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for mobile development)
- Python 3.11+ (for local backend development)
- Anthropic API Key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd claude
```

### 2. Environment Setup

#### Backend

```bash
cd backend
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

#### Mobile

```bash
cd mobile
npm install
# or
yarn install
```

### 3. Start Services with Docker

```bash
# Start all services (PostgreSQL, Redis, MinIO, Backend API)
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### 4. Initialize Database

The database schema will be automatically initialized when PostgreSQL starts (using `docs/DB_Schema.sql`).

To manually run migrations:

```bash
cd backend
alembic upgrade head
```

### 5. Start Mobile App

```bash
cd mobile
npm start
# or
yarn start

# Press 'a' for Android
# Press 'i' for iOS
# Press 'w' for web
```

## 📁 Project Structure

```
claude/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core config
│   │   ├── db/             # Database
│   │   ├── ml/             # AI/ML logic
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── tests/              # Backend tests
│   ├── alembic/            # DB migrations
│   ├── Dockerfile
│   └── requirements.txt
│
├── mobile/                  # React Native Mobile App
│   ├── App.tsx             # Main app component
│   ├── app.json            # Expo config
│   ├── package.json
│   └── tsconfig.json
│
├── docs/                    # Design Documents
│   ├── PRD_먹은대로_MVP.md
│   ├── DB_Schema.sql
│   ├── API_Spec.yaml
│   ├── Prompts.md
│   └── Sprint_Backlog.md
│
├── docker-compose.yml       # Docker orchestration
└── README.md
```

## 🔧 Development Workflow

### Backend Development

```bash
# Run backend locally (without Docker)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/
```

### Mobile Development

```bash
cd mobile

# Start Expo dev server
npm start

# Run on Android
npm run android

# Run on iOS (macOS only)
npm run ios

# Run tests
npm test

# Format code
npm run format
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history
```

## 🧪 Testing

### Backend API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test ping endpoint
curl http://localhost:8000/v1/ping

# View API docs
open http://localhost:8000/v1/docs
```

### Mobile App Testing

The mobile app includes a connection test to the backend API. When you launch the app, it will automatically check the backend API status.

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Connect to PostgreSQL
docker exec -it eatasyoueat-postgres psql -U postgres -d eatasyoueat
```

### Backend API Not Starting

```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend container
docker-compose build backend
docker-compose up -d backend
```

### Mobile App Can't Connect to API

1. Make sure backend is running: `docker-compose ps`
2. Check backend health: `curl http://localhost:8000/health`
3. For Android emulator, use `http://10.0.2.2:8000` instead of `http://localhost:8000`
4. For iOS simulator, `http://localhost:8000` should work
5. For physical devices, use your computer's IP address

## 📊 Services URLs

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/v1/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MinIO Console**: http://localhost:9001 (user: minioadmin, pass: minioadmin)
- **MinIO API**: http://localhost:9000

## 🔐 Environment Variables

### Backend (.env)

Key variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for AI features)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `S3_ENDPOINT_URL`: MinIO/S3 endpoint

See `backend/.env.example` for full list.

## 📝 Git Workflow

```bash
# Create feature branch
git checkout -b feature/sprint-1-auth

# Make changes and commit
git add .
git commit -m "Add user authentication API"

# Push to remote
git push origin feature/sprint-1-auth

# Create pull request on GitHub
```

## 🚢 Deployment

### Backend Deployment (Production)

1. Set production environment variables
2. Build Docker image: `docker build -t eatasyoueat-backend:v1 ./backend`
3. Push to container registry
4. Deploy to Kubernetes/ECS/Cloud Run

### Mobile App Deployment

```bash
cd mobile

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios

# Submit to app stores
eas submit
```

## 🔍 Monitoring

- **Backend Logs**: `docker-compose logs -f backend`
- **Database Logs**: `docker-compose logs -f postgres`
- **Health Check**: `curl http://localhost:8000/health`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## ❓ FAQ

**Q: How do I reset the database?**
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Recreate with fresh DB
```

**Q: How do I add a new Python dependency?**
```bash
cd backend
pip install <package>
pip freeze > requirements.txt
docker-compose build backend
docker-compose up -d backend
```

**Q: How do I test AI features without API key?**
Use mock responses in development. See `backend/app/ml/mock.py` (to be created in Sprint 1).

---

**Happy Coding! 🎉**
