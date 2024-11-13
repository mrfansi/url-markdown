from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, QFileDialog,
    QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from qasync import asyncSlot

from ..interfaces.converter import IConverter
from ..interfaces.scraper import IScraper
from ..interfaces.storage import IStorage
from .widgets.url_input import URLInputWidget
from .widgets.markdown_display import MarkdownDisplayWidget
from .widgets.action_buttons import ActionButtonsWidget
from .widgets.logger_widget import LogWidget
from .widgets.html_preview import HTMLPreviewWidget
from ..services.logger import LoggerService


class MarkdownViewer(QMainWindow):
    """Main window for the URL to Markdown converter application."""

    def __init__(self, 
                 scraper: IScraper, 
                 converter: IConverter, 
                 storage: IStorage,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_components(scraper, converter, storage)
        self._init_ui()
        
    def _setup_components(self, scraper: IScraper, converter: IConverter, storage: IStorage) -> None:
        self.scraper = scraper
        self.converter = converter
        self.storage = storage
        self.setWindowTitle("URL to Markdown Converter")
        self.setMinimumSize(800, 600)
        
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create splitter for preview areas (changed to Horizontal)
        preview_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create widgets
        self.url_widget = URLInputWidget(self.convert_url)
        self.markdown_widget = MarkdownDisplayWidget()
        self.html_preview = HTMLPreviewWidget()
        self.action_buttons = ActionButtonsWidget(
            self.copy_to_clipboard,
            self.save_markdown
        )
        self.log_widget = LogWidget()
        
        # Add widgets to preview splitter with equal width
        preview_splitter.addWidget(self.markdown_widget)
        preview_splitter.addWidget(self.html_preview)
        preview_splitter.setSizes([400, 400])  # Set equal initial widths
        
        # Add widgets to content layout
        content_layout.addWidget(self.url_widget)
        content_layout.addWidget(preview_splitter)
        content_layout.addWidget(self.action_buttons)
        content_layout.addWidget(self.log_widget)
        
        # Set splitter proportions (horizontal)
        preview_splitter.setStretchFactor(0, 1)
        preview_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(content_widget)
        self.statusBar().showMessage("Ready")

    @asyncSlot()
    async def convert_url(self) -> None:
        """Convert URL to markdown asynchronously."""
        if not (url := self.url_widget.get_url()):
            return
            
        self._set_ui_state(False)
        try:
            await self._perform_conversion(url)
        except Exception as e:
            self._show_error(f"Conversion failed: {str(e)}")
        finally:
            self._set_ui_state(True)

    async def _perform_conversion(self, url: str) -> None:
        """Perform the actual conversion process."""
        self._update_status("Downloading page...")
        content, title = await self.scraper.fetch_content(url)
        
        # Update HTML preview first
        self.html_preview.set_content(content)
        
        self._update_status("Converting to markdown...")
        markdown = self.converter.convert_to_markdown(content)
        
        self._update_status("Updating display...")
        self.markdown_widget.set_content(markdown, title)
        
        self.action_buttons.enable_save()
        self._update_status("Conversion complete", timeout=2000)

    def _set_ui_state(self, enabled: bool) -> None:
        """Enable or disable UI elements."""
        self.url_widget.set_enabled(enabled)
        self.action_buttons.setEnabled(enabled)
        QApplication.processEvents()

    def _update_status(self, message: str, timeout: int = 0) -> None:
        """Update status bar with message."""
        self.statusBar().showMessage(message, timeout)
        QApplication.processEvents()

    def save_markdown(self):
        content = self.markdown_widget.get_content()
        title = self.markdown_widget.get_title()
        
        if content and title:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Markdown File",
                f"{title}.md",
                "Markdown Files (*.md);;All Files (*)"
            )
            
            if file_path and self.storage.save(content, file_path):
                self.statusBar().showMessage(f"Saved to {file_path}")
            else:
                self._show_error("Failed to save file")

    def copy_to_clipboard(self):
        """Copy markdown content to clipboard."""
        content = self.markdown_widget.get_content()
        if content:
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            self.statusBar().showMessage("Copied to clipboard", 2000)

    def _show_error(self, message: str):
        """Show error message in a dialog."""
        QMessageBox.warning(self, "Error", message)