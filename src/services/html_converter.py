from markdownify import markdownify
from bs4 import BeautifulSoup
from ..interfaces.converter import IConverter
from ..config import CONTENT_SELECTORS, CLEANING_SELECTORS

class HTMLConverter(IConverter):
    def __init__(self):
        self.md = lambda x: markdownify(x, heading_style="ATX")

    def convert_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        self._clean_content(soup)
        main_content = self._extract_main_content(soup)
        return self.md(str(main_content))

    def _clean_content(self, soup: BeautifulSoup) -> None:
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