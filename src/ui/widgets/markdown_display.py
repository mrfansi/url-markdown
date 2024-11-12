from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from .markdown_highlighter import MarkdownHighlighter

class MarkdownDisplayWidget(QWidget):
    """Widget for displaying converted markdown content."""

    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        markdown_label = QLabel("Markdown Preview:")
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        # Add custom styling
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        # Initialize syntax highlighter
        self.highlighter = MarkdownHighlighter(self.text_edit.document())
        
        layout.addWidget(markdown_label)
        layout.addWidget(self.text_edit)

    def set_content(self, content: str, title: str) -> None:
        self.title = title
        self.text_edit.setText(content)

    def get_content(self) -> str:
        return self.text_edit.toPlainText()

    def get_title(self) -> str:
        return self.title