from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.projects import router as projects_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.health import router as health_router
from app.api.v1.reports import router as reports_router
from app.api.v1.settings import router as settings_router
from app.api.v1.ai import router as ai_router
from app.api.v1.static_analysis import router as static_analysis_router

v1_router = APIRouter()
v1_router.include_router(health_router)
v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(projects_router)
v1_router.include_router(reviews_router)
v1_router.include_router(reports_router)
v1_router.include_router(settings_router)
v1_router.include_router(ai_router)
v1_router.include_router(static_analysis_router)
