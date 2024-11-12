from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt

class URLInputWidget(QWidget):
    """Widget for URL input and conversion trigger."""

    def __init__(self, on_convert: callable) -> None:
        super().__init__()
        self.on_convert = on_convert
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # Add spacing between widgets
        
        url_label = QLabel("Enter URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 4px;
                font-size: 14px;
            }
        """)
        # Add Enter key handler
        self.url_input.returnPressed.connect(self.on_convert)
        
        self.convert_button = QPushButton("Convert")
        self.convert_button.setMinimumHeight(40)
        self.convert_button.clicked.connect(self.on_convert)
        
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.convert_button)

    def get_url(self) -> str:
        return self.url_input.text().strip()

    def set_enabled(self, enabled: bool) -> None:
        self.url_input.setEnabled(enabled)
        self.convert_button.setEnabled(enabled)
        
        # Update button text to show loading state
        if enabled:
            self.convert_button.setText("Convert")
        else:
            self.convert_button.setText("Converting...")