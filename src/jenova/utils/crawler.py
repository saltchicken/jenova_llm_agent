import asyncio
from crawl4ai import *

async def crawl(link):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url = link
        )
        return result.markdown
