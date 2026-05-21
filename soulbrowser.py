#!/usr/bin/env python3
"""
Soul Browser Test Script
Opens https://telegram.org/support for 2 minutes in visible mode (no headless)
Uses Playwright with stealth settings
"""

import time
from playwright.sync_api import sync_playwright

def main():
    print("🚀 Starting Soul Browser...")
    print("📍 Opening: https://telegram.org/support")
    print("⏱️  Will stay open for 2 minutes")
    print("-" * 50)
    
    with sync_playwright() as p:
        # Launch Chromium in visible mode with stealth args
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--disable-browser-side-navigation",
                "--disable-gpu-sandbox",
                "--no-first-run",
                "--no-service-autorun",
                "--password-store=basic",
                "--use-mock-keychain",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-background-timer-throttling",
                "--disable-ipc-flooding-protection",
                "--enable-features=NetworkService,NetworkServiceInProcess",
            ]
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
        )
        
        # Remove webdriver detection
        context.add_init_script("""
            Object.defineProperty(navigator, webdriver, {
                get: () => undefined
            });
            
            // Overwrite plugins
            Object.defineProperty(navigator, plugins, {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Overwrite languages
            Object.defineProperty(navigator, languages, {
                get: () => [en-US, en]
            });
            
            // Hide automation
            window.chrome = { runtime: {} };
        """)
        
        # Create page and navigate
        page = context.new_page()
        page.goto("https://telegram.org/support", wait_until="domcontentloaded")
        
        print(f"✅ Page loaded: {page.title()}")
        print("⏳ Waiting for 2 minutes...")
        
        # Wait for 2 minutes (120 seconds)
        time.sleep(120)
        
        print("🛑 Closing browser...")
        browser.close()
        
    print("✅ Done!")

if __name__ == "__main__":
    main()
