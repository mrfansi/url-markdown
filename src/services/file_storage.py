from ..interfaces.storage import IStorage
import threading
from .logger import LoggerService

class FileStorage(IStorage):
    def __init__(self):
        self._lock = threading.Lock()
        self.logger = LoggerService()
        
    def save(self, content: str, filepath: str) -> bool:
        self.logger.info(f"Attempting to save content to: {filepath}")
        with self._lock:
            try:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.logger.info(f"Successfully saved content to: {filepath}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to save content: {str(e)}")
                return False