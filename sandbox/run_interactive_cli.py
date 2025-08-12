#!/usr/bin/env python3
"""
DOKKAEBI Interactive CLI Launcher

Quick launcher for the interactive price downloader.
Run this script to start the beautiful UI!

Usage:
    python run_interactive_cli.py
    python run_interactive_cli.py --cache-path custom/path.duckdb
"""

import sys
import os
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from price_downloader.interactive_cli import main

if __name__ == '__main__':
    main()