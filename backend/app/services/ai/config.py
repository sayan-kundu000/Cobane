import os
from app.core.config import settings

class AIConfig:
    """Config manager reading AI integration settings from Core configuration and environment."""
    
    def __init__(self):
        self.provider: str = os.getenv("AI_PROVIDER", settings.AI_PROVIDER)
        self.api_key: str = os.getenv("AI_API_KEY", settings.AI_API_KEY)
        self.base_url: str = os.getenv("AI_BASE_URL", settings.AI_BASE_URL)
        
        # Dedicated model parameters with robust defaults
        self.model_name: str = os.getenv("AI_MODEL_NAME", os.getenv("AI_MODEL", "gpt-4o"))
        self.temperature: float = float(os.getenv("AI_TEMPERATURE", "0.2"))
        self.max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "2048"))
        self.timeout_seconds: float = float(os.getenv("AI_TIMEOUT_SECONDS", "30.0"))
        self.retry_count: int = int(os.getenv("AI_RETRY_COUNT", "3"))

ai_config = AIConfig()
