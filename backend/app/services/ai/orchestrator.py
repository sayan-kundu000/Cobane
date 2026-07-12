import asyncio
import json
import random
import time
from typing import List, Any, Optional
from app.services.ai.config import ai_config
from app.services.ai.models import AIReviewResult, AIFinding
from app.services.ai.providers import BaseAIProvider, OpenAICompatibleProvider
from app.services.ai.prompts import PromptManager
from app.services.ai.context import ContextBuilder
from app.services.ai.token_manager import estimate_tokens, chunk_code
from app.services.ai.metrics import ai_metrics
from app.core.exceptions import ValidationException
from app.core.logging import ai_logger


class AIReviewOrchestrator:
    """Core review engine orchestrator piping context, managing tokens, handling retries, and validating JSON models."""

    def __init__(self, provider: Optional[BaseAIProvider] = None):
        # Allow passing mock or custom provider, otherwise instantiate standard
        is_mock_key = (
            not ai_config.api_key or "mock" in ai_config.api_key.lower() or ai_config.api_key == "openai-api-key"
        )
        if provider:
            self.provider = provider
        elif ai_config.provider == "openai" and not is_mock_key:
            self.provider = OpenAICompatibleProvider()
        else:
            # Fallback mock/dev provider
            from app.services.ai.providers import MockAIProvider

            # Standard seed mock response conforming to JSON schema
            mock_res = {
                "summary": "AI code review run completed successfully.",
                "findings": [
                    {
                        "category": "naming",
                        "severity": "warning",
                        "summary": "Use descriptive variable names",
                        "explanation": "Variables named x or y do not convey semantic naming meanings.",
                        "recommendation": "x = 42 -> total_count = 42",
                        "confidence": 0.9,
                        "file_reference": "stub.py",
                        "function_reference": "run",
                        "line_reference": 10,
                    }
                ],
            }
            self.provider = MockAIProvider(response_content=json.dumps(mock_res))

    @staticmethod
    def _clean_json_response(text: str) -> str:
        """Cleans markdown JSON block markers from LLM output strings."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    async def _execute_request_with_backoff(self, system_prompt: str, user_prompt: str) -> str:
        """Invokes provider generate action wrapped in exponential backoff retries."""
        max_retries = ai_config.retry_count
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                start_time = time.perf_counter()
                content = await self.provider.generate(system_prompt, user_prompt)
                duration = time.perf_counter() - start_time

                # Check JSON validity of content to trigger retry early if malformed
                cleaned = self._clean_json_response(content)
                json.loads(cleaned)

                # Request succeeded and parsed successfully
                ai_metrics.record_success(duration)
                return content

            except Exception as e:
                ai_metrics.record_retry()
                if attempt == max_retries - 1:
                    ai_metrics.record_failure()
                    ai_logger.error("AI provider execution failed after %d retries. Error: %s", max_retries, str(e))
                    raise ValidationException("AI code review generation service is currently unavailable.") from e

                delay = base_delay * (2**attempt) + random.uniform(0.0, 0.5)
                ai_logger.warning(
                    "AI review attempt %d failed. Retrying in %.2f seconds. Error: %s", attempt + 1, delay, str(e)
                )
                await asyncio.sleep(delay)

        raise ValidationException("AI code review execution failed.")

    async def conduct_review(
        self, filename: str, language: str, code_content: str, findings: List[Any], metrics: Any
    ) -> AIReviewResult:
        """Coordinates prompt compilation, code chunking, completions calling, and validation schemas parsing."""

        # 1. Estimate tokens and chunk code if it exceeds thresholds
        # Using 3000 max tokens per chunk to fit context + prompts comfortably inside 4096 bounds
        code_chunks = chunk_code(code_content, max_tokens_per_chunk=3000, model_name=ai_config.model_name)

        # 2. Build diagnostics static analysis context
        static_context = ContextBuilder.build_full_context(findings, metrics)

        chunk_results: List[AIReviewResult] = []

        # 3. Process each chunk
        for index, chunk in enumerate(code_chunks):
            # Track request details
            system_prompt = PromptManager.get_system_prompt()
            user_prompt = PromptManager.get_user_prompt(
                filename=f"{filename} (Part {index + 1}/{len(code_chunks)})" if len(code_chunks) > 1 else filename,
                language=language,
                code_content=chunk,
                static_context=static_context,
            )

            estimated_prompt_tokens = estimate_tokens(system_prompt + user_prompt, ai_config.model_name)
            ai_metrics.record_request(estimated_prompt_tokens)

            # Request completion content with backoff
            raw_response = await self._execute_request_with_backoff(system_prompt, user_prompt)

            # Parse and Validate response
            try:
                cleaned_response = self._clean_json_response(raw_response)
                parsed_json = json.loads(cleaned_response)
                validated_result = AIReviewResult.model_validate(parsed_json)
                chunk_results.append(validated_result)
            except Exception as e:
                ai_logger.error("Failed to parse validated JSON from model response: %s", str(e))
                # Note: clean_json_response error triggers retry inside backoff,
                # but if we get here, it means we exhausted retries and JSON was still malformed.
                raise ValidationException("Failed validating AI structured review outcomes schema.") from e

        # 4. Aggregate results from multiple chunks if needed
        if len(chunk_results) == 1:
            return chunk_results[0]

        # Combine multiple results
        all_findings = []
        summaries = []
        for i, res in enumerate(chunk_results):
            all_findings.extend(res.findings)
            summaries.append(f"Chunk {i+1}: {res.summary}")

        aggregated_summary = "Multi-part code review analysis findings:\n" + "\n".join(summaries)
        return AIReviewResult(summary=aggregated_summary, findings=all_findings)
