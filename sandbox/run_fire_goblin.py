#!/usr/bin/env python3
"""
Launch the FIRE GOBLIN interface!
"""
import curses
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run the fire goblin interface."""
    stdscr = None
    try:
        # Import here to avoid import errors
        from src.price_downloader.curses_cli import FireGoblinCLI
        
        # Initialize curses
        stdscr = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        curses.curs_set(0)  # Hide cursor
        
        # Create and run interface
        interface = FireGoblinCLI()
        interface.run(stdscr)
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        # Clean up curses first
        if stdscr:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()
        print(f"Error: {e}")
        print("Full traceback:")
        traceback.print_exc()
    finally:
        # Clean up curses
        if stdscr:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()
        print("\n🔥 DOKKAEBI FIRE GOBLIN INTERFACE TERMINATED 🔥")

if __name__ == "__main__":
    main()