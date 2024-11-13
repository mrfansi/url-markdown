import re
from PySide6.QtWidgets import QApplication
import sys
import anyio
from src.services.web_scraper import WebScraper
from src.services.html_converter import HTMLConverter
from src.services.file_storage import FileStorage
from src.ui.main_window import MarkdownViewer
from contextlib import asynccontextmanager
import atexit
import os

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

def main():
    # Suppress OpenType support warnings
    os.environ["QT_LOGGING_RULES"] = "qt.fonts.warning=false"
    
    app = QApplication(sys.argv)
    
    async def run_app():
        async with setup_services() as (scraper, converter, storage):
            viewer = MarkdownViewer(scraper, converter, storage)
            viewer.show()
            
            while not viewer.isHidden():
                app.processEvents()
                await anyio.sleep(0.01)

    anyio.run(run_app)

@atexit.register
def cleanup():
    # Ensure resources are properly released
    for window in QApplication.topLevelWindows():
        window.close()

if __name__ == "__main__":
    main()
