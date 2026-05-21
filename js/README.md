<p align="center">
<img src="https://i.imgur.com/cqkp6fG.png" width="500" alt="SoulBrowser">
</p>

# SoulBrowser

[![npm](https://img.shields.io/npm/v/soulbrowser)](https://www.npmjs.com/package/soulbrowser)
[![License](https://img.shields.io/github/license/SoulBrowser/SoulBrowser)](https://github.com/SoulBrowser/SoulBrowser/blob/main/LICENSE)

**Stealth Chromium that passes every bot detection test.**

Drop-in Playwright/Puppeteer replacement. Same API, same code — just swap the import. **3 lines of code, 30 seconds to unblock.**

- **48 source-level C++ patches** — canvas, WebGL, audio, fonts, GPU, screen, WebRTC, network timing, automation signals
- **0.9 reCAPTCHA v3 score** — human-level, server-verified
- **Passes Cloudflare Turnstile**, FingerprintJS, BrowserScan — tested against 30+ detection sites
- **`npm install soulbrowser`** — binary auto-downloads, auto-updates, zero config
- **Free and open source** — no subscriptions, no usage limits
- **Works with any framework** — tested with browser-use, Crawl4AI, Scrapling, Stagehand ([example](examples/stagehand.ts)), LangChain, Selenium, and more

## Install

```bash
# With Playwright
npm install soulbrowser playwright-core

# With Puppeteer
npm install soulbrowser puppeteer-core
```

On first launch, the stealth Chromium binary auto-downloads (~200MB, cached at `~/.soulbrowser/`).

## Usage

### Playwright (default)

```javascript
import { launch } from 'soulbrowser';

const browser = await launch();
const page = await browser.newPage();
await page.goto('https://protected-site.com');
console.log(await page.title());
await browser.close();
```

### Puppeteer

> **Note:** Playwright is recommended for sites with reCAPTCHA Enterprise. Puppeteer's CDP protocol leaks automation signals that reCAPTCHA Enterprise can detect. This is a known Puppeteer limitation, not specific to SoulBrowser.

```javascript
import { launch } from 'soulbrowser/puppeteer';

const browser = await launch();
const page = await browser.newPage();
await page.goto('https://protected-site.com');
console.log(await page.title());
await browser.close();
```

### Options

```javascript
import { launch, launchContext, launchPersistentContext } from 'soulbrowser';

// With proxy (HTTP or SOCKS5)
const browser = await launch({
  proxy: 'http://user:pass@proxy:8080',
});
const browser = await launch({
  proxy: 'socks5://user:pass@proxy:1080',
});

// With proxy object (bypass, separate auth fields)
const browser = await launch({
  proxy: { server: 'http://proxy:8080', bypass: '.google.com', username: 'user', password: 'pass' },
});

// Headed mode (visible browser window)
const browser = await launch({ headless: false });

// Extra Chrome args
const browser = await launch({
  args: ['--fingerprint=12345'],
});

// With timezone and locale
const browser = await launch({
  timezone: 'America/New_York',
  locale: 'en-US',
});

// Auto-detect timezone/locale from proxy IP (requires: npm install mmdb-lib)
const browser = await launch({
  proxy: 'http://proxy:8080',
  geoip: true,
});

// Browser + context in one call (timezone/locale set via binary flags)
const context = await launchContext({
  userAgent: 'Custom UA',
  viewport: { width: 1920, height: 1080 },
  locale: 'en-US',
  timezone: 'America/New_York',
});

// Persistent profile — stay logged in, bypass incognito detection, load extensions
const ctx = await launchPersistentContext({
  userDataDir: './chrome-profile',
  headless: false,
  proxy: 'http://user:pass@proxy:8080',
});
const page = ctx.pages()[0] || await ctx.newPage();
await page.goto('https://example.com');
await ctx.close();  // profile saved — reuse same path to restore state
```

### Auto Timezone/Locale from Proxy IP

When using a proxy, antibot systems check that your browser's timezone and locale match the proxy's location. Install `mmdb-lib` to enable auto-detection from an offline GeoIP database (~70 MB, downloaded on first use):

```bash
npm install mmdb-lib
```

```javascript
// Auto-detect — timezone and locale set from proxy's IP geolocation
const browser = await launch({ proxy: 'http://proxy:8080', geoip: true });

// Works with launchContext too
const context = await launchContext({ proxy: 'http://proxy:8080', geoip: true });

// Explicit values always win over auto-detection
const browser = await launch({ proxy: 'http://proxy:8080', geoip: true, timezone: 'Europe/London' });
```

> **Note:** For rotating residential proxies, the DNS-resolved IP may differ from the exit IP. Pass explicit `timezone`/`locale` in those cases.

### CLI

Pre-download the binary or check installation status from the command line:

```bash
npx soulbrowser install      # Download binary with progress output
npx soulbrowser info         # Show version, path, platform
npx soulbrowser update       # Check for and download newer binary
npx soulbrowser clear-cache  # Remove cached binaries
```

### Utilities

```javascript
import { ensureBinary, clearCache, binaryInfo, checkForUpdate } from 'soulbrowser';

// Pre-download binary (e.g., during Docker build)
await ensureBinary();

// Check installation
console.log(binaryInfo());

// Force re-download
clearCache();

// Manually check for newer Chromium version
const newVersion = await checkForUpdate();
if (newVersion) console.log(`Updated to ${newVersion}`);
```

## Test Results

| Detection Service | Stock Browser | SoulBrowser |
|---|---|---|
| **reCAPTCHA v3** | 0.1 (bot) | **0.9** (human) |
| **Cloudflare Turnstile** | FAIL | **PASS** |
| **FingerprintJS** | DETECTED | **PASS** |
| **BrowserScan** | DETECTED | **NORMAL** (4/4) |
| **bot.incolumitas.com** | 13 fails | **1 fail** |
| `navigator.webdriver` | `true` | **`false`** |
| CDP detection | Detected | **Not detected** |
| TLS fingerprint | Mismatch | **Identical to Chrome** |
| | | **Tested against 30+ detection sites** |

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `SOULBROWSER_BINARY_PATH` | — | Skip download, use a local Chromium binary |
| `SOULBROWSER_CACHE_DIR` | `~/.soulbrowser` | Binary cache directory |
| `SOULBROWSER_DOWNLOAD_URL` | `soulbrowser.dev` | Custom download URL |
| `SOULBROWSER_AUTO_UPDATE` | `true` | Set to `false` to disable background update checks |
| `SOULBROWSER_SKIP_CHECKSUM` | `false` | Set to `true` to skip SHA-256 verification after download |

## Migrate From Playwright

```diff
- import { chromium } from 'playwright';
- const browser = await chromium.launch();
+ import { launch } from 'soulbrowser';
+ const browser = await launch();

const page = await browser.newPage();
// ... rest of your code works unchanged
```

## Platforms

| Platform | Chromium | Patches | Status |
|---|---|---|---|
| Linux x86_64 | 145 | 48 | ✅ Latest |
| Linux arm64 (RPi, Graviton) | 145 | 48 | ✅ Latest |
| macOS arm64 (Apple Silicon) | 145 | 26 | ✅ Latest |
| macOS x86_64 (Intel) | 145 | 26 | ✅ Latest |
| Windows x86_64 | 145 | 48 | ✅ Latest |

## Requirements

- Node.js >= 20
- One of: `playwright-core` >= 1.53 or `puppeteer-core` >= 21

## Troubleshooting

**Site detects incognito / private browsing mode**

By default, `launch()` opens an incognito context. Some sites (like BrowserScan) detect this. Use `launchPersistentContext()` instead — it runs with a real user profile:

```javascript
import { launchPersistentContext } from 'soulbrowser';

const ctx = await launchPersistentContext({
  userDataDir: './my-profile',
  headless: false,
});

// Load Chrome extensions
const ctx = await launchPersistentContext({
  userDataDir: './my-profile',
  headless: false,
  extensionPaths: ['./my-extension'],
});
```

This also gives you cookie and localStorage persistence across sessions.

**reCAPTCHA v3 scores are low (0.1–0.3)**

Avoid `page.waitForTimeout()` — it sends CDP protocol commands that reCAPTCHA detects. Use native sleep instead:

```javascript
// Bad — sends CDP commands, reCAPTCHA detects this
await page.waitForTimeout(3000);

// Good — invisible to the browser
await new Promise(r => setTimeout(r, 3000));
```

Other tips for maximizing reCAPTCHA scores:
- **Use Playwright, not Puppeteer** — Puppeteer sends more CDP protocol traffic that reCAPTCHA detects ([details](#puppeteer))
- **Use residential proxies** — datacenter IPs are flagged by IP reputation, not browser fingerprint
- **Spend 15+ seconds on the page** before triggering reCAPTCHA — short visits score lower
- **Space out requests** — back-to-back `grecaptcha.execute()` calls from the same session get penalized. Wait 30+ seconds between pages with reCAPTCHA
- **Use a fixed fingerprint seed** (`--fingerprint=12345`) for consistent device identity across sessions
- **Use `page.type()` instead of `page.fill()`** for form filling — `fill()` sets values directly without keyboard events, which reCAPTCHA's behavioral analysis flags. `type()` with a delay simulates real keystrokes:
  ```javascript
  await page.type('#email', 'user@example.com', { delay: 50 });
  ```
- **Minimize `page.evaluate()` calls** before the reCAPTCHA check fires — each one sends CDP traffic

**New update broke something? Roll back to the previous version**
When auto-update downloads a newer binary, the previous version stays in `~/.soulbrowser/`. Point `SOULBROWSER_BINARY_PATH` to the older cached binary:
```bash
# Linux
export SOULBROWSER_BINARY_PATH=~/.soulbrowser/chromium-145.0.7632.159.2/chrome

# macOS
export SOULBROWSER_BINARY_PATH=~/.soulbrowser/chromium-145.0.7632.109.2/Chromium.app/Contents/MacOS/Chromium

# Windows
set SOULBROWSER_BINARY_PATH=%USERPROFILE%\.soulbrowser\chromium-145.0.7632.159.7\chrome.exe
```

## Links

- 🌐 [Website](https://soulbrowser.dev)
- 🐛 [Bug reports & feature requests](https://github.com/SoulBrowser/SoulBrowser/issues)
- 📦 [PyPI (Python package)](https://pypi.org/project/soulbrowser/)
- 📖 [Full documentation](https://github.com/SoulBrowser/SoulBrowser#readme)
- 📧 Contact: soulbrowser-team@pm.me

## License

- **Wrapper code** (this repository) — MIT. See [LICENSE](https://github.com/SoulBrowser/SoulBrowser/blob/main/LICENSE).
- **SoulBrowser binary** (compiled Chromium) — free to use, no redistribution. See [BINARY-LICENSE.md](https://github.com/SoulBrowser/SoulBrowser/blob/main/BINARY-LICENSE.md).

Use against financial, banking, healthcare, or government authentication systems without authorization is expressly prohibited.
