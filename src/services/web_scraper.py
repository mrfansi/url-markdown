import random
from pyppeteer import launch
from ..interfaces.scraper import IScraper
from typing import Tuple
from .user_agent import UserAgentService
from .logger import LoggerService

class WebScraper(IScraper):
    def __init__(self):
        self.logger = LoggerService()

    def _get_random_user_agent(self) -> str:
        ua_service = UserAgentService()
        ua = ua_service.get_user_agent()
        return ua if ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    async def fetch_content(self, url: str) -> Tuple[str, str]:
        self.logger.info(f"Starting to fetch content from: {url}")
        browser = await launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        )
        
        try:
            page = await browser.newPage()
            
            user_agent = self._get_random_user_agent()
            self.logger.debug(f"Using user agent: {user_agent}")
            await page.setUserAgent(user_agent)
            
            # Enable JavaScript
            await page.setJavaScriptEnabled(True)
            
            # Navigate to URL with timeout
            response = await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 30000})
            
            # Wait extra time if needed for dynamic content
            await page.waitForSelector('body', {'timeout': 10000})
            
            content = await page.content()
            title = await page.title()
            
            self.logger.info(f"Successfully fetched content from: {url}")
            return content, title
            
        except Exception as e:
            self.logger.error(f"Error fetching content: {str(e)}")
            raise
        finally:
            await browser.close()