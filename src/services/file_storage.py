from ..interfaces.storage import IStorage
import threading

class FileStorage(IStorage):
    def __init__(self):
        self._lock = threading.Lock()
        
    def save(self, content: str, filepath: str) -> bool:
        with self._lock:
            try:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                return True
            except Exception:
                return False