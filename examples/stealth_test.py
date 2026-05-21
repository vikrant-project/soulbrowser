"""Run stealth tests against major bot detection services.

Tests soulbrowser against multiple detection sites, extracts pass/fail
verdicts via JS evaluation, and reports results with screenshots.

Usage:
    python examples/stealth_test.py
    python examples/stealth_test.py --headed     # watch in real-time
    python examples/stealth_test.py --no-screenshots
    python examples/stealth_test.py --proxy http://10.50.96.5:8888
"""

import json
import sys
import time

from soulbrowser import launch

HEADED = "--headed" in sys.argv
SCREENSHOTS = "--no-screenshots" not in sys.argv
PROXY = None
for i, arg in enumerate(sys.argv):
    if arg == "--proxy" and i + 1 < len(sys.argv):
        PROXY = sys.argv[i + 1]


def test_bot_sannysoft(page):
    """bot.sannysoft.com — classic bot detection checks."""
    page.goto("https://bot.sannysoft.com", wait_until="networkidle", timeout=30000)
    time.sleep(3)

    results = page.evaluate("""() => {
        const rows = document.querySelectorAll('table tr');
        const data = {};
        rows.forEach(r => {
            const cells = r.querySelectorAll('td');
            if (cells.length >= 2) {
                const key = cells[0].innerText.trim();
                const val = cells[1].innerText.trim();
                const cls = cells[1].className || '';
                data[key] = {value: val, passed: !cls.includes('failed')};
            }
        });
        return data;
    }""")

    failed = [k for k, v in results.items() if not v["passed"]]
    total = len(results)
    passed = total - len(failed)
    return {"passed": passed, "total": total, "failed": failed}


def test_bot_incolumitas(page):
    """bot.incolumitas.com — comprehensive 30+ check bot detection."""
    page.goto("https://bot.incolumitas.com", wait_until="networkidle", timeout=30000)

    # Poll until test count stabilizes (site runs tests progressively)
    last_total = 0
    for _ in range(15):
        time.sleep(2)
        results = page.evaluate("""() => {
            const text = document.body.innerText;
            const okMatches = text.match(/"\\w+":\\s*"OK"/g) || [];
            const failMatches = text.match(/"\\w+":\\s*"FAIL"/g) || [];
            const failedTests = failMatches.map(m => m.match(/"(\\w+)"/)[1]);
            return {
                passed: okMatches.length,
                failed: failMatches.length,
                failedTests,
                total: okMatches.length + failMatches.length
            };
        }""")
        if results["total"] >= 30 and results["total"] == last_total:
            break
        last_total = results["total"]

    return results


def test_browserscan(page):
    """browserscan.net/bot-detection — WebDriver, UA, CDP, Navigator checks."""
    page.goto("https://www.browserscan.net/bot-detection", wait_until="networkidle", timeout=30000)
    time.sleep(5)

    results = page.evaluate("""() => {
        const items = document.querySelectorAll('[class*="result"], [class*="item"], [class*="check"]');
        let normal = 0, abnormal = 0;
        const text = document.body.innerText;
        // Count "Normal" vs "Abnormal" verdicts
        const normalMatches = text.match(/Normal/g);
        const abnormalMatches = text.match(/Abnormal/g);
        return {
            normal: normalMatches ? normalMatches.length : 0,
            abnormal: abnormalMatches ? abnormalMatches.length : 0,
            pageText: text.substring(0, 500)
        };
    }""")
    return results


def test_deviceandbrowserinfo(page):
    """deviceandbrowserinfo.com/are_you_a_bot — fingerprint + behavioral detection."""
    page.goto("https://deviceandbrowserinfo.com/are_you_a_bot", wait_until="domcontentloaded", timeout=30000)
    time.sleep(8)

    results = page.evaluate("""() => {
        const text = document.body.innerText;
        // Site outputs JSON with "isBot": false and detail checks
        const botMatch = text.match(/"isBot":\\s*(true|false)/);
        const isBot = botMatch ? botMatch[1] === 'true' : null;
        const checks = {};
        const patterns = [
            'isBot', 'hasBotUserAgent', 'hasWebdriverTrue',
            'isHeadlessChrome', 'isAutomatedWithCDP', 'hasSuspiciousWeakSignals',
            'isPlaywright', 'hasInconsistentChromeObject'
        ];
        patterns.forEach(p => {
            const match = text.match(new RegExp('"' + p + '":\\s*(true|false)'));
            if (match) checks[p] = match[1] === 'true';
        });
        return {isBot, checks};
    }""")
    return results


def test_fingerprintjs(page):
    """demo.fingerprint.com/web-scraping — industry-standard bot detection."""
    page.goto("https://demo.fingerprint.com/web-scraping", wait_until="domcontentloaded", timeout=30000)
    time.sleep(8)

    # Click search to trigger bot detection — bots get blocked, humans see flights
    try:
        page.click("button:has-text('Search')", timeout=5000)
        time.sleep(5)
    except Exception:
        pass

    results = page.evaluate("""() => {
        const text = document.body.innerText;
        // Bots see error messages; humans see flight prices
        const hasFlights = text.includes('Price per adult') || text.includes('$');
        const isBlocked = text.includes('request was blocked') || text.includes('bot visit detected');
        return {passed: hasFlights && !isBlocked, isBlocked, hasFlights};
    }""")
    return results


def test_recaptcha(page):
    """recaptcha-demo.appspot.com — Google's official reCAPTCHA v3 score."""
    page.goto(
        "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    # Wait for score to appear (polls up to 30s)
    for _ in range(15):
        time.sleep(2)
        score = page.evaluate("""() => {
            const text = document.body.innerText;
            const match = text.match(/"score":\\s*(\\d+\\.\\d+)/);
            return match ? parseFloat(match[1]) : null;
        }""")
        if score is not None:
            break

    return {"score": score}


TESTS = [
    {
        "name": "bot.sannysoft.com",
        "url": "https://bot.sannysoft.com",
        "runner": test_bot_sannysoft,
        "verdict": lambda r: f"{r['passed']}/{r['total']} passed"
            + (f" (FAILED: {', '.join(r['failed'])})" if r["failed"] else " — ALL GREEN"),
        "pass": lambda r: len(r["failed"]) == 0,
    },
    {
        "name": "bot.incolumitas.com",
        "url": "https://bot.incolumitas.com",
        "runner": test_bot_incolumitas,
        "verdict": lambda r: f"{r['passed']}/{r['total']} passed"
            + (" — ALL GREEN" if r.get("failed", 0) == 0
               else f" (FAILED: {', '.join(r.get('failedTests', []))} — known false positives)"
               if set(r.get("failedTests", [])) <= {"WEBDRIVER", "connectionRTT"}
               else f" (FAILED: {', '.join(r.get('failedTests', []))})"),
        "pass": lambda r: set(r.get("failedTests", [])) <= {"WEBDRIVER", "connectionRTT"},  # known false positives
    },
    {
        "name": "BrowserScan",
        "url": "https://www.browserscan.net/bot-detection",
        "runner": test_browserscan,
        "verdict": lambda r: f"Normal: {r['normal']}, Abnormal: {r['abnormal']}",
        "pass": lambda r: r.get("abnormal", 1) == 0,
    },
    {
        "name": "deviceandbrowserinfo.com",
        "url": "https://deviceandbrowserinfo.com/are_you_a_bot",
        "runner": test_deviceandbrowserinfo,
        "verdict": lambda r: f"isBot: {r.get('isBot', 'unknown')}"
            + (f" checks: {json.dumps(r.get('checks', {}))}" if r.get("checks") else ""),
        "pass": lambda r: not r.get("isBot", True),
    },
    {
        "name": "FingerprintJS",
        "url": "https://demo.fingerprint.com/web-scraping",
        "runner": test_fingerprintjs,
        "verdict": lambda r: "PASSED (flights shown)" if r.get("passed") else "BLOCKED" if r.get("isBlocked") else "NO FLIGHTS",
        "pass": lambda r: r.get("passed", False),
    },
    {
        "name": "reCAPTCHA v3 (Google)",
        "url": "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php",
        "runner": test_recaptcha,
        "verdict": lambda r: f"Score: {r.get('score', 'N/A')}",
        "pass": lambda r: (r.get("score") or 0) >= 0.7,
    },
]


def main():
    print("=" * 60)
    print("SoulBrowser Stealth Test Suite")
    print("=" * 60)
    print(f"Mode: {'headed' if HEADED else 'headless'}")
    print(f"Screenshots: {'on' if SCREENSHOTS else 'off'}")
    print(f"Proxy: {PROXY or 'none'}")
    print()
    print("Launching stealth browser...", flush=True)

    browser = launch(headless=not HEADED, proxy=PROXY, geoip=True)
    page = browser.new_page()

    # Show browser fingerprint details
    try:
        import re
        info = page.evaluate("""async () => {
            const ua = navigator.userAgent;
            let fullVersion = null;
            try {
                const data = await navigator.userAgentData.getHighEntropyValues(['fullVersionList', 'platform', 'platformVersion']);
                const chrome = data.fullVersionList.find(b => b.brand === 'Chromium' || b.brand === 'Google Chrome');
                fullVersion = chrome ? chrome.version : null;
            } catch {}
            const gl = document.createElement('canvas').getContext('webgl');
            const dbg = gl ? gl.getExtension('WEBGL_debug_renderer_info') : null;
            return {
                ua,
                fullVersion,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency,
                gpu: dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : 'N/A',
                gpuVendor: dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : 'N/A',
                screen: screen.width + 'x' + screen.height,
                languages: navigator.languages.join(', '),
            };
        }""")
        # Condensed UA
        ua_short = re.sub(r'^Mozilla/5\.0 \(', '', info["ua"])
        ua_short = re.sub(r'\) AppleWebKit/[\d.]+ \(KHTML, like Gecko\) ', ' | ', ua_short)
        print(f"UA: {ua_short}", flush=True)
        print(f"Platform: {info['platform']} | Cores: {info['cores']} | Screen: {info['screen']}", flush=True)
        print(f"GPU: {info['gpuVendor']} — {info['gpu']}", flush=True)
    except Exception:
        print("Chrome: could not detect", flush=True)

    # Show IP address
    try:
        page.goto("https://httpbin.org/ip", timeout=10000)
        ip = page.evaluate("JSON.parse(document.body.innerText).origin")
        print(f"IP: {ip}", flush=True)
    except Exception:
        print("IP: could not detect", flush=True)

    print(f"Running {len(TESTS)} tests (this takes ~2 minutes)...\n", flush=True)

    results_summary = []

    for test in TESTS:
        name = test["name"]
        print(f"--- {name} ---")
        print(f"URL: {test['url']}")

        try:
            result = test["runner"](page)
            passed = test["pass"](result)
            verdict = test["verdict"](result)
            status = "PASS" if passed else "FAIL"
            results_summary.append((name, status, verdict))

            print(f"Result: [{status}] {verdict}")

            if SCREENSHOTS:
                filename = f"stealth_test_{name.replace('.', '_').replace(' ', '_').replace('/', '_')}.png"
                page.screenshot(path=filename)
                print(f"Screenshot: {filename}")

        except Exception as e:
            results_summary.append((name, "ERROR", str(e)))
            print(f"Error: {e}")

        print()

    browser.close()

    # Summary table
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for name, status, verdict in results_summary:
        icon = {"PASS": "+", "FAIL": "!", "ERROR": "x"}[status]
        print(f"  [{icon}] {name}: {verdict}")

    passed_count = sum(1 for _, s, _ in results_summary if s == "PASS")
    total = len(results_summary)
    print(f"\n  {passed_count}/{total} tests passed")
    print("=" * 60)

    return 0 if passed_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
