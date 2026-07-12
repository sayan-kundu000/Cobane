from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.core.responses import StandardJSONResponse
from app.models.user import User

router = APIRouter(prefix="/static-analysis", tags=["static-analysis-configurations"])


@router.get("/config", response_class=StandardJSONResponse)
async def get_static_analysis_config(current_user: User = Depends(get_current_user)):
    """Retrieves enabled rules and configuration options for pylint, bandit, and radon checkers."""
    return {
        "checkers": {
            "pylint": {
                "enabled": True,
                "disabled_warnings": ["missing-docstring", "invalid-name"],
                "max_line_length": 120,
            },
            "bandit": {"enabled": True, "confidence_level": "medium", "severity_level": "medium"},
            "radon": {"enabled": True, "min_maintainability_index": "B", "max_cyclomatic_complexity": 10},
        }
    }
