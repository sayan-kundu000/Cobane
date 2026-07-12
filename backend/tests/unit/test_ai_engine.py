import pytest
import json
import httpx
import os
from app.core.config import settings
from app.services.ai.config import ai_config
from app.services.ai.models import AIFinding, AIReviewResult
from app.services.ai.providers import MockAIProvider
from app.services.ai.prompts import PromptManager
from app.services.ai.context import ContextBuilder
from app.services.ai.token_manager import estimate_tokens, chunk_code
from app.services.ai.metrics import ai_metrics
from app.services.ai.orchestrator import AIReviewOrchestrator
from app.services.ai_service import AIService
from app.core.exceptions import ValidationException

@pytest.mark.anyio
async def test_token_estimation_and_chunking():
    # 1. Test token estimation
    text = "def hello():\n    print('world')"
    tokens = estimate_tokens(text)
    assert tokens > 0
    assert tokens == len(text) // 4

    # 2. Test code chunking
    code_content = "\n".join([f"line_{i} = {i}" for i in range(100)])
    chunks = chunk_code(code_content, max_tokens_per_chunk=30)
    assert len(chunks) > 1
    assert "".join(chunks).replace("\n", "") == code_content.replace("\n", "")

@pytest.mark.anyio
async def test_context_builder_formatting():
    # 1. Test formatting static findings
    class MockFinding:
        provider = "pylint"
        category = "style"
        severity = "warning"
        line_number = 12
        message = "Missing docstring"

    findings = [MockFinding()]
    formatted_analysis = ContextBuilder.format_static_analysis(findings)
    assert "Missing docstring" in formatted_analysis
    assert "Line 12: [WARNING]" in formatted_analysis

    # 2. Test formatting metrics
    class MockMetrics:
        cyclomatic_complexity = 5
        maintainability_index = 85.5
        loc = 50
        functions_count = 3
        classes_count = 1

    formatted_metrics = ContextBuilder.format_metrics(MockMetrics())
    assert "Maintainability Index: 85.50" in formatted_metrics
    assert "Cyclomatic Complexity: 5" in formatted_metrics

@pytest.mark.anyio
async def test_prompt_manager():
    system = PromptManager.get_system_prompt()
    assert "JSON Response Schema" in system
    assert "summary" in system

    user = PromptManager.get_user_prompt("test.py", "python", "x = 1", "Static findings context")
    assert "test.py" in user
    assert "Static findings context" in user
    assert "x = 1" in user

@pytest.mark.anyio
async def test_ai_models_validation():
    finding_data = {
        "category": "performance",
        "severity": "warning",
        "summary": "Avoid global variables",
        "explanation": "Globals consume memory globally.",
        "recommendation": "Use local variables.",
        "confidence": 0.85,
        "file_reference": "main.py",
        "line_reference": 5
    }
    finding = AIFinding(**finding_data)
    assert finding.category == "performance"
    assert finding.severity == "warning"

    finding_data["category"] = "invalid_category"
    with pytest.raises(ValueError):
        AIFinding(**finding_data)

    finding_data["category"] = "bug"
    finding_data["severity"] = "critical_level"
    with pytest.raises(ValueError):
        AIFinding(**finding_data)

@pytest.mark.anyio
async def test_orchestrator_successful_review():
    mock_res = {
        "summary": "Mock review completed successfully.",
        "findings": [
            {
                "category": "bug",
                "severity": "critical",
                "summary": "Infinite loop detected",
                "explanation": "The loop has no break statement.",
                "recommendation": "Add a termination check condition.",
                "confidence": 0.95,
                "file_reference": "app.py",
                "line_reference": 45
            }
        ]
    }
    
    mock_provider = MockAIProvider(response_content=json.dumps(mock_res))
    orchestrator = AIReviewOrchestrator(provider=mock_provider)

    result = await orchestrator.conduct_review(
        filename="app.py",
        language="python",
        code_content="while True: pass",
        findings=[],
        metrics=None
    )

    assert result.summary == "Mock review completed successfully."
    assert len(result.findings) == 1
    assert result.findings[0].category == "bug"
    assert result.findings[0].severity == "critical"
    assert result.findings[0].line_reference == 45

@pytest.mark.anyio
async def test_orchestrator_retry_on_failure():
    ai_metrics.total_retries = 0

    mock_provider = MockAIProvider(raises_error=True)
    orchestrator = AIReviewOrchestrator(provider=mock_provider)

    original_retry_count = ai_config.retry_count
    ai_config.retry_count = 2

    try:
        with pytest.raises(ValidationException):
            await orchestrator.conduct_review(
                filename="fail.py",
                language="python",
                code_content="x = 1",
                findings=[],
                metrics=None
            )
        
        assert ai_metrics.total_retries >= 1
        assert mock_provider.calls_count == 2
        
    finally:
        ai_config.retry_count = original_retry_count

@pytest.mark.anyio
async def test_ai_service_integration():
    mock_res = {
        "summary": "AI Service review completed.",
        "findings": [
            {
                "category": "naming",
                "severity": "info",
                "summary": "Standard variable names style advice",
                "explanation": "CamelCase should not be used for local variables.",
                "recommendation": "myVal = 5 -> my_val = 5",
                "confidence": 0.8,
                "file_reference": "helpers.py",
                "line_reference": 10
            }
        ]
    }
    mock_provider = MockAIProvider(response_content=json.dumps(mock_res))
    
    orchestrator = AIReviewOrchestrator(provider=mock_provider)
    
    ai_service = AIService()
    original_conduct_review = AIReviewOrchestrator.conduct_review
    
    async def mock_conduct_review(*args, **kwargs):
        return AIReviewResult.model_validate(mock_res)
        
    AIReviewOrchestrator.conduct_review = mock_conduct_review
    
    try:
        results = await ai_service.generate_review(
            _code_content="myVal = 5",
            filename="helpers.py",
            language="python"
        )
        
        assert results["provider"] == "openai"
        assert os.getenv("AI_PROVIDER", settings.AI_PROVIDER) == "openai" or results["provider"] is not None
        assert results["summary"] == "AI Service review completed."
        assert len(results["suggestions"]) == 1
        assert results["suggestions"][0]["type"] == "naming"
        assert results["suggestions"][0]["line"] == 10
        assert "myVal = 5" in results["suggestions"][0]["suggestion"]
        
    finally:
        AIReviewOrchestrator.conduct_review = original_conduct_review
