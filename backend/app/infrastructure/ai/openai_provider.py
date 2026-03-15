from openai import AsyncOpenAI
from typing import List, Dict
from app.config import settings
from .base import AIProvider


class OpenAIProvider(AIProvider):

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

    async def generate(
        self,
        messages: List[Dict[str, str]],
    ) -> str:

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content