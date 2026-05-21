"""Selenium + SoulBrowser: use stealth Chromium with Selenium WebDriver.

SoulBrowser provides the binary and stealth args.
Selenium drives it via ChromeDriver.

Requires: pip install selenium soulbrowser
Note: ChromeDriver version must match Chromium 145.
      pip install chromedriver-autoinstaller or download manually.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from soulbrowser.config import get_default_stealth_args
from soulbrowser.download import ensure_binary

binary_path = ensure_binary()
stealth_args = get_default_stealth_args()

options = Options()
options.binary_location = binary_path
options.add_argument("--headless")
for arg in stealth_args:
    options.add_argument(arg)

driver = webdriver.Chrome(options=options)

driver.get("https://example.com")
print(f"Selenium + SoulBrowser: {driver.title}")

# Verify stealth
result = driver.execute_script("""
    return {
        webdriver: navigator.webdriver,
        plugins: navigator.plugins.length,
        platform: navigator.platform,
    }
""")
print(f"Stealth checks: {result}")

driver.quit()
