import marko
from bs4 import BeautifulSoup
from ..interfaces.converter import IConverter
from ..config import CONTENT_SELECTORS, CLEANING_SELECTORS
import threading
from .logger import LoggerService

class HTMLConverter(IConverter):
    def __init__(self):
        self._local = threading.local()
        self.logger = LoggerService()
    
    @property
    def converter(self):
        if not hasattr(self._local, 'converter'):
            self._local.converter = marko.Markdown()
        return self._local.converter
        
    def convert_to_markdown(self, html_content: str) -> str:
        self.logger.info("Starting HTML to Markdown conversion")
        soup = BeautifulSoup(html_content, 'html.parser')
        self._clean_content(soup)
        main_content = self._extract_main_content(soup)
        markdown = self.converter.convert(str(main_content))
        self.logger.info("HTML to Markdown conversion completed")
        return markdown
    
    def _clean_content(self, soup: BeautifulSoup) -> None:
        self.logger.debug("Cleaning HTML content")
        
        # Remove data-testid attributes
        for element in soup.find_all(attrs={"data-testid": True}):
            del element["data-testid"]
            
        # Remove copy buttons and toolbar elements
        for element in soup.find_all(["button", "div"], class_=CLEANING_SELECTORS['common_classes']):
            element.decompose()
            
        # Remove style attributes
        for element in soup.find_all(style=True):
            del element["style"]
            
        # Remove unwanted elements
        for tag in CLEANING_SELECTORS['unwanted_tags']:
            for element in soup.find_all(tag):
                element.decompose()
                
        # Remove elements by class names
        for class_name in CLEANING_SELECTORS['common_classes']:
            for element in soup.find_all(class_=lambda x: x and class_name in x.lower()):
                element.decompose()
                
        # Remove elements by IDs
        for id_name in CLEANING_SELECTORS['common_ids']:
            for element in soup.find_all(id=lambda x: x and id_name in x.lower()):
                element.decompose()
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        self.logger.debug("Extracting main content")
        
        # First try readme.com specific article class
        main_content = soup.find(class_="rm-Article")
        if main_content:
            # Get only the content section
            content_section = main_content.find(class_="content-body")
            if content_section:
                return content_section
                
        # Fallback to other content selectors
        # Try to find element with matching ID
        for content_id in CONTENT_SELECTORS['ids']:
            main_content = soup.find(id=lambda x: x and content_id in x.lower())
            if main_content:
                return main_content
                
        # Try to find element with matching class
        for content_class in CONTENT_SELECTORS['classes']:
            main_content = soup.find(class_=content_class)
            if main_content:
                return main_content
                
        return soup.find('body')  # Fallback to body if no content is found