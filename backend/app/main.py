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
    try:
        from app.core.database import engine, AsyncSessionLocal
        from app.models.base import Base
        from app.db.seed import seed_database

        app_logger.info("Verifying and creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        app_logger.info("Checking database seeding...")
        async with AsyncSessionLocal() as session:
            await seed_database(session)
    except Exception as e:
        app_logger.error(f"Database initialization/seeding failed on startup: {e}")

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

# Configure CORS origins dynamically
allow_origins = settings.ALLOWED_CORS_ORIGINS
allow_all = "*" in allow_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount endpoints
app.include_router(v1_router, prefix="/api/v1")

# Mount frontend static assets if they exist (for single-service deployment)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist"
)
if not os.path.exists(frontend_dist):
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

if os.path.exists(frontend_dist):
    app_logger.info(f"Serving frontend static files from: {frontend_dist}")

    # Mount assets subfolder if it exists
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        # Serve existing files
        file_path = os.path.join(frontend_dist, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fall back to index.html for SPA client routing
        return FileResponse(os.path.join(frontend_dist, "index.html"))
