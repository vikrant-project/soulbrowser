"""browser-use + SoulBrowser: AI agent with stealth fingerprints.

browser-use handles AI agent logic, SoulBrowser handles bot detection.
Your agent can now browse sites behind Cloudflare, reCAPTCHA, DataDome.

Requires: pip install browser-use soulbrowser
Set OPENAI_API_KEY (or swap for another LLM provider).
"""

import asyncio

from browser_use import Agent, BrowserSession, ChatOpenAI

from soulbrowser import launch_async


async def main():
    # Step 1: Launch SoulBrowser (handles binary, stealth args, fingerprints)
    cb_browser = await launch_async(
        headless=True,
        args=["--remote-debugging-port=9242", "--remote-debugging-address=127.0.0.1"],
    )

    # Step 2: Connect browser-use to the stealth browser via CDP
    session = BrowserSession(cdp_url="http://127.0.0.1:9242")

    # Step 3: Run your AI agent — it browses through SoulBrowser
    agent = Agent(
        task="Go to https://www.google.com and search for 'browser automation'",
        llm=ChatOpenAI(model="gpt-4o-mini"),
        browser_session=session,
    )

    result = await agent.run()
    print(result)

    await cb_browser.close()


if __name__ == "__main__":
    asyncio.run(main())
