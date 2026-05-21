# Soul Browser API Reference

## SoulBrowser Class

```python
from soulbrowser import SoulBrowser

browser = SoulBrowser(
    headless=False,
    proxy=None,
    fingerprint_protection=True
)
```

### Methods

#### new_page()
Create a new browser page.

```python
page = browser.new_page()
```

#### close()
Close the browser.

```python
browser.close()
```

## Page Methods

### Navigation

```python
page.goto("https://example.com")
page.reload()
page.go_back()
page.go_forward()
```

### Interaction

```python
page.click("button#submit")
page.fill("input[name=email]", "test@example.com")
page.select("select#country", "US")
```

### Privacy

```python
page.enable_fingerprint_protection()
page.set_proxy("socks5://localhost:9050")
page.enable_tor()
```

### Media

```python
page.mute_all()
page.enable_pip()
page.set_playback_rate(1.5)
```

## Events

```python
page.on("request", lambda req: print(req.url))
page.on("response", lambda res: print(res.status))
```

## Async API

```python
import asyncio
from soulbrowser import AsyncSoulBrowser

async def main():
    browser = AsyncSoulBrowser()
    page = await browser.new_page()
    await page.goto("https://example.com")
    await browser.close()

asyncio.run(main())
```
