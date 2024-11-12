
import html2text
from bs4 import BeautifulSoup
from ..interfaces.converter import IConverter

class HTMLConverter(IConverter):
    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        
    def convert_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        self._clean_content(soup)
        main_content = self._extract_main_content(soup)
        return self.converter.handle(str(main_content))
    
    def _clean_content(self, soup: BeautifulSoup) -> None:
        unwanted_tags = ['nav', 'footer', 'header', 'breadcrumb', 'aside']
        common_classes = [
            'navigation', 'nav', 'footer', 'menu', 'sidebar', 'breadcrumb',
            'author', 'bio', 'profile', 'social', 'share', 'sharing', 'social-media',
            'social-links', 'author-info', 'about-author', 'twitter', 'facebook',
            'linkedin', 'social-buttons', 'author-bio', 'author-box', 'author-details',
            'related-posts', 'post-block-list', 'post-block', 'post-blocks', 'post-blocks-list',
            'header-social-networks', 'header-social', 'header-social-links', 'header-social-icons',
            'entry-meta', 'single-more-articles'
        ]
        common_ids = [
            'author', 'social', 'share', 'profile', 'bio',
            'author-box', 'social-media', 'sharing-buttons'
        ]
        
        # Remove unwanted elements
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
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        return soup.find('main') or soup.find('article') or \
               soup.find('div', class_='content') or soup.find('body')