
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Markdown text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_formats()

    def _init_formats(self):
        # Headers
        self.h1_format = self._create_format(20, True)
        self.h2_format = self._create_format(16, True)
        self.h3_format = self._create_format(14, True)
        
        # Other formats
        self.bold_format = self._create_format(weight=True)
        self.italic_format = self._create_format(italic=True)
        self.code_format = self._create_format(family="Courier")
        self.link_format = self._create_format(color=QColor("#0366d6"))
        
    def _create_format(self, size=None, weight=False, italic=False, 
                      color=None, family=None):
        text_format = QTextCharFormat()
        if size:
            text_format.setFontPointSize(size)
        if weight:
            text_format.setFontWeight(QFont.Bold)
        if italic:
            text_format.setFontItalic(True)
        if color:
            text_format.setForeground(color)
        if family:
            text_format.setFontFamily(family)
        return text_format

    def highlightBlock(self, text):
        # Headers
        if text.startswith('# '):
            self.setFormat(0, len(text), self.h1_format)
        elif text.startswith('## '):
            self.setFormat(0, len(text), self.h2_format)
        elif text.startswith('### '):
            self.setFormat(0, len(text), self.h3_format)
            
        # Bold
        self._highlight_pattern(text, r'\*\*(.+?)\*\*', self.bold_format)
        self._highlight_pattern(text, r'__(.+?)__', self.bold_format)
        
        # Italic
        self._highlight_pattern(text, r'\*(.+?)\*', self.italic_format)
        self._highlight_pattern(text, r'_(.+?)_', self.italic_format)
        
        # Code
        self._highlight_pattern(text, r'`(.+?)`', self.code_format)
        
        # Links
        self._highlight_pattern(text, r'\[(.+?)\]\(.+?\)', self.link_format)

    def _highlight_pattern(self, text, pattern, text_format):
        import re
        for match in re.finditer(pattern, text):
            start, end = match.span()
            self.setFormat(start, end - start, text_format)