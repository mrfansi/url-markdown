from typing import Optional, Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class URLInputWidget(QWidget):
    """Widget for URL input and conversion triggering."""

    def __init__(self, 
                 on_convert: Callable[[], None],
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.on_convert = on_convert
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 0)
        layout.setSpacing(8)
        
        self._setup_input_field()
        self._setup_convert_button()
        
    def _setup_input_field(self) -> None:
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self._apply_input_style()
        self.url_input.returnPressed.connect(self.on_convert)
        self.layout().addWidget(QLabel("Enter URL:"))
        self.layout().addWidget(self.url_input)
        
    def _apply_input_style(self) -> None:
        """Apply custom styling to the input field."""
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 4px;
                font-size: 14px;
            }
        """)
        
    def _setup_convert_button(self) -> None:
        self.convert_button = QPushButton("Convert")
        self.convert_button.setMinimumHeight(40)
        self.convert_button.clicked.connect(self.on_convert)
        self.layout().addWidget(self.convert_button)

    def get_url(self) -> str:
        """
        Get the current URL from the input field.
        
        Returns:
            str: The trimmed URL text
        """
        return self.url_input.text().strip()

    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the input components.
        
        Args:
            enabled (bool): True to enable, False to disable
        """
        self.url_input.setEnabled(enabled)
        self.convert_button.setEnabled(enabled)
        self.convert_button.setText("Convert" if enabled else "Converting...")