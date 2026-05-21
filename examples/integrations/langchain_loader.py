"""LangChain + SoulBrowser: load web pages behind bot detection into LangChain Documents.

LangChain's PlaywrightURLLoader hardcodes chromium.launch() with no way to pass
a custom binary. This example uses SoulBrowser directly as a stealth document loader
that produces LangChain Document objects.

Requires: pip install langchain-core soulbrowser
"""

import asyncio

from langchain_core.documents import Document

from soulbrowser import launch_async


async def load_urls_stealth(urls: list[str], **launch_kwargs) -> list[Document]:
    """Load URLs using SoulBrowser stealth browser, return LangChain Documents."""
    browser = await launch_async(headless=True, **launch_kwargs)
    page = await browser.new_page()
    docs = []

    for url in urls:
        await page.goto(url, wait_until="domcontentloaded")
        text = await page.evaluate("document.body.innerText")
        title = await page.title()
        docs.append(Document(
            page_content=text,
            metadata={"source": url, "title": title},
        ))

    await browser.close()
    return docs


async def main():
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
    ]

    docs = await load_urls_stealth(urls)

    for doc in docs:
        print(f"--- {doc.metadata['title']} ({doc.metadata['source']}) ---")
        print(doc.page_content[:300])
        print()


if __name__ == "__main__":
    asyncio.run(main())
