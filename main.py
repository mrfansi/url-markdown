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

async def url_to_markdown(url):
    try:
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        await page.goto(url, {'waitUntil': 'networkidle2'})
        
        # Wait for Cloudflare challenge to complete (if any)
        if "challenge" in await page.content():
            await asyncio.sleep(10)  # Wait for challenge completion
        
        # Get page content
        page_content = await page.content()
        await browser.close()
        
        # Process the page content
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Remove navigation, footer, and other unwanted elements
        unwanted_tags = ['nav', 'footer', 'header', 'breadcrumb', 'aside']
        
        # Remove elements with common unwanted class names
        common_classes = [
            'navigation', 'nav', 'footer', 'menu', 'sidebar', 'breadcrumb', 'breadcrumbs',
            'author', 'bio', 'profile', 'social', 'share', 'sharing', 'social-media',
            'social-links', 'author-info', 'about-author', 'twitter', 'facebook',
            'linkedin', 'social-buttons', 'author-bio', 'author-box', 'author-details',
            'related-posts', 'post-block-list', 'post-block', 'post-blocks', 'post-blocks-list',
            'header-social-networks', 'header-social', 'header-social-links', 'header-social-icons',
            'entry-meta', 'single-more-articles'
        ]
        
        # Remove elements with common unwanted IDs
        common_ids = [
            'author', 'social', 'share', 'profile', 'bio',
            'author-box', 'social-media', 'sharing-buttons'
        ]
        
        # Remove unwanted elements by tags
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements by class names
        for class_name in common_classes:
            for element in soup.find_all(class_=lambda x: x and class_name in x.lower()):
                element.decompose()
                
        # Remove elements by IDs
        for id_name in common_ids:
            for element in soup.find_all(id=lambda x: x and id_name in x.lower()):
                element.decompose()
                
        # Also remove schema.org author metadata
        for element in soup.find_all(itemprop=['author', 'creator']):
            element.decompose()
        
        # Extract the title for the filename
        title = soup.title.string if soup.title else "output"
        slugified_title = slugify(title)
        
        # Find the main content (prefer main content areas)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.find('body')
        
        # Convert HTML to Markdown
        converter = html2text.HTML2Text()
        converter.ignore_links = False  # Set to True to ignore hyperlinks
        markdown_text = converter.handle(str(main_content))
        
        # Return the markdown text and title
        return markdown_text, slugified_title
        
    except Exception as e:
        error_msg = f"Conversion failed: {str(e)}"
        print(error_msg)
        return None, None

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
