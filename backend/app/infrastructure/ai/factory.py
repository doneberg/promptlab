from app.config import settings
from .mock_provider import MockAIProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .base import AIProvider


def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "openai":
        return OpenAIProvider()

    if settings.ai_provider == "ollama":
        return OllamaProvider()

    return MockAIProvider()