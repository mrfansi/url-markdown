
from abc import ABC, abstractmethod

class IConverter(ABC):
    @abstractmethod
    def convert_to_markdown(self, html_content: str) -> str:
        pass