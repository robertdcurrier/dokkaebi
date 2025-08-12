#!/usr/bin/env python3
"""
DOKKAEBI FIRE GOBLIN - Ultimate Textual Interface Launcher

Quick launcher for the ULTIMATE Fire Goblin from the project root.
This is MAXIMUM REBELLIOUS ELEGANCE with modern Textual power!
"""

import os
import sys
from pathlib import Path

# Add parent directory (project root) to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set demo environment if no real keys
if not os.getenv('ALPACA_API_KEY'):
    os.environ['ALPACA_API_KEY'] = 'demo_key'
    os.environ['ALPACA_API_SECRET'] = 'demo_secret'

# Import and run
from src.price_downloader.fire_goblin_textual import run_ultimate_fire_goblin

if __name__ == "__main__":
    print("🔥💀 LAUNCHING ULTIMATE DOKKAEBI FIRE GOBLIN 💀🔥")
    run_ultimate_fire_goblin()
