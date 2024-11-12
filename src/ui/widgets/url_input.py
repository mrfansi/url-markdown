from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt

class URLInputWidget(QWidget):
    """
    A widget for URL input and conversion triggering.
    
    This widget provides a URL input field and a convert button,
    with support for Enter key submission.
    
    Attributes:
        url_input (QLineEdit): The URL input field
        convert_button (QPushButton): The conversion trigger button
    """

    def __init__(self, on_convert: callable) -> None:
        """
        Initialize the URL input widget.
        
        Args:
            on_convert (callable): Callback function for conversion trigger
        """
        super().__init__()
        self.on_convert = on_convert
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface components."""
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