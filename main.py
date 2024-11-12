import json
import time
from bs4 import BeautifulSoup
import html2text
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QTextEdit, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Signal, QThread
import sys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import platform

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

def verify_node_registration(max_retries=10, delay=5):
    """
    Verify that the node is properly registered with the hub.
    """
    import urllib.request
    import json
    import time

    hub_url = 'http://127.0.0.1:4444/grid/api/hub'
    
    for i in range(max_retries):
        try:
            response = urllib.request.urlopen(hub_url)
            data = json.loads(response.read())
            print(f"Hub status: {data}")
            if data.get('success', False):
                print("Hub is ready and running")
                return True
        except Exception as e:
            print(f"Attempt {i+1}: Hub not ready yet... ({str(e)})")
        time.sleep(delay)
    return False

def download_selenium_server_jar(url, dest_path):
    """
    Download the Selenium Server JAR file from the specified URL to the destination path.
    """
    import urllib.request

    print(f"Downloading Selenium Server JAR from {url} to {dest_path}...")
    urllib.request.urlretrieve(url, dest_path)
    print("Download complete.")

def setup_selenium_grid():
    """
    Set up Selenium Grid using Java in standalone mode.
    """
    import subprocess
    import time
    import os

    # Kill any process using port 4444
    kill_port(4444)
    time.sleep(2)

    binaries_path = os.path.join(os.path.dirname(__file__), 'binaries')
    selenium_server_jar = os.path.join(binaries_path, 'selenium-server.jar')

    if not os.path.exists(selenium_server_jar):
        selenium_server_url = "https://selenium-release.storage.googleapis.com/3.141/selenium-server-standalone-3.141.59.jar"
        download_selenium_server_jar(selenium_server_url, selenium_server_jar)

    # Verify Java is installed
    try:
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
        print(f"Java version: {java_version.decode()}")
    except Exception as e:
        raise RuntimeError(f"Java is not installed or not in PATH: {str(e)}")

    # Use Selenium Manager to get the ChromeDriver path
    chromedriver_path = ChromeDriverManager().install()

    # Start the Selenium Grid in standalone mode
    print("Starting Selenium Grid in standalone mode...")
    grid_process = subprocess.Popen([
        "java",
        f"-Dwebdriver.chrome.driver={chromedriver_path}",
        "-jar", selenium_server_jar,
        "-port", "4444",
        "-host", "127.0.0.1"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(5)

    # Check if grid process is still running
    if grid_process.poll() is not None:
        out, err = grid_process.communicate()
        raise RuntimeError(f"Grid failed to start. Output: {out.decode()}\nError: {err.decode()}")

    # Verify grid is running
    if not verify_node_registration():
        grid_process.terminate()
        raise Exception("Failed to verify Selenium Grid is running")

    selenium_server_url = "http://127.0.0.1:4444"
    print(f"Selenium Grid setup complete and running at {selenium_server_url}")
    return grid_process, None

# Call the setup function before starting the application and store the processes
hub_process, node_process = setup_selenium_grid()

def url_to_markdown(url, remote_webdriver_url):
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize remote WebDriver with increased timeouts
        driver = webdriver.Remote(
            command_executor=remote_webdriver_url,
            options=chrome_options
        )
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(30)
        
        try:
            # Load the page with Cloudflare bypass support
            driver.get(url)
            
            # Wait for Cloudflare challenge to complete (if any)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                # Additional wait if Cloudflare challenge is detected
                if "challenge" in driver.page_source.lower():
                    time.sleep(10)  # Wait for challenge completion
            except Exception:
                pass  # Continue if timeout
            
            # Rest of the existing code...
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
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
            
        finally:
            driver.quit()
            
    except Exception as e:
        error_msg = f"Conversion failed: {str(e)}"
        print(error_msg)
        return None, None

class ConvertThread(QThread):
    finished = Signal(str, str)  # Signal now includes title
    error = Signal(str)
    
    def __init__(self, url, remote_webdriver_url):
        super().__init__()
        self.url = url
        self.remote_webdriver_url = remote_webdriver_url
        
    def run(self):
        try:
            result, title = url_to_markdown(self.url, self.remote_webdriver_url)
            if result:
                self.finished.emit(result, title)
            else:
                self.error.emit("Conversion failed")
        except Exception as e:
            self.error.emit(str(e))

class MarkdownViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("URL to Markdown Converter")
        self.setMinimumSize(800, 600)
        self.convert_thread = None
        self.remote_webdriver_url = "http://127.0.0.1:4444/wd/hub"  # Update with your Selenium Grid URL
        
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
        button_layout.addWidget(self.copy_button)
        
        # Save button
        self.save_button = QPushButton("Save Markdown")
        self.save_button.clicked.connect(self.save_markdown)
        self.save_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Store current markdown and title
        self.current_markdown = None
        self.current_title = None

        # Status bar
        self.statusBar().showMessage("Ready")

    def convert_url(self):
        if not self.url_input.text():
            return
            
        # Disable input while processing
        self.url_input.setEnabled(False)
        self.convert_button.setEnabled(False)
        
        # Show processing indicator
        self.statusBar().showMessage("Converting...")
        
        # Start conversion in thread
        self.convert_thread = ConvertThread(self.url_input.text(), self.remote_webdriver_url)
        self.convert_thread.finished.connect(self.on_conversion_complete)
        self.convert_thread.error.connect(self.on_conversion_error)
        self.convert_thread.start()
    
    def on_conversion_complete(self, result, title):
        self.current_markdown = result
        self.current_title = title
        self.text_area.setText(result)
        self.statusBar().clearMessage()
        self.url_input.setEnabled(True)
        self.convert_button.setEnabled(True)
        self.save_button.setEnabled(True)
        
    def on_conversion_error(self, error):
        QMessageBox.warning(self, "Error", f"Conversion failed: {error}")
        self.statusBar().clearMessage()
        self.url_input.setEnabled(True)
        self.convert_button.setEnabled(True)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_area.toPlainText())
        
    def save_markdown(self):
        if self.current_markdown and self.current_title:
            try:
                output_file = f"{self.current_title}.md"
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(self.current_markdown)
                self.statusBar().showMessage(f"Saved to {output_file}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {e}")

def main():
    app = QApplication(sys.argv)
    viewer = MarkdownViewer()
    viewer.show()
    try:
        sys.exit(app.exec())
    finally:
        # Cleanup Selenium Grid processes
        if hub_process:
            hub_process.terminate()
        if node_process:
            node_process.terminate()

if __name__ == "__main__":
    main()
