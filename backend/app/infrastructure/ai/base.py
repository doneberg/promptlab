from abc import ABC, abstractmethod
from typing import List, Dict


class AIProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        pass