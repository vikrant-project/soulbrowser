"""Soul Browser CLI entry point."""

import argparse
import sys
import json

from .download import ensure_binary, clear_cache, binary_info, check_for_update
from ._version import __version__, SOUL_BROWSER_CODENAME


def main():
    parser = argparse.ArgumentParser(
        prog="soulbrowser",
        description="Soul Browser — The Ultimate Privacy-First Stealth Browser"
    )
    parser.add_argument("--version", action="version", version=f"Soul Browser {__version__} ({SOUL_BROWSER_CODENAME})")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install command
    subparsers.add_parser("install", help="Download and install the Chromium binary")
    
    # Info command
    subparsers.add_parser("info", help="Show installation information")
    
    # Update command
    subparsers.add_parser("update", help="Check for and download updates")
    
    # Clear cache command
    subparsers.add_parser("clear-cache", help="Remove cached binaries")
    
    args = parser.parse_args()
    
    if args.command == "install":
        print("Soul Browser — Installing Chromium binary...")
        try:
            path = ensure_binary()
            print(f"✓ Binary installed at: {path}")
        except Exception as e:
            print(f"✗ Installation failed: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "info":
        info = binary_info()
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║              SOUL BROWSER INFORMATION                 ║")
        print("╠══════════════════════════════════════════════════════╣")
        print(f"║  Soul Browser Version: {info['soul_browser_version']:<27} ║")
        print(f"║  Chromium Version:     {info['chromium_version']:<27} ║")
        print(f"║  Platform:             {info['platform']:<27} ║")
        print(f"║  Installed:            {'Yes' if info['installed'] else 'No':<27} ║")
        print("╠══════════════════════════════════════════════════════╣")
        print(f"║  Binary Path:                                        ║")
        print(f"║    {info['binary_path'][:50]:<50} ║")
        print("╚══════════════════════════════════════════════════════╝\n")
    
    elif args.command == "update":
        print("Soul Browser — Checking for updates...")
        new_version = check_for_update()
        if new_version:
            print(f"✓ Updated to Chromium {new_version}")
        else:
            print("✓ Already up to date")
    
    elif args.command == "clear-cache":
        print("Soul Browser — Clearing cache...")
        clear_cache()
        print("✓ Cache cleared")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
