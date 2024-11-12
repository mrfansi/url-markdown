import time
from bs4 import BeautifulSoup
import html2text
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QTextEdit, QLineEdit, QLabel, QMessageBox,
                              QFileDialog)
from PySide6.QtCore import Signal, QObject
import sys
import asyncio
from pyppeteer import launch
import qasync
from qasync import asyncSlot, QEventLoop
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

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Initialize services
    scraper = WebScraper()
    converter = HTMLConverter()
    storage = FileStorage()
    
    # Create and show main window
    viewer = MarkdownViewer(scraper, converter, storage)
    viewer.show()
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
