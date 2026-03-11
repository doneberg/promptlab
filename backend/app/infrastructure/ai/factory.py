from .mock_provider import MockAIProvider
from .base import AIProvider


def get_ai_provider() -> AIProvider:
    return MockAIProvider()