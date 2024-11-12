
from pyppeteer import launch
from ..interfaces.scraper import IScraper
import asyncio

class WebScraper(IScraper):
    async def fetch_content(self, url: str) -> tuple[str, str]:
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        try:
            page = await browser.newPage()
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            await page.goto(url, {'waitUntil': 'networkidle2'})
            
            if "challenge" in await page.content():
                await asyncio.sleep(10)
            
            content = await page.content()
            title = await page.title()
            return content, title
        finally:
            await browser.close()