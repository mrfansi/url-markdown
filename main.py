import re
import sys
import os
import atexit
import asyncio
import anyio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from contextlib import asynccontextmanager
from src.services.web_scraper import WebScraper
from src.services.html_converter import HTMLConverter
from src.services.file_storage import FileStorage
from src.ui.main_window import MarkdownViewer

def slugify(text):
    """
    Convert text to a slug format.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove non-alphanumeric characters
    text = re.sub(r'\s+', '-', text).strip('-')  # Replace spaces with dashes
    return text

@asynccontextmanager
async def setup_services():
    scraper = WebScraper()
    converter = HTMLConverter()
    storage = FileStorage()
    try:
        yield scraper, converter, storage
    finally:
        # Cleanup
        await scraper.close()

async def run_app(app: QApplication):
    async with setup_services() as (scraper, converter, storage):
        viewer = MarkdownViewer(scraper, converter, storage)
        viewer.show()
        
        while not viewer.isHidden():
            app.processEvents()
            await asyncio.sleep(0.01)

def main():
    # Suppress OpenType support warnings
    os.environ["QT_LOGGING_RULES"] = "qt.fonts.warning=false"
    
    app = QApplication(sys.argv)
    anyio.run(lambda: run_app(app), backend="asyncio")

@atexit.register
def cleanup():
    # Ensure resources are properly released
    for window in QApplication.topLevelWindows():
        window.close()

if __name__ == "__main__":
    main()
