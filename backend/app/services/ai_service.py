# Provider-agnostic AI integration abstraction layer.

from typing import Any, List, Optional
from app.core.config import settings
from app.core.logging import ai_logger

class AIService:
    """Service to handle communication with OpenAI-style LLM API providers."""
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.api_key = settings.AI_API_KEY
        self.base_url = settings.AI_BASE_URL

    async def generate_review(
        self,
        _code_content: str,
        _prompt_template: str = "Standard review template",
        filename: str = "stub.py",
        language: str = "python",
        findings: Optional[List[Any]] = None,
        metrics: Optional[Any] = None
    ) -> dict:
        """Invokes the AI review orchestrator, translating its structured findings to standard suggestions."""
        ai_logger.info("Triggering AI review request using provider: %s", self.provider)

        # Import orchestrator dynamically to prevent circular dependencies
        from app.services.ai.orchestrator import AIReviewOrchestrator
        orchestrator = AIReviewOrchestrator()

        # Execute code review
        result = await orchestrator.conduct_review(
            filename=filename,
            language=language,
            code_content=_code_content,
            findings=findings or [],
            metrics=metrics
        )

        # Translate structured AIReviewResult into the client dictionary expected by review services
        suggestions = []
        for finding in result.findings:
            suggestions.append({
                "type": finding.category,
                "file": finding.file_reference or filename,
                "line": finding.line_reference or 1,
                "comment": finding.explanation,
                "suggestion": finding.recommendation,
                "confidence": finding.confidence,
                "severity": finding.severity
            })

        return {
            "provider": self.provider,
            "summary": result.summary,
            "suggestions": suggestions
        }
