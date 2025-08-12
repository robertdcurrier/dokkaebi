#!/usr/bin/env python3
"""
DOKKAEBI FIRE GOBLIN CURSES CLI
A REBELLIOUSLY ELEGANT terminal interface that BURNS with the fury
of a thousand trading algorithms!

This is NOT your grandmother's terminal app - this is a FIRE GOBLIN
interface that updates in place with NO SCROLLING BULLSHIT!
"""

import curses
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# from .crypto_client import CryptoClient  # TODO: implement crypto client
# from .stock_client import StockClient  # TODO: implement stock client


class FireGoblinColors:
    """Color definitions for our BURNING interface"""
    
    # Main colors (curses color pairs)
    BURNING_ORANGE = 1  # Headers
    MOLTEN_GOLD = 2     # Highlights 
    DEEP_PURPLE = 3     # Backgrounds
    ELECTRIC_GREEN = 4  # Success
    BLOOD_RED = 5       # Errors
    WHITE_HOT = 6       # Important text
    FIRE_BORDER = 7     # Borders


class MenuItem:
    """A menu item that can BURN or be selected"""
    
    def __init__(self, key: str, label: str, action: str, description: str):
        self.key = key
        self.label = label
        self.action = action
        self.description = description


class FireGoblinCLI:
    """
    The main FIRE GOBLIN interface that BURNS through the terminal
    with REBELLIOUS ELEGANCE!
    """
    
    def __init__(self, stdscr=None):
        self.stdscr = stdscr
        self.height = 0
        self.width = 0
        self.current_menu = "main"
        self.selected_index = 0
        self.status_message = "^^^ DOKKAEBI FIRE GOBLIN READY TO BURN ^^^"
        # self.crypto_client = CryptoClient()  # TODO: implement
        # self.stock_client = StockClient()    # TODO: implement
        self.data_cache = {}
        self.animation_frame = 0
        self.spark_positions = []
        self.explosion_active = False
        self.explosion_frame = 0
        
        # Menu definitions
        self.menus = {
            "main": [
                MenuItem("1", "^^^ CRYPTO INFERNO", "crypto_menu", 
                        "Dive into the burning depths of cryptocurrency"),
                MenuItem("2", "/^\\ STOCK VOLCANO", "stock_menu",
                        "Erupt with traditional market fury"),
                MenuItem("3", ">>> PRICE LIGHTNING", "quick_prices",
                        "Instant price strikes like lightning"),
                MenuItem("4", "/^^\\ BULK MAGMA", "bulk_download",
                        "Download molten data in bulk"),
                MenuItem("5", "[*] GOBLIN SETTINGS", "settings",
                        "Configure your fire goblin powers"),
                MenuItem("q", "[X] ESCAPE HELL", "quit",
                        "Exit the burning realm")
            ],
            "crypto_menu": [
                MenuItem("1", "[$] BTC/ETH/SOL", "crypto_major",
                        "The big three burning coins"),
                MenuItem("2", "^^^ TOP 10 COINS", "crypto_top10",
                        "The hottest coins in the inferno"),
                MenuItem("3", ">>> CUSTOM SYMBOL", "crypto_custom",
                        "Enter your own burning symbol"),
                MenuItem("4", "[%] LIVE PRICES", "crypto_live",
                        "Watch prices burn in real-time"),
                MenuItem("b", "<-- BACK TO HELL", "main",
                        "Return to the main inferno")
            ],
            "stock_menu": [
                MenuItem("1", "^^^ FAANG FLAMES", "stock_faang",
                        "Facebook, Apple, Amazon, Netflix, Google"),
                MenuItem("2", "<>< DOW DIAMONDS", "stock_dow",
                        "Dow Jones burning bright"),
                MenuItem("3", ">>> S&P LIGHTNING", "stock_sp500",
                        "S&P 500 electric fury"),
                MenuItem("4", "[O] CUSTOM TICKER", "stock_custom",
                        "Your own burning ticker"),
                MenuItem("b", "<-- BACK TO HELL", "main",
                        "Return to the main inferno")
            ]
        }
    
    def init_colors(self):
        """Initialize the FIRE GOBLIN color scheme"""
        curses.start_color()
        curses.use_default_colors()
        
        # Define color pairs (foreground, background)
        curses.init_pair(FireGoblinColors.BURNING_ORANGE, 
                        curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(FireGoblinColors.MOLTEN_GOLD,
                        curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(FireGoblinColors.DEEP_PURPLE,
                        curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(FireGoblinColors.ELECTRIC_GREEN,
                        curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(FireGoblinColors.BLOOD_RED,
                        curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(FireGoblinColors.WHITE_HOT,
                        curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(FireGoblinColors.FIRE_BORDER,
                        curses.COLOR_YELLOW, curses.COLOR_RED)
    
    def draw_border_fire(self, y: int, x: int, height: int, width: int):
        """Draw a BURNING border around a section"""
        # Top and bottom
        for i in range(width):
            self.stdscr.addstr(y, x + i, "═", 
                             curses.color_pair(FireGoblinColors.BURNING_ORANGE))
            self.stdscr.addstr(y + height - 1, x + i, "═",
                             curses.color_pair(FireGoblinColors.BURNING_ORANGE))
        
        # Left and right
        for i in range(height):
            self.stdscr.addstr(y + i, x, "║",
                             curses.color_pair(FireGoblinColors.BURNING_ORANGE))
            self.stdscr.addstr(y + i, x + width - 1, "║",
                             curses.color_pair(FireGoblinColors.BURNING_ORANGE))
        
        # Corners
        self.stdscr.addstr(y, x, "╔",
                          curses.color_pair(FireGoblinColors.BURNING_ORANGE))
        self.stdscr.addstr(y, x + width - 1, "╗",
                          curses.color_pair(FireGoblinColors.BURNING_ORANGE))
        self.stdscr.addstr(y + height - 1, x, "╚",
                          curses.color_pair(FireGoblinColors.BURNING_ORANGE))
        self.stdscr.addstr(y + height - 1, x + width - 1, "╝",
                          curses.color_pair(FireGoblinColors.BURNING_ORANGE))
    
    def get_dokkaebi_ascii(self) -> List[str]:
        """Return EPIC DOKKAEBI fire goblin ASCII art"""
        return [
            "    ===============================================",
            "   ###        ^^^ DOKKAEBI FIRE GOBLIN ^^^        ###",
            "  ###               >>> MARKET DEMON <<<             ###",
            " ###                     /-\\                       ###",
            "###              /\\     /  \\     /\\                ###",
            "###             (@)   (  o_o  )   (@)              ###",
            "###              \\|     \\ ^^^ /     |/                ###",
            "###               |      \\_/      |                 ###",
            "###              /|\\      |      /|\\                ###",
            "###             ^^^~~~    /-\\    ~~~^^^               ###",
            " ###        STEALING WEALTH * BURNING MARKETS      ###",
            "  ###              >>> CHAOS UNLEASHED <<<            ###",
            "   #################################################",
        ]

    def get_flame_border_chars(self, frame: int) -> Tuple[str, str, str]:
        """Get animated flame border characters"""
        flame_frames = [
            ("^", "#", "~"),
            ("#", "^", "*"),
            ("~", "#", "^"),
            ("*", "~", "#"),
        ]
        return flame_frames[frame % len(flame_frames)]

    def draw_animated_flames(self, frame: int):
        """Draw animated flames around the interface"""
        flame1, flame2, flame3 = self.get_flame_border_chars(frame)
        
        # Top flame border
        flame_pattern = f"{flame1}{flame2}{flame3}" * ((self.width // 3) + 1)
        self.stdscr.addstr(0, 0, flame_pattern[:self.width],
                          curses.color_pair(FireGoblinColors.BURNING_ORANGE) | curses.A_BOLD)
        
        # Bottom flame border
        self.stdscr.addstr(self.height - 1, 0, flame_pattern[:self.width],
                          curses.color_pair(FireGoblinColors.BURNING_ORANGE) | curses.A_BOLD)

    def draw_header(self):
        """Draw the EPIC DOKKAEBI header that burns retinas"""
        ascii_art = self.get_dokkaebi_ascii()
        
        # Calculate starting position to center the ASCII art
        start_y = 1
        start_x = max(0, (self.width - len(ascii_art[0])) // 2)
        
        # Draw the DOKKAEBI ASCII art
        for i, line in enumerate(ascii_art):
            if start_y + i < self.height - 5:  # Make sure we don't overflow
                # Alternate colors for epic effect
                if i % 3 == 0:
                    color = curses.color_pair(FireGoblinColors.BURNING_ORANGE) | curses.A_BOLD
                elif i % 3 == 1:
                    color = curses.color_pair(FireGoblinColors.MOLTEN_GOLD) | curses.A_BOLD
                else:
                    color = curses.color_pair(FireGoblinColors.BLOOD_RED) | curses.A_BOLD
                
                # Truncate line if too wide
                display_line = line[:self.width - start_x] if len(line) > self.width - start_x else line
                
                try:
                    self.stdscr.addstr(start_y + i, start_x, display_line, color)
                except curses.error:
                    pass  # Ignore if we can't draw (terminal too small)

    def generate_spark_effect(self):
        """Generate sparks for navigation effects"""
        import random
        sparks = [">", "*", "+", "x", "o", "#", "^", "v", "<"]
        for _ in range(5):
            x = random.randint(5, self.width - 5)
            y = random.randint(15, self.height - 5)
            spark_char = random.choice(sparks)
            self.spark_positions.append((x, y, spark_char, 10))  # x, y, char, lifetime

    def draw_sparks(self):
        """Draw spark effects"""
        remaining_sparks = []
        for x, y, char, lifetime in self.spark_positions:
            if lifetime > 0 and 0 <= x < self.width and 0 <= y < self.height:
                try:
                    color = curses.color_pair(FireGoblinColors.MOLTEN_GOLD) | curses.A_BOLD
                    self.stdscr.addstr(y, x, char, color)
                    remaining_sparks.append((x, y, char, lifetime - 1))
                except curses.error:
                    pass
        self.spark_positions = remaining_sparks

    def trigger_explosion_effect(self):
        """Trigger explosion when selecting items"""
        self.explosion_active = True
        self.explosion_frame = 0

    def draw_explosion(self, center_y: int, center_x: int):
        """Draw explosion effect at selection"""
        if not self.explosion_active:
            return
        
        explosion_patterns = [
            ["*"],
            ["/-\\", "*", "/-\\"],
            ["^", "/-\\", "*", "/-\\", "^"],
            [">", "^", "/-\\", "*", "/-\\", "^", "<"],
            ["+", ">", "^", "/-\\", "*", "/-\\", "^", "<", "+"],
            ["", "", "", "", "", "", "", "", ""],  # Fade out
        ]
        
        if self.explosion_frame < len(explosion_patterns):
            pattern = explosion_patterns[self.explosion_frame]
            start_x = center_x - len(pattern) // 2
            
            for i, char in enumerate(pattern):
                if char and 0 <= start_x + i < self.width and 0 <= center_y < self.height:
                    try:
                        color = curses.color_pair(FireGoblinColors.BLOOD_RED) | curses.A_BOLD
                        self.stdscr.addstr(center_y, start_x + i, char, color)
                    except curses.error:
                        pass
            
            self.explosion_frame += 1
        else:
            self.explosion_active = False

    def get_goblin_status_message(self, action: str) -> str:
        """Return INTENSE goblin status messages"""
        messages = {
            "loading": [
                "💀 SUMMONING DATA FROM THE DEPTHS OF HELL... 💀",
                "🔥 MELTING SERVERS TO EXTRACT PRICES... 🔥",
                "⚡ CHANNELING THE FURY OF MARKET DEMONS... ⚡",
                "👹 DOKKAEBI FEASTING ON MARKET DATA... 👹",
                "🌋 ERUPTING WITH MOLTEN INFORMATION... 🌋"
            ],
            "success": [
                "💀 TARGET OBLITERATED! DATA CONSUMED! 💀",
                "🔥 MARKET BURNED TO ASHES! SUCCESS! 🔥",
                "⚡ LIGHTNING STRIKE SUCCESSFUL! ⚡",
                "👹 DOKKAEBI HAS STOLEN THE WEALTH! 👹",
                "🌋 VOLCANIC ERUPTION OF SUCCESS! 🌋"
            ],
            "navigation": [
                "🔥 BURNING THROUGH MENU PATHS... 🔥",
                "⚡ SPARKS FLY AS YOU NAVIGATE... ⚡",
                "💀 DEATH APPROACHES YOUR SELECTION... 💀",
                "👹 GOBLIN EYES TRACK YOUR MOVEMENT... 👹"
            ],
            "error": [
                "💀 THE ABYSS STARES BACK! ERROR DETECTED! 💀",
                "🔥 FLAMES OF FAILURE CONSUME ALL! 🔥",
                "⚡ LIGHTNING BOLT OF DESTRUCTION! ⚡",
                "👹 DOKKAEBI LAUGHS AT YOUR MISERY! 👹"
            ]
        }
        
        import random
        return random.choice(messages.get(action, messages["navigation"]))
    
    def draw_menu(self):
        """Draw the current menu with FIRE GOBLIN styling"""
        menu_items = self.menus[self.current_menu]
        start_y = 16  # Move menu down to accommodate ASCII art
        
        for i, item in enumerate(menu_items):
            y = start_y + i * 2
            if y >= self.height - 4:  # Don't overflow
                break
                
            # Determine colors based on selection
            if i == self.selected_index:
                key_color = curses.color_pair(FireGoblinColors.WHITE_HOT)
                label_color = (curses.color_pair(FireGoblinColors.ELECTRIC_GREEN) |
                              curses.A_BOLD | curses.A_REVERSE)
                desc_color = curses.color_pair(FireGoblinColors.MOLTEN_GOLD)
                prefix = "🔥► "
                # Draw explosion effect for selected item
                self.draw_explosion(y, 2)
            else:
                key_color = curses.color_pair(FireGoblinColors.DEEP_PURPLE)
                label_color = curses.color_pair(FireGoblinColors.BURNING_ORANGE)
                desc_color = curses.color_pair(FireGoblinColors.WHITE_HOT)
                prefix = "   "
            
            # Draw menu item
            self.stdscr.addstr(y, 4, f"{prefix}[{item.key}]",
                              key_color | curses.A_BOLD)
            self.stdscr.addstr(y, 12, item.label,
                              label_color | curses.A_BOLD)
            
            # Draw description on next line
            if len(item.description) > 0:
                desc_x = 15
                max_desc_width = self.width - desc_x - 4
                if len(item.description) > max_desc_width:
                    desc = item.description[:max_desc_width - 3] + "..."
                else:
                    desc = item.description
                self.stdscr.addstr(y + 1, desc_x, desc, desc_color)
    
    def draw_status_bar(self):
        """Draw the bottom status bar with BURNING intensity"""
        status_y = self.height - 2
        
        # Clear status line
        self.stdscr.addstr(status_y, 0, " " * self.width,
                          curses.color_pair(FireGoblinColors.DEEP_PURPLE))
        
        # Draw status message
        if len(self.status_message) > self.width - 4:
            message = self.status_message[:self.width - 7] + "..."
        else:
            message = self.status_message
            
        self.stdscr.addstr(status_y, 2, message,
                          curses.color_pair(FireGoblinColors.MOLTEN_GOLD) |
                          curses.A_BOLD)
        
        # Draw controls on the right
        controls = "↑↓:Navigate | Enter:Select | ESC:Back | q:Quit"
        if len(controls) < self.width - len(message) - 8:
            controls_x = self.width - len(controls) - 2
            self.stdscr.addstr(status_y, controls_x, controls,
                              curses.color_pair(FireGoblinColors.WHITE_HOT))
    
    def draw_data_panel(self, data: Dict):
        """Draw real-time data with ELECTRIC intensity"""
        panel_start_y = 6
        panel_height = self.height - 10
        panel_width = self.width - 8
        
        # Draw border
        self.draw_border_fire(panel_start_y, 4, panel_height, panel_width)
        
        # Draw data inside
        y = panel_start_y + 2
        for key, value in data.items():
            if y >= panel_start_y + panel_height - 2:
                break
                
            # Format the data line
            line = f"{key}: {value}"
            if len(line) > panel_width - 4:
                line = line[:panel_width - 7] + "..."
                
            self.stdscr.addstr(y, 6, line,
                              curses.color_pair(FireGoblinColors.ELECTRIC_GREEN))
            y += 1
    
    def handle_key(self, key: int) -> bool:
        """Handle keyboard input with FIRE GOBLIN responsiveness"""
        menu_items = self.menus[self.current_menu]
        
        if key == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(menu_items)
            self.status_message = self.get_goblin_status_message("navigation")
            self.generate_spark_effect()
            
        elif key == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(menu_items)
            self.status_message = self.get_goblin_status_message("navigation")
            self.generate_spark_effect()
            
        elif key in (curses.KEY_ENTER, 10, 13):
            self.trigger_explosion_effect()
            return self.execute_action(menu_items[self.selected_index].action)
            
        elif key == 27:  # ESC
            if self.current_menu != "main":
                self.current_menu = "main"
                self.selected_index = 0
                self.status_message = "⬅️ ESCAPED BACK TO MAIN HELL - COWARD!"
                self.generate_spark_effect()
            else:
                return False  # Quit
                
        elif key == ord('q') or key == ord('Q'):
            self.status_message = "💀 DOKKAEBI RELEASES YOU... FOR NOW... 💀"
            return False
            
        else:
            # Check for direct key selection
            key_char = chr(key) if 32 <= key <= 126 else None
            if key_char:
                for i, item in enumerate(menu_items):
                    if item.key.lower() == key_char.lower():
                        self.selected_index = i
                        self.trigger_explosion_effect()
                        self.status_message = self.get_goblin_status_message("success")
                        return self.execute_action(item.action)
        
        return True
    
    def execute_action(self, action: str) -> bool:
        """Execute the selected action with GOBLIN FURY"""
        if action == "quit":
            self.status_message = "💀 DOKKAEBI DEVOURS YOUR SOUL ON EXIT! 💀"
            return False
            
        elif action in self.menus:
            self.current_menu = action
            self.selected_index = 0
            self.status_message = f"🔥 ENTERED {action.upper()} REALM OF CHAOS 🔥"
            self.generate_spark_effect()
            
        elif action == "crypto_major":
            self.status_message = self.get_goblin_status_message("loading")
            # TODO: Implement crypto major fetch
            
        elif action == "crypto_live":
            self.status_message = "⚡ LIVE PRICES MELTING YOUR EYEBALLS ⚡"
            # TODO: Implement live price updates
            
        elif action == "stock_faang":
            self.status_message = self.get_goblin_status_message("loading")
            # TODO: Implement FAANG fetch
            
        elif action == "crypto_top10":
            self.status_message = "🌋 SUMMONING THE TOP 10 DEMONS OF CRYPTO 🌋"
            
        elif action == "bulk_download":
            self.status_message = "💀 BULK HARVEST OF MARKET SOULS INITIATED 💀"
            
        elif action == "settings":
            self.status_message = "⚙️ CONFIGURING GOBLIN POWERS AND DARK MAGIC ⚙️"
            
        else:
            self.status_message = f"🚨 {action.upper()} RITUAL NOT YET SUMMONED! 🚨"
        
        return True
    
    def run(self, stdscr):
        """Main FIRE GOBLIN event loop"""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # Initialize the BURNING interface
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(50)  # 50ms timeout for smooth animations
        
        self.init_colors()
        
        running = True
        while running:
            # Increment animation frame
            self.animation_frame += 1
            
            # Clear screen with DEEP PURPLE background
            stdscr.clear()
            stdscr.bkgd(' ', curses.color_pair(FireGoblinColors.DEEP_PURPLE))
            
            # Draw animated flame borders
            self.draw_animated_flames(self.animation_frame)
            
            # Draw all interface elements
            self.draw_header()
            self.draw_menu()
            self.draw_status_bar()
            
            # Draw visual effects
            self.draw_sparks()
            
            # Add pulsing effect to status message every 20 frames
            if self.animation_frame % 20 == 0:
                # Add some random sparks for ambient effect
                if len(self.spark_positions) < 3:
                    self.generate_spark_effect()
            
            # Refresh the BURNING display
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            if key != -1:  # Key was pressed
                running = self.handle_key(key)
            
            # Small delay to prevent CPU BURNING while maintaining smooth animation
            time.sleep(0.05)


def main():
    """
    Launch the FIRE GOBLIN CURSES CLI!
    
    This is where the REBELLIOUS ELEGANCE begins!
    """
    try:
        cli = FireGoblinCLI()
        curses.wrapper(cli.run)
        print("🔥 FIRE GOBLIN SAYS GOODBYE! MAY YOUR TRADES BURN BRIGHT! 🔥")
        
    except KeyboardInterrupt:
        print("\n🔥 FIRE GOBLIN INTERRUPTED! BURNING OUT... 🔥")
        
    except Exception as e:
        print(f"💀 FIRE GOBLIN CRASHED AND BURNED: {e} 💀")
        raise


if __name__ == "__main__":
    main()