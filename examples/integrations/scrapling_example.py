"""Scrapling + SoulBrowser: adaptive web scraping with stealth fingerprints.

Scrapling handles parsing and element tracking,
SoulBrowser handles bot detection.

Requires: pip install scrapling[all] soulbrowser
"""

import asyncio
import json
from urllib.request import urlopen

from scrapling.fetchers import StealthyFetcher

from soulbrowser import launch_async


async def main():
    # Launch SoulBrowser with remote debugging
    cb_browser = await launch_async(
        headless=True,
        args=["--remote-debugging-port=9245", "--remote-debugging-address=127.0.0.1"],
    )

    # Get the WebSocket URL from Chrome (Scrapling requires ws:// scheme)
    info = json.loads(urlopen("http://127.0.0.1:9245/json/version").read())
    ws_url = info["webSocketDebuggerUrl"]

    # Connect Scrapling to the stealth browser via CDP
    page = await StealthyFetcher.async_fetch(
        "https://example.com",
        cdp_url=ws_url,
    )

    print(f"Title: {page.css('title::text').get()}")
    print(f"Text: {page.css('p::text').getall()}")

    await cb_browser.close()


if __name__ == "__main__":
    asyncio.run(main())
