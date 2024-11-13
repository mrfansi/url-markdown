import requests
from requests_html import AsyncHTMLSession
import cloudscraper
import anyio
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.async_api import async_playwright
from ..interfaces.scraper import IScraper
from typing import Tuple
from .logger import LoggerService
import multiprocessing
from cachetools import TTLCache, cached
from contextlib import asynccontextmanager

class WebScraper(IScraper):
    def __init__(self):
        self.logger = LoggerService()
        try:
            self.ua = UserAgent(browsers=['chrome', 'edge', 'firefox'])
            self.logger.info("Initialized fake-useragent with browser profiles")
        except Exception as e:
            self.logger.error(f"Failed to initialize fake-useragent: {str(e)}")
            self.ua = None
        self.session = self._create_session()
        self.html_session = AsyncHTMLSession()
        self.cloudscraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.logger.info("WebScraper initialized with concurrent execution capability")
        self.cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour cache
        self.process_pool = multiprocessing.Pool(processes=2)
        self.connection_pool = {
            'http': requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20),
            'https': requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
        }
        
    def _create_session(self):
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self.logger.debug(f"Created session with retry config: {retry.__dict__}")
        return session

    @lru_cache(maxsize=1)
    def _get_random_user_agent(self) -> str:
        try:
            if self.ua:
                agent = self.ua.random
                self.logger.debug(f"Generated random user agent: {agent}")
                return agent
        except Exception as e:
            self.logger.error(f"Error generating user agent: {str(e)}")
        
        # Fallback user agent if fake-useragent fails
        fallback = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.logger.debug(f"Using fallback user agent: {fallback}")
        return fallback

    @asynccontextmanager
    async def _browser_context(self):
        browser = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                yield browser
        finally:
            if browser:
                await browser.close()

    @cached(cache=TTLCache(maxsize=100, ttl=3600))
    async def _fetch_with_requests(self, url: str) -> Tuple[str, str]:
        try:
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            self.logger.debug(f"Request headers: {headers}")
            
            # Try cloudscraper first
            try:
                self.logger.info("Attempting cloudscraper request...")
                response = self.cloudscraper.get(url, headers=headers, timeout=15)
                self.logger.debug(f"Cloudscraper status: {response.status_code}")
                self.logger.debug(f"Cloudscraper headers: {dict(response.headers)}")
                
                if response.ok:
                    self.logger.info("Cloudscraper request successful")
                    return response.text, ""
            except Exception as e:
                self.logger.debug(f"Cloudscraper failed with error type: {type(e).__name__}")
                self.logger.debug(f"Cloudscraper error details: {str(e)}")

            # Fall back to regular session
            self.logger.info("Falling back to regular session request...")
            response = self.session.get(url, headers=headers, timeout=15)
            self.logger.debug(f"Regular session status: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            self.logger.debug(f"Response encoding: {response.encoding}")
            
            response.raise_for_status()
            content_length = len(response.text)
            self.logger.info(f"Request successful, content length: {content_length} characters")
            return response.text, ""
        except Exception as e:
            self.logger.error(f"Request failed with error type: {type(e).__name__}")
            self.logger.error(f"Request error details: {str(e)}")
            return "", ""

    async def _fetch_with_requests_html(self, url: str) -> Tuple[str, str]:
        self.logger.info("Starting requests-html fetch process...")
        try:
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = await self.html_session.get(url, headers=headers, timeout=30)
            self.logger.debug(f"Initial response status: {response.status_code}")
            
            # Render JavaScript
            self.logger.info("Rendering JavaScript...")
            await response.html.arender(timeout=30)
            
            content = response.html.html
            title = response.html.find('title', first=True)
            title_text = title.text if title else ""
            
            self.logger.info("requests-html fetch successful")
            self.logger.debug(f"Content length: {len(content)} characters")
            return content, title_text
            
        except Exception as e:
            self.logger.error(f"requests-html fetch failed: {str(e)}")
            return "", ""

    async def _fetch_with_selenium(self, url: str) -> Tuple[str, str]:
        self.logger.info("Starting Selenium fetch process...")
        try:
            # Run selenium in a separate thread using anyio
            result = await anyio.to_thread.run_sync(
                self._selenium_fetch,
                url,
                cancellable=True
            )
            content, title = result
            if content:
                self.logger.info(f"Selenium fetch successful, title: {title}")
                self.logger.debug(f"Content length: {len(content)} characters")
                return result
        except anyio.get_cancelled_exc_class():
            self.logger.warning("Selenium fetch cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Selenium fetch failed with error type: {type(e).__name__}")
            self.logger.error(f"Selenium error details: {str(e)}")
        return "", ""

    def _selenium_fetch(self, url: str) -> Tuple[str, str]:
        self.logger.debug("Configuring Selenium Chrome options...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={self._get_random_user_agent()}')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = None
        try:
            self.logger.debug("Initializing Chrome driver...")
            driver = webdriver.Chrome(options=options)
            self.logger.debug(f"Setting page load timeout: 20 seconds")
            driver.set_page_load_timeout(20)
            
            self.logger.info(f"Navigating to URL: {url}")
            driver.get(url)
            
            self.logger.debug("Waiting for body element...")
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            content = driver.page_source
            title = driver.title
            self.logger.debug(f"Page loaded - Title: {title}")
            self.logger.debug(f"Content length: {len(content)} characters")
            return content, title
        finally:
            if driver:
                self.logger.debug("Closing Chrome driver...")
                driver.quit()

    async def _fetch_with_playwright(self, url: str) -> Tuple[str, str]:
        self.logger.info("Starting Playwright fetch process...")
        async with self._browser_context() as browser:
            try:
                context = await browser.new_context(
                    user_agent=self._get_random_user_agent()
                )
                page = await context.new_page()
                self.logger.info(f"Navigating to URL: {url}")
                
                response = await page.goto(url, wait_until='networkidle')
                if not response:
                    self.logger.error("Failed to get response from page")
                    return "", ""
                
                content = await page.content()
                title = await page.title()
                
                self.logger.info(f"Page loaded successfully - Title: {title}")
                self.logger.debug(f"Content length: {len(content)} characters")
                return content, title
                
            except Exception as e:
                self.logger.error(f"Playwright error type: {type(e).__name__}")
                self.logger.error(f"Playwright error details: {str(e)}")
                return "", ""

    async def fetch_content(self, url: str) -> Tuple[str, str]:
        self.logger.info(f"Starting fetch for URL: {url}")
        
        # Check cache first
        cache_key = f"content_{url}"
        if cache_key in self.cache:
            self.logger.info("Returning cached content")
            return self.cache[cache_key]

        fetch_methods = [
            (self._fetch_with_requests, "Requests", 5),  # timeout in seconds
            (self._fetch_with_requests_html, "Requests-HTML", 10),
            (self._fetch_with_selenium, "Selenium", 15),
            (self._fetch_with_playwright, "Playwright", 20)
        ]

        async with anyio.create_task_group() as tg:
            for method, name, timeout in fetch_methods:
                try:
                    with anyio.move_on_after(timeout):
                        content, title = await method(url)
                        if content:
                            # Cache successful result
                            self.cache[cache_key] = (content, title)
                            tg.cancel_scope.cancel()  # Stop other tasks
                            return content, title
                except Exception as e:
                    self.logger.error(f"{name} failed: {str(e)}")
                    continue

        self.logger.error("All fetch methods failed")
        return "", ""

    async def close(self):
        """Cleanup resources asynchronously"""
        self.logger.info("Cleaning up WebScraper resources...")
        self.process_pool.close()
        self.process_pool.join()
        self.executor.shutdown(wait=True)
        await self.html_session.close()
        self.session.close()
        self.logger.info("WebScraper cleanup completed")

    def __del__(self):
        """Fallback cleanup"""
        try:
            self.process_pool.close()
            self.process_pool.join()
            self.executor.shutdown(wait=False)
        except:
            pass