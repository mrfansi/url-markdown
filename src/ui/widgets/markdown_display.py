from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from typing import Optional

class MarkdownDisplayWidget(QWidget):
    """Widget for displaying and formatting markdown content."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.title: str = ""
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self._setup_header()
        self._setup_editor()
        
    def _setup_header(self) -> None:
        self.header_label = QLabel("Markdown Preview:")
        self.layout().addWidget(self.header_label)
        
    def _setup_editor(self) -> None:
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self._apply_editor_style()
        self.layout().addWidget(self.text_edit)
        
    def _apply_editor_style(self) -> None:
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
            }
        """)

    def set_content(self, content: str, title: str) -> None:
        """
        Set the markdown content and title.
        
        Args:
            content (str): The markdown content to display
            title (str): The title of the content
        """
        self.title = title
        self.text_edit.setText(content)

    def get_content(self) -> str:
        """
        Get the current markdown content.
        
        Returns:
            str: The current markdown text
        """
        return self.text_edit.toPlainText()

    def get_title(self) -> str:
        """
        Get the current content title.
        
        Returns:
            str: The current title
        """
        return self.title