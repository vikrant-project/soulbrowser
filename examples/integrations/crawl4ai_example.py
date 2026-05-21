"""Crawl4AI + SoulBrowser: LLM-ready web crawling with stealth fingerprints.

Crawl4AI handles extraction and markdown conversion,
SoulBrowser handles bot detection.

Requires: pip install crawl4ai soulbrowser
"""

import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

from soulbrowser import launch_async


async def main():
    # Step 1: Launch SoulBrowser with remote debugging
    cb_browser = await launch_async(
        headless=True,
        args=["--remote-debugging-port=9243", "--remote-debugging-address=127.0.0.1"],
    )

    # Step 2: Connect Crawl4AI to the stealth browser via CDP
    browser_config = BrowserConfig(browser_mode="cdp", cdp_url="http://127.0.0.1:9243")
    run_config = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            "https://example.com",
            config=run_config,
        )
        print(f"Extracted {len(result.markdown)} chars of markdown")
        print(result.markdown[:500])

    await cb_browser.close()


if __name__ == "__main__":
    asyncio.run(main())
