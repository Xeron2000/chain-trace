#!/usr/bin/env python3
"""
Twitter Data Fetcher with Auto-Camofox

Wrapper around x-tweet-fetcher that automatically starts Camofox when needed.
"""

import sys
import os
from pathlib import Path

# Add x-tweet-fetcher to path
X_FETCHER_PATH = Path.home() / ".claude/skills/x-tweet-fetcher/scripts"
if not X_FETCHER_PATH.exists():
    X_FETCHER_PATH = Path.home() / ".agents/skills/x-tweet-fetcher/scripts"

if X_FETCHER_PATH.exists():
    sys.path.insert(0, str(X_FETCHER_PATH))

from camofox_starter import ensure_camofox


def needs_camofox(args: list) -> bool:
    """Check if the command needs Camofox"""
    # Needs Camofox if:
    # - --user (user timeline)
    # - --replies (fetch replies)
    # - --article (X articles)
    return any(arg in args for arg in ['--user', '--replies', '-r', '--article', '-a'])


def main():
    args = sys.argv[1:]

    # Check if Camofox is needed
    if needs_camofox(args):
        print("[Twitter Fetcher] This operation requires Camofox browser service")

        if not ensure_camofox():
            print("\n❌ Failed to start Camofox. Advanced features unavailable.")
            print("\nAlternatives:")
            print("  1. Install Node.js: https://nodejs.org/")
            print("  2. Use basic features only (single tweet without --replies)")
            sys.exit(1)

        print()  # Blank line for readability

    # Import and run fetch_tweet
    try:
        if not X_FETCHER_PATH.exists():
            print("❌ x-tweet-fetcher not found")
            print("Install: https://github.com/ythx-101/x-tweet-fetcher")
            sys.exit(1)

        # Run fetch_tweet.py
        import subprocess
        fetch_script = X_FETCHER_PATH / "fetch_tweet.py"

        result = subprocess.run(
            [sys.executable, str(fetch_script)] + args,
            check=False
        )

        sys.exit(result.returncode)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
