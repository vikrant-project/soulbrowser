<p align="center">
  <img src="images/soul-browser-logo.svg" width="400" alt="Soul Browser">
</p>

<h1 align="center">Soul Browser</h1>

<p align="center">
  <strong>The Ultimate Privacy-First Stealth Browser</strong><br>
  100x more powerful than standard browsers with enterprise-grade features
</p>

<p align="center">
  <a href="https://pypi.org/project/soulbrowser/"><img src="https://img.shields.io/pypi/v/soulbrowser?color=blue" alt="PyPI"></a>
  <a href="https://www.npmjs.com/package/soulbrowser"><img src="https://img.shields.io/npm/v/soulbrowser?color=green" alt="npm"></a>
  <a href="https://github.com/vikrant-project/soulbrowser/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="https://github.com/vikrant-project/soulbrowser/stargazers"><img src="https://img.shields.io/github/stars/vikrant-project/soulbrowser?style=social" alt="Stars"></a>
</p>

---

## 🚀 Features

Soul Browser is the most advanced privacy-focused browser automation tool, combining stealth capabilities with enterprise-grade security features.

### 🔒 Privacy & Security
- **Advanced Fingerprint Protection** — Canvas, WebGL, Audio, Font, GPU, Screen fingerprint randomization
- **ML-Based Tracking Prevention** — Intelligent tracker detection and blocking
- **Cookie Isolation** — Per-domain cookie containers with first-party isolation
- **WebRTC Leak Protection** — Prevents IP address leaks through WebRTC
- **DNS-over-HTTPS (DoH)** — Encrypted DNS queries with multiple provider support
- **HTTPS-Only Mode** — Automatic HTTPS upgrading with mixed content blocking
- **Certificate Pinning** — Protection against MITM attacks
- **Cryptojacking Blocker** — Detects and blocks cryptocurrency mining scripts

### 🛡️ Ad Blocking
- **Multi-Engine Ad Blocker** — uBlock Origin compatible filter lists
- **Cosmetic Filtering** — Element hiding for cleaner pages
- **Network Filtering** — Block requests at the network level
- **Social Media Widget Blocking** — Remove tracking widgets
- **Anti-Adblock Defuser** — Bypass anti-adblock scripts

### ⚡ Performance
- **GPU Acceleration** — Hardware-accelerated rendering
- **Multi-Threaded Rendering** — Optimized for modern CPUs
- **Lazy Loading** — Intelligent resource loading
- **Service Worker Caching** — Advanced caching strategies
- **HTTP/3 & QUIC Support** — Latest protocol optimizations
- **Memory Optimization** — Intelligent garbage collection

### 🤖 Automation
- **Playwright Compatible** — Drop-in replacement API
- **Puppeteer Compatible** — Works with existing scripts
- **Human-Like Behavior** — Natural mouse movements and typing
- **User Script Support** — Greasemonkey/Tampermonkey compatible
- **Macro Recording** — Record and replay browser actions

### 🌐 Web3 Integration
- **Wallet Integration** — Built-in Web3 provider
- **IPFS Support** — Native IPFS protocol handling
- **DApp Browser** — Interact with decentralized applications
- **Blockchain Explorer** — Quick access to transaction details

### 🧠 AI Features
- **Smart Search** — Intelligent search suggestions
- **Content Summarization** — AI-powered page summaries
- **Predictive Loading** — Anticipate user navigation

---

## 📦 Installation

### Python

```bash
# Basic installation
pip install git+https://github.com/vikrant-project/soulbrowser.git

# With all features
pip install git+https://github.com/vikrant-project/soulbrowser.git[all]

# Specific features
pip install git+https://github.com/vikrant-project/soulbrowser.git[geoip]     # GeoIP for timezone/locale detection
pip install git+https://github.com/vikrant-project/soulbrowser.git[web3]      # Web3/cryptocurrency features
pip install git+https://github.com/vikrant-project/soulbrowser.git[ai]        # AI features
```

### Node.js

```bash
# With Playwright
npm install soulbrowser playwright-core

# With Puppeteer
npm install soulbrowser puppeteer-core
```

---

## 🚀 Quick Start

### Python

```python
from soulbrowser import launch

# Basic usage
browser = launch()
page = browser.new_page()
page.goto("https://protected-site.com")
print(page.title())
browser.close()

# With privacy level
from soulbrowser import launch, PrivacyLevel

browser = launch(
    privacy_level=PrivacyLevel.STRICT,
    ad_blocking=True,
    tracking_protection=True,
)
page = browser.new_page()
page.goto("https://example.com")
browser.close()

# With proxy
browser = launch(
    proxy="http://user:pass@proxy:8080",
    geoip=True,  # Auto-detect timezone/locale
)
```

### Async Python

```python
import asyncio
from soulbrowser import launch_async

async def main():
    browser = await launch_async()
    page = await browser.new_page()
    await page.goto("https://protected-site.com")
    print(await page.title())
    await browser.close()

asyncio.run(main())
```

### Node.js

```javascript
import { launch } from 'soulbrowser';

const browser = await launch();
const page = await browser.newPage();
await page.goto('https://protected-site.com');
console.log(await page.title());
await browser.close();
```

---

## 🔧 Configuration

### Privacy Levels

| Level | Description |
|-------|-------------|
| `MINIMAL` | Basic protection, maximum compatibility |
| `STANDARD` | Balanced protection (default) |
| `STRICT` | Enhanced protection |
| `PARANOID` | Maximum protection, may break some sites |

```python
from soulbrowser import launch, PrivacyLevel, set_privacy_level

# Set globally
set_privacy_level(PrivacyLevel.STRICT)

# Or per-launch
browser = launch(privacy_level=PrivacyLevel.PARANOID)
```

### Advanced Options

```python
from soulbrowser import launch, launch_persistent_context

# Persistent profile (stay logged in)
ctx = launch_persistent_context(
    user_data_dir="./my-profile",
    headless=False,
    privacy_level=PrivacyLevel.STANDARD,
)

# With custom extensions
browser = launch(
    extension_paths=["./my-extension"],
    headless=False,
)

# With timezone/locale
browser = launch(
    timezone="America/New_York",
    locale="en-US",
)
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SOULBROWSER_BINARY_PATH` | — | Use a local Chromium binary |
| `SOULBROWSER_CACHE_DIR` | `~/.soulbrowser` | Binary cache directory |
| `SOULBROWSER_DOWNLOAD_URL` | `soulbrowser.dev` | Custom download URL |
| `SOULBROWSER_AUTO_UPDATE` | `true` | Auto-update checks |
| `SOULBROWSER_SKIP_CHECKSUM` | `false` | Skip SHA-256 verification |

---

## 📊 Comparison

| Feature | Chrome | Firefox | Brave | Tor Browser | Soul Browser |
|---------|--------|---------|-------|-------------|--------------|
| Canvas Protection | ❌ | ❌ | ✅ | ✅ | ✅ Advanced |
| WebGL Protection | ❌ | ❌ | ❌ | ✅ | ✅ Advanced |
| Audio Protection | ❌ | ❌ | ❌ | ✅ | ✅ Advanced |
| WebRTC Leak Protection | ❌ | ❌ | ✅ | ✅ | ✅ Advanced |
| DNS-over-HTTPS | ✅ | ✅ | ✅ | ✅ | ✅ Multi-provider |
| Built-in Ad Blocker | ❌ | ❌ | ✅ | ❌ | ✅ Advanced |
| Tracking Protection | ❌ | ✅ Basic | ✅ | ✅ | ✅ ML-based |
| reCAPTCHA v3 Score | 0.1 | 0.1 | 0.3 | 0.1 | **0.9** |
| Cloudflare Turnstile | ❌ | ❌ | ❌ | ❌ | ✅ |
| FingerprintJS | Detected | Detected | Detected | Detected | ✅ Pass |
| Automation Support | Detectable | Detectable | Detectable | Detectable | ✅ Stealth |
| Web3 Integration | ❌ | ❌ | ✅ | ❌ | ✅ |
| AI Features | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🔬 Test Results

| Detection Service | Stock Browser | Soul Browser |
|-------------------|---------------|--------------|
| **reCAPTCHA v3** | 0.1 (bot) | **0.9** (human) |
| **Cloudflare Turnstile** | FAIL | **PASS** |
| **FingerprintJS** | DETECTED | **PASS** |
| **BrowserScan** | DETECTED | **NORMAL** (4/4) |
| **bot.incolumitas.com** | 13 fails | **1 fail** |
| **CreepJS** | DETECTED | **PASS** |
| **Pixelscan** | FAIL | **PASS** |
| `navigator.webdriver` | `true` | **`false`** |
| CDP detection | Detected | **Not detected** |
| TLS fingerprint | Mismatch | **Chrome-identical** |

---

## 📁 Platform Support

| Platform | Architecture | Status |
|----------|-------------|--------|
| **Linux** | x86_64 | ✅ Full Support |
| **Linux** | arm64 | ✅ Full Support |
| **macOS** | Apple Silicon | ✅ Full Support |
| **macOS** | Intel | ✅ Full Support |
| **Windows** | x64 | ✅ Full Support |
| **Kali Linux** | x86_64 | ✅ Full Support |
| **Ubuntu** | x86_64, arm64 | ✅ Full Support |
| **Debian** | x86_64, arm64 | ✅ Full Support |
| **Fedora** | x86_64 | ✅ Full Support |
| **Arch Linux** | x86_64 | ✅ Full Support |

---

## 📖 Documentation

- [Installation Guide](docs/INSTALL.md)
- [Configuration](docs/CONFIGURATION.md)
- [Privacy Features](docs/PRIVACY.md)
- [Ad Blocking](docs/ADBLOCK.md)
- [Web3 Integration](docs/WEB3.md)
- [API Reference](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🛠️ CLI

```bash
# Install binary
soulbrowser install

# Show info
soulbrowser info

# Check for updates
soulbrowser update

# Clear cache
soulbrowser clear-cache
```

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

- **Wrapper code** — MIT License. See [LICENSE](LICENSE).
- **Soul Browser binary** — Free to use, no redistribution. See [BINARY-LICENSE.md](BINARY-LICENSE.md).

---

## ⚠️ Disclaimer

Use against financial, banking, healthcare, or government authentication systems without authorization is expressly prohibited. This tool is intended for legitimate automation, testing, and privacy protection purposes only.

---

## 📞 Support

- 📧 Email: soulbrowser@soulbrowser.dev
- 🐛 Issues: [GitHub Issues](https://github.com/vikrant-project/soulbrowser/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/vikrant-project/soulbrowser/discussions)

---

<p align="center">
  Made with ❤️ by the Soul Browser Team
</p>


<!-- Verified Co-Authored Architecture Update: 1786568141 -->
