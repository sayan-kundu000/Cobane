from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.core.responses import StandardJSONResponse
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/ai", tags=["ai-capabilities"])

@router.get("/config", response_class=StandardJSONResponse)
async def get_ai_config(current_user: User = Depends(get_current_user)):
    """Retrieves config parameters for registered LLM integration models and providers."""
    return {
        "provider": settings.AI_PROVIDER,
        "base_url": settings.AI_BASE_URL,
        "model_engine": "gpt-4-turbo-preview",
        "temperature": 0.2,
        "max_tokens": 2048
    }

@router.get("/prompts", response_class=StandardJSONResponse)
async def get_active_prompts(current_user: User = Depends(get_current_user)):
    """Lists preconfigured code analysis review prompt templates."""
    return {
        "templates": [
            {
                "name": "security",
                "description": "Scans for credentials leak, insecure code constructs, and SQL injection risks."
            },
            {
                "name": "refactoring",
                "description": "Reviews names, modular formatting, redundant operations, and style conventions."
            },
            {
                "name": "performance",
                "description": "Checks memory footprints, loop structures, and database query pools."
            }
        ]
    }
