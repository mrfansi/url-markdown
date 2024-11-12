from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout
from src.services.logger import LogObserver

class LogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        layout.addWidget(self._log_text)

    def on_log_message(self, level: str, message: str, timestamp: str):
        self._log_text.append(f"[{timestamp}] {level}: {message}")
        self._log_text.verticalScrollBar().setValue(
            self._log_text.verticalScrollBar().maximum()
        )