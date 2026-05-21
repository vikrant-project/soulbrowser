#!/bin/bash
# agent-browser + SoulBrowser: AI browser agent with stealth fingerprints.
#
# agent-browser is a Node.js CLI for browser automation with session management.
# SoulBrowser provides the stealth Chromium binary.
#
# Requires: npm install -g agent-browser
#           pip install soulbrowser (to auto-download the binary)
#
# Note: agent-browser launches Chrome itself via env vars — it can't connect
# to an existing browser via CDP. So we pass the binary path and stealth args directly.

# Get SoulBrowser binary path (auto-downloads if needed)
BINARY_PATH=$(python3 -c "from soulbrowser.download import ensure_binary; print(ensure_binary())")

# Get stealth args from our wrapper (comma-separated for agent-browser)
STEALTH_ARGS=$(python3 -c "from soulbrowser.config import get_default_stealth_args; print(','.join(get_default_stealth_args()))")

# Point agent-browser at SoulBrowser
export AGENT_BROWSER_EXECUTABLE_PATH="$BINARY_PATH"
export AGENT_BROWSER_ARGS="$STEALTH_ARGS"

# Open a page
agent-browser --session stealth-test open "https://example.com"

# Get page title
agent-browser --session stealth-test eval "document.title"

# Check stealth
agent-browser --session stealth-test eval "JSON.stringify({webdriver: navigator.webdriver, plugins: navigator.plugins.length, platform: navigator.platform})"
