from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from src.services.logger import LogObserver, LoggerService

class LogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._register_logger()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # layout.setContentsMargins(10, 10, 10, 10)
        # layout.setSpacing(5)

        # Add title label
        title_label = QLabel("Log Output:")
        layout.addWidget(title_label)

        # Add log text area
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        layout.addWidget(self._log_text)

    def _register_logger(self):
        logger = LoggerService()
        logger.add_observer(self)

    def on_log_message(self, level: str, message: str, timestamp: str):
        self._log_text.append(f"[{timestamp}] {level}: {message}")
        self._log_text.verticalScrollBar().setValue(
            self._log_text.verticalScrollBar().maximum()
        )