import httpx
from typing import List, Dict
from .base import AIProvider


class OllamaProvider(AIProvider):

    async def generate(
        self,
        messages: List[Dict[str, str]],
    ) -> str:

        prompt = "\n".join([m["content"] for m in messages])

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False,
                },
            )

        data = response.json()
        return data["response"]