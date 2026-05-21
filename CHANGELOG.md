# Soul Browser Changelog

All notable changes to Soul Browser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-21

### Added

#### Core Browser
- Initial release of Soul Browser
- Drop-in Playwright/Puppeteer replacement
- Chromium 146 with 48+ source-level patches
- Multi-platform support (Windows, macOS, Linux)

#### Privacy & Security
- Advanced fingerprint protection (canvas, WebGL, audio, fonts, GPU, screen)
- ML-based tracking prevention
- Cookie isolation per domain
- First-party isolation
- Cross-origin isolation
- WebRTC leak protection
- DNS-over-HTTPS (DoH) with multiple providers
- HTTPS-only mode
- Certificate pinning support
- Cryptojacking blocker
- Referrer policy enforcement
- Battery API blocking
- Sensor API blocking
- Clipboard protection

#### Ad Blocking
- Multi-engine ad blocker (uBlock Origin compatible)
- Custom filter list support
- Cosmetic filtering
- Network-level blocking
- Social media widget blocking
- Anti-adblock defuser

#### Performance
- GPU acceleration
- Multi-threaded rendering
- Lazy loading
- Service worker caching
- HTTP/3 and QUIC support
- Brotli compression
- Resource preloading
- Memory optimization

#### Automation
- Playwright API compatibility
- Puppeteer API compatibility
- Human-like behavior mode
- User script support (Greasemonkey compatible)
- Macro recording and playback

#### Web3
- Built-in Web3 wallet provider
- IPFS protocol support
- Blockchain explorer integration

#### AI Features
- Smart search suggestions
- Content summarization
- Predictive page loading

#### Developer Tools
- Network inspector with HAR export
- Console capture
- Performance metrics

### Security
- SHA-256 checksum verification for downloads
- Secure binary distribution
- No telemetry or data collection

---

## Coming Soon

### [1.1.0] - Planned
- Built-in VPN integration
- Tor network support
- I2P protocol support
- Enhanced AI features with local LLM
- Voice commands
- Mobile platform support (Android, iOS)
