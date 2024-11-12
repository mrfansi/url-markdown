
from ..interfaces.storage import IStorage

class FileStorage(IStorage):
    def save(self, content: str, filepath: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception:
            return False