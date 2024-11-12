
from abc import ABC, abstractmethod

class IStorage(ABC):
    @abstractmethod
    def save(self, content: str, filepath: str) -> bool:
        pass