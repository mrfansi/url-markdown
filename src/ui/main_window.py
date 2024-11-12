from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox, QApplication
from qasync import asyncSlot

from ..interfaces.converter import IConverter
from ..interfaces.scraper import IScraper
from ..interfaces.storage import IStorage
from .widgets.url_input import URLInputWidget
from .widgets.markdown_display import MarkdownDisplayWidget
from .widgets.action_buttons import ActionButtonsWidget


class MarkdownViewer(QMainWindow):
    """Main window for the URL to Markdown converter application."""

    def __init__(self, scraper: IScraper, converter: IConverter, storage: IStorage) -> None:
        super().__init__()
        self.scraper = scraper
        self.converter = converter
        self.storage = storage
        
        self.setWindowTitle("URL to Markdown Converter")
        self.setMinimumSize(800, 600)
        
        self._init_ui()
        
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create widgets
        self.url_widget = URLInputWidget(self.convert_url)
        self.markdown_widget = MarkdownDisplayWidget()
        self.action_buttons = ActionButtonsWidget(
            self.copy_to_clipboard,
            self.save_markdown
        )
        
        # Add widgets to layout
        layout.addWidget(self.url_widget)
        layout.addWidget(self.markdown_widget)
        layout.addWidget(self.action_buttons)
        
        self.statusBar().showMessage("Ready")

    @asyncSlot()
    async def convert_url(self):
        url = self.url_widget.get_url()
        if not url:
            return
            
        self.url_widget.set_enabled(False)
        self.statusBar().showMessage("Fetching content...")
        
        try:
            # Show intermediate status updates
            self.statusBar().showMessage("Downloading page...")
            content, title = await self.scraper.fetch_content(url)
            
            self.statusBar().showMessage("Converting to markdown...")
            markdown = self.converter.convert_to_markdown(content)
            
            self.markdown_widget.set_content(markdown, title)
            self.action_buttons.enable_save()
            self.statusBar().showMessage("Conversion complete", 2000)
        except Exception as e:
            self._show_error(f"Conversion failed: {str(e)}")
        finally:
            self.url_widget.set_enabled(True)

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