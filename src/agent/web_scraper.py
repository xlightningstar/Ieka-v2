from playwright.async_api import async_playwright
import asyncio
from typing import Optional


class WebScraper:
    """Handles web scraping using headless browser."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def initialize(self):
        """Initialize the browser instance."""
        if self.browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.firefox.launch(headless=True)
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def search_web(self, query: str) -> str:
        """Perform a web search and extract results.
        
        Args:
            query: The search query or URL
            
        Returns:
            Extracted text content from the page
        """
        await self.initialize()
        page = await self.context.new_page()

        try:
            url = query if query.startswith("http") else \
                f"https://html.duckduckgo.com/html/?q={query}"

            await page.goto(url, timeout=15000, wait_until="domcontentloaded")

            if "duckduckgo" in url:
                results = await page.query_selector_all(".result")
                extracted = []

                for i, result in enumerate(results[:5], 1):
                    title = await result.inner_text()
                    extracted.append(f"{i}. {title}")

                return "\n".join(extracted) or "No results found"

            else:
                body = await page.inner_text("body")
                return body[:2000]

        finally:
            if 'page' in locals():
                await page.close()
        
    async def get_weather(self, location: str = "London") -> str:
        """Get current weather for a location.
        
        Args:
            location: The location to get weather for
            
        Returns:
            Weather information
        """
        try:
            await self.initialize()
            page = await self.context.new_page()
            
            # Use wttr.in for weather (text-based weather service)
            url = f"https://wttr.in/{location}?format=3"
            await page.goto(url, timeout=10000)
            
            body = await page.query_selector('body')
            weather_text = await body.inner_text() if body else "Could not fetch weather"
            
            await page.close()
            return weather_text.strip()
            
        except Exception as e:
            return f"Weather fetch failed: {str(e)}"


# Singleton instance
_scraper_instance = None


def get_scraper() -> WebScraper:
    """Get or create the web scraper singleton instance."""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = WebScraper()
    return _scraper_instance
