"""API router configuration."""
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include routers (will be created in Sprint 1)
# from app.api.routes import auth, health_checks, meals, reports, gamification

# For now, add a simple test route
@api_router.get("/ping")
async def ping():
    """Ping endpoint for testing."""
    return {"message": "pong", "status": "ok"}


__all__ = ["api_router"]
