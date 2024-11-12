
from abc import ABC, abstractmethod
from typing import Tuple

class IScraper(ABC):
    @abstractmethod
    async def fetch_content(self, url: str) -> Tuple[str, str]:
        """Returns tuple of (content, title)"""
        pass