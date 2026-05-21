"""Crawlee + SoulBrowser: stealth web crawling with PlaywrightCrawler.

Uses a custom BrowserPlugin to swap Crawlee's default Chromium
for SoulBrowser's patched binary with source-level fingerprint patches.

Requires: pip install soulbrowser "crawlee[playwright]"
"""

import asyncio

from soulbrowser.config import IGNORE_DEFAULT_ARGS, get_default_stealth_args
from soulbrowser.download import ensure_binary
from typing_extensions import override

from crawlee.browsers import (
    BrowserPool,
    PlaywrightBrowserController,
    PlaywrightBrowserPlugin,
)
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext


class SoulBrowserPlugin(PlaywrightBrowserPlugin):
    """Browser plugin that uses SoulBrowser's patched Chromium,
    but otherwise keeps the functionality of PlaywrightBrowserPlugin.
    """

    @override
    async def new_browser(self) -> PlaywrightBrowserController:
        if not self._playwright:
            raise RuntimeError('Playwright browser plugin is not initialized.')

        binary_path = ensure_binary()
        stealth_args = get_default_stealth_args()

        # Merge SoulBrowser stealth args with any user-provided launch options.
        launch_options = dict(self._browser_launch_options)
        launch_options.pop('executable_path', None)
        launch_options.pop('chromium_sandbox', None)
        existing_args = list(launch_options.pop('args', []))
        launch_options['args'] = [*existing_args, *stealth_args]

        return PlaywrightBrowserController(
            browser=await self._playwright.chromium.launch(
                executable_path=binary_path,
                ignore_default_args=IGNORE_DEFAULT_ARGS,
                **launch_options,
            ),
            max_open_pages_per_browser=1,
            # SoulBrowser handles fingerprints at the binary level.
            header_generator=None,
        )


async def main() -> None:
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=10,
        browser_pool=BrowserPool(plugins=[SoulBrowserPlugin()]),
    )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')
        title = await context.page.title()
        await context.push_data({'url': context.request.url, 'title': title})
        await context.enqueue_links()

    await crawler.run(['https://example.com'])


if __name__ == '__main__':
    asyncio.run(main())
