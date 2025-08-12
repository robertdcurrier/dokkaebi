#!/usr/bin/env python3
"""
Simple test to see if curses is working at all.
"""
import curses
import time

def main(stdscr):
    """Simple curses test."""
    # Clear screen
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Display some text
    stdscr.addstr(0, 0, "🔥 DOKKAEBI FIRE GOBLIN TEST 🔥")
    stdscr.addstr(2, 0, f"Screen size: {width}x{height}")
    stdscr.addstr(4, 0, "Press any key to continue...")
    
    # Refresh the screen
    stdscr.refresh()
    
    # Wait for user input
    stdscr.getch()
    
    # Show countdown
    for i in range(3, 0, -1):
        stdscr.clear()
        stdscr.addstr(height//2, width//2 - 10, f"Exiting in {i}...")
        stdscr.refresh()
        time.sleep(1)

if __name__ == "__main__":
    print("Starting curses test...")
    try:
        curses.wrapper(main)
        print("Curses test completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()