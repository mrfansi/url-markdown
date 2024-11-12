from pyppeteer import launch
from ..interfaces.scraper import IScraper
from typing import Tuple
import asyncio

class WebScraper(IScraper):
    async def fetch_content(self, url: str) -> Tuple[str, str]:
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
            
            # Set user agent to avoid detection
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Enable JavaScript
            await page.setJavaScriptEnabled(True)
            
            # Navigate to URL with timeout
            response = await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 30000})
            
            # Wait extra time if needed for dynamic content
            await page.waitForSelector('body', {'timeout': 10000})
            
            content = await page.content()
            title = await page.title()
            
            return content, title
            
        finally:
            await browser.close()