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

def slugify(text):
    """
    Convert text to a slug format.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove non-alphanumeric characters
    text = re.sub(r'\s+', '-', text).strip('-')  # Replace spaces with dashes
    return text

def kill_port(port):
    """
    Kill any process using the specified port.
    """
    import subprocess
    import platform

    system = platform.system().lower()
    if system == 'windows':
        subprocess.run(["netstat", "-ano", "|", "findstr", f":{port}", "|", "findstr", "LISTENING", "|", "for", "/F", "\"tokens=5\"", "%i", "in", "('more')", "do", "taskkill", "/F", "/PID", "%i"], shell=True)
    else:
        # Use lsof to find and kill the process using the port
        result = subprocess.run(["lsof", "-t", f"-i:{port}"], capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split()
            for pid in pids:
                subprocess.run(["kill", "-9", pid])

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

class MarkdownViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("URL to Markdown Converter")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # URL input
        url_layout = QVBoxLayout()
        url_label = QLabel("Enter URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.convert_button = QPushButton("Convert to Markdown")
        self.convert_button.setMinimumHeight(40)
        self.convert_button.clicked.connect(self.convert_url)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.convert_button)
        layout.addLayout(url_layout)

        # Markdown display
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Button layout
        button_layout = QVBoxLayout()
        
        # Copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setMinimumHeight(40)
        button_layout.addWidget(self.copy_button)
        
        # Save button
        self.save_button = QPushButton("Save Markdown")
        self.save_button.clicked.connect(self.save_markdown)
        self.save_button.setEnabled(False)  # Initially disabled
        self.save_button.setMinimumHeight(40)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Store current markdown and title
        self.current_markdown = None
        self.current_title = None

        # Status bar
        self.statusBar().showMessage("Ready")

    @asyncSlot()
    async def convert_url(self):
        if not self.url_input.text():
            return
            
        # Disable input while processing
        self.url_input.setEnabled(False)
        self.convert_button.setEnabled(False)
        self.statusBar().showMessage("Converting...")
        
        try:
            result, title = await url_to_markdown(self.url_input.text())
            if result:
                self.current_markdown = result
                self.current_title = title
                self.text_area.setText(result)
                self.save_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "Conversion failed")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Conversion failed: {str(e)}")
        finally:
            self.statusBar().clearMessage()
            self.url_input.setEnabled(True)
            self.convert_button.setEnabled(True)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_area.toPlainText())
        
    def save_markdown(self):
        if self.current_markdown and self.current_title:
            try:
                # Open file dialog to choose save location
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Markdown File",
                    f"{self.current_title}.md",
                    "Markdown Files (*.md);;All Files (*)"
                )
                
                if file_path:  # Only save if user didn't cancel
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(self.current_markdown)
                    self.statusBar().showMessage(f"Saved to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {e}")

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    viewer = MarkdownViewer()
    viewer.show()
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
