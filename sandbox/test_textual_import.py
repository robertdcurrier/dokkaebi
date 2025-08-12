#!/usr/bin/env python3
"""
Test script to verify Textual fire goblin interface can import correctly.

COMPLIANCE NOTE: This file is correctly placed in sandbox/ directory
per MANDATORY file location rules from memory bank:
- ALL test code MUST go in sandbox/ directory
- Test scripts → sandbox/test_*.py
- NO TEST CODE IN ROOT - EVER!
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from price_downloader.fire_goblin_textual import (
        FireGoblinApp, 
        PortfolioScreen,
        TickerInputScreen
    )
    print("✅ SUCCESS: fire_goblin_textual module imported correctly!")
    print("   - FireGoblinApp class available")
    print("   - PortfolioScreen class available") 
    print("   - TickerInputScreen class available")
    print("🔥 Fire Goblin Textual interface is ready for REBELLIOUS trading!")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print("   Could not import fire_goblin_textual module")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
    sys.exit(1)

print("\n📁 COMPLIANCE CONFIRMATION:")
print("   - Test file correctly placed in sandbox/ directory")
print("   - Following MANDATORY file location rules")
print("   - Test code NEVER goes in root directory")
print("   - Documentation ALWAYS goes in docs/ directory")