# Soul Browser - Installation Guide

## Install from Source (Recommended)

Since Soul Browser is not yet published to PyPI, install directly from the repository:

### Option 1: Install from GitHub URL
```bash
pip install git+https://github.com/vikrant-project/soulbrowser.git
```

### Option 2: Install from cloned repo
```bash
git clone https://github.com/vikrant-project/soulbrowser.git
cd soulbrowser
pip install -e .
```

### With extras (optional features)
```bash
# From GitHub
pip install "git+https://github.com/vikrant-project/soulbrowser.git#egg=soulbrowser[all]"

# From local clone
pip install -e ".[all]"
pip install -e ".[geoip]"
pip install -e ".[web3]"
pip install -e ".[ai]"
```

## Verify Installation
```bash
python -c "from soulbrowser import launch; print('SoulBrowser installed successfully!')"
```

## Quick Start
```python
from soulbrowser import launch

browser = launch()
page = browser.new_page()
page.goto("https://example.com")
print(page.title())
browser.close()
```
