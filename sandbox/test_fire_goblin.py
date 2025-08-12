#!/usr/bin/env python3
"""
Quick test script to launch the DOKKAEBI FIRE GOBLIN interface
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.price_downloader.curses_cli import main

if __name__ == "__main__":
    print("🔥 SUMMONING THE DOKKAEBI FIRE GOBLIN... 🔥")
    main()