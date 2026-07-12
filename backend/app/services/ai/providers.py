import abc
import json
import httpx
from typing import Dict, Any, Optional
from app.services.ai.config import ai_config
from app.core.exceptions import ValidationException
from app.core.logging import ai_logger

class BaseAIProvider(abc.ABC):
    """Abstract interface defining required behaviors for AI LLM engine providers."""
    
    @abc.abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Sends prompts to the AI provider and returns the raw string completion content."""
        pass

class OpenAICompatibleProvider(BaseAIProvider):
    """Provider execution wrapper invoking standard OpenAI-compatible chat completion endpoints."""
    
    def __init__(
        self,
        api_key: str = ai_config.api_key,
        base_url: str = ai_config.base_url,
        model_name: str = ai_config.model_name
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Invokes chat completions API over HTTP return JSON string response."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": ai_config.temperature,
            "max_tokens": ai_config.max_tokens,
            "response_format": {"type": "json_object"}
        }

        ai_logger.info("Dispatching chat completions request to provider model '%s'...", self.model_name)
        
        async with httpx.AsyncClient(timeout=ai_config.timeout_seconds) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                res_data = response.json()
                
                # Extract response text
                choices = res_data.get("choices", [])
                if not choices:
                    raise ValidationException("API responded successfully but choice results list is empty.")
                    
                content = choices[0].get("message", {}).get("content", "")
                if not content:
                    raise ValidationException("API returned empty completion response text content.")
                    
                return content
                
            except httpx.HTTPStatusError as e:
                ai_logger.error("HTTP error response received from AI provider [Status Code: %d]. Details: %s", e.response.status_code, e.response.text)
                raise ValidationException(f"AI provider failed with status code {e.response.status_code}.") from e
            except httpx.RequestError as e:
                ai_logger.error("HTTP connection request failure targeting AI provider: %s", str(e))
                raise ValidationException("Could not connect to the remote AI provider API.") from e

class MockAIProvider(BaseAIProvider):
    """Deterministically returns pre-configured mock response payload strings for unit tests."""
    
    def __init__(self, response_content: str = "", raises_error: bool = False):
        self.response_content = response_content
        self.raises_error = raises_error
        self.calls_count = 0

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls_count += 1
        if self.raises_error:
            ai_logger.warning("Mock provider simulated request connection failure.")
            raise httpx.ConnectError("Simulated connection timeout.")
        return self.response_content
