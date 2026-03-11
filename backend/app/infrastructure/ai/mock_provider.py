import asyncio
from typing import List, Dict
from .base import AIProvider


class MockAIProvider(AIProvider):
    async def generate(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        await asyncio.sleep(0.5)
        combined = " | ".join([m["content"] for m in messages])
        return f"[MOCK RESPONSE] {combined}"