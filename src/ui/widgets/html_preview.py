from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser
from PySide6.QtCore import Qt

class HTMLPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header label
        header = QLabel("HTML Preview")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)
        
        # Text browser for HTML content
        self.text_browser = QTextBrowser()
        self.text_browser.setMinimumHeight(200)
        self.text_browser.setOpenExternalLinks(True)
        layout.addWidget(self.text_browser)
        
        self.clear_content()
        
    def set_content(self, html_content: str):
        """Set the HTML content to display."""
        if html_content:
            self.text_browser.setHtml(html_content)
        else:
            self.clear_content()
            
    def clear_content(self):
        """Clear the HTML preview."""
        self.text_browser.setHtml("<center><p>No content to preview</p></center>")