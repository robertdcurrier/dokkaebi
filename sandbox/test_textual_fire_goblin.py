#!/usr/bin/env python3
"""
Test script for the DOKKAEBI FIRE GOBLIN Textual CLI

This will launch the REBELLIOUSLY ELEGANT terminal interface
and make sure it burns properly with modern Textual power!
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for testing (use dummy values if no real keys)
if not os.getenv('ALPACA_API_KEY'):
    print("⚠️  WARNING: No ALPACA_API_KEY set - some features will be limited")
    print("Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables for full functionality")

# Import and run the FIRE GOBLIN
try:
    from src.price_downloader.textual_cli import run_fire_goblin_cli
    
    print("🔥 LAUNCHING DOKKAEBI FIRE GOBLIN TEXTUAL CLI 🔥")
    print("🚀 PREPARE FOR REBELLIOUSLY ELEGANT TERMINAL DOMINATION! 🚀")
    print()
    
    run_fire_goblin_cli()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory with the virtual environment activated")
    
except Exception as e:
    print(f"💀 FIRE GOBLIN EXPLODED: {e}")
    raise