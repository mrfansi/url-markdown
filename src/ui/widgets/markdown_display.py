from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel

class MarkdownDisplayWidget(QWidget):
    """
    A widget for displaying and formatting markdown content.
    
    This widget provides a read-only text area with markdown syntax highlighting
    and formatted preview capabilities.
    
    Attributes:
        title (str): The title of the current markdown content
        text_edit (QTextEdit): The main text display area
    """

    def __init__(self) -> None:
        """Initialize the markdown display widget."""
        super().__init__()
        self.title = ""
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface components."""
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
        
        layout.addWidget(markdown_label)
        layout.addWidget(self.text_edit)

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