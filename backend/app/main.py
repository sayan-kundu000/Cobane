from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import v1_router
from app.core.config import settings
from app.core.middleware import register_middlewares
from app.core.exceptions import register_exception_handlers
from app.core.logging import app_logger

# Define system startup/shutdown lifecycle hook manager
@asynccontextmanager
async def lifespan(_app: FastAPI):
    app_logger.info("Initializing Cobane API runtime environment...")
    yield
    app_logger.info("Tearing down Cobane API database engines and sockets...")

app = FastAPI(
    title="Cobane API",
    description="AI-Powered Code Review Assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register custom exception handlers
register_exception_handlers(app)

# Register security and timing middlewares
register_middlewares(app)

# Configure CORS origins dynamically using configurations settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount endpoints
app.include_router(v1_router, prefix="/api/v1")
