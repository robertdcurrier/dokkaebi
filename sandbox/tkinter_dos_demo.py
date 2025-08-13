#!/usr/bin/env python3
"""
DOS-Style Tkinter GUI Demo
==========================

FUCK TEXTUAL - This actually works!

Features:
- REAL working dropdown menus
- DOS blue/white color scheme
- Two scrollable text areas
- Function key bindings that ACTUALLY WORK
- Status bar at bottom
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random

# DOS Color Palette
DOS_BLUE = '#0000AA'
DOS_LIGHT_BLUE = '#5555FF'
DOS_WHITE = '#FFFFFF'
DOS_YELLOW = '#FFFF00'
DOS_BLACK = '#000000'
DOS_GRAY = '#AAAAAA'
DOS_CYAN = '#00FFFF'


class DOSApp(tk.Tk):
    """DOS-style GUI application using Tkinter"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("DOKKAEBI PRICE DATA SYSTEM - [TKINTER EDITION]")
        self.geometry("1024x768")
        self.configure(bg=DOS_BLUE)
        
        # DOS-style fixed font
        self.dos_font = ('Courier', 10)
        self.dos_font_bold = ('Courier', 10, 'bold')
        
        # Create the GUI components
        self.create_menu_bar()  # System menu bar (for Mac)
        self.create_custom_menu_bar()  # Our custom menu bar
        self.create_main_area()
        self.create_simple_status_bar()  # Simple status line only
        self.setup_key_bindings()
        
        # Populate with sample data
        self.populate_sample_data()
    
    def create_custom_menu_bar(self):
        """Create a Windows-style menu bar as buttons in a frame"""
        menu_frame = tk.Frame(self, bg=DOS_WHITE, height=25)
        menu_frame.pack(side=tk.TOP, fill=tk.X)
        menu_frame.pack_propagate(False)
        
        # Menu buttons that look like DOS menu items
        menus = ["File", "Edit", "View", "Download", "Help"]
        
        for menu_name in menus:
            btn = tk.Button(menu_frame, 
                          text=f" {menu_name} ",
                          bg=DOS_WHITE, 
                          fg=DOS_BLUE,
                          font=self.dos_font,
                          bd=0,
                          activebackground=DOS_BLUE,
                          activeforeground=DOS_WHITE,
                          command=lambda m=menu_name: self.show_menu_dropdown(m))
            btn.pack(side=tk.LEFT, padx=2)
        
    def show_menu_dropdown(self, menu_name):
        """Show dropdown for clicked menu"""
        self.update_status(f"{menu_name} menu clicked")
        # For now, just show status
        # Could create popup menus here
        
    def create_menu_bar(self):
        """Create WORKING dropdown menus - fuck yeah!"""
        menubar = tk.Menu(self, bg=DOS_WHITE, fg=DOS_BLUE, 
                         activebackground=DOS_BLUE, activeforeground=DOS_WHITE)
        
        # File menu - IT ACTUALLY WORKS!
        file_menu = tk.Menu(menubar, tearoff=0, bg=DOS_WHITE, fg=DOS_BLUE,
                          activebackground=DOS_BLUE, activeforeground=DOS_WHITE)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", 
                            command=self.file_open)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", 
                            command=self.file_save)
        file_menu.add_command(label="Save As...", command=self.file_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", 
                            command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu, underline=0)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=DOS_WHITE, fg=DOS_BLUE,
                          activebackground=DOS_BLUE, activeforeground=DOS_WHITE)
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V")
        menubar.add_cascade(label="Edit", menu=edit_menu, underline=0)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=DOS_WHITE, fg=DOS_BLUE,
                          activebackground=DOS_BLUE, activeforeground=DOS_WHITE)
        view_menu.add_command(label="Refresh", accelerator="F5", 
                            command=self.refresh_data)
        view_menu.add_command(label="Clear", command=self.clear_all)
        menubar.add_cascade(label="View", menu=view_menu, underline=0)
        
        # Download menu
        download_menu = tk.Menu(menubar, tearoff=0, bg=DOS_WHITE, fg=DOS_BLUE,
                              activebackground=DOS_BLUE, activeforeground=DOS_WHITE)
        download_menu.add_command(label="Download Watchlist", 
                                command=self.download_watchlist)
        download_menu.add_command(label="Download Custom...", 
                                command=self.download_custom)
        download_menu.add_separator()
        download_menu.add_command(label="View Cache", command=self.view_cache)
        menubar.add_cascade(label="Download", menu=download_menu, underline=0)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=DOS_WHITE, fg=DOS_BLUE,
                          activebackground=DOS_BLUE, activeforeground=DOS_WHITE)
        help_menu.add_command(label="Help Topics", accelerator="F1", 
                            command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu, underline=0)
        
        self.config(menu=menubar)
        
    def create_main_area(self):
        """Create the main content area with two scrollable text windows"""
        # Main container frame
        main_frame = tk.Frame(self, bg=DOS_BLUE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Watchlist/Symbols
        left_frame = tk.LabelFrame(main_frame, text=" WATCHLIST ", 
                                  bg=DOS_BLUE, fg=DOS_WHITE,
                                  font=self.dos_font_bold)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.left_text = scrolledtext.ScrolledText(
            left_frame, 
            width=40, 
            height=30,
            bg=DOS_BLACK,
            fg=DOS_WHITE,
            font=self.dos_font,
            insertbackground=DOS_YELLOW,
            selectbackground=DOS_YELLOW,
            selectforeground=DOS_BLACK
        )
        self.left_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Price Data
        right_frame = tk.LabelFrame(main_frame, text=" PRICE DATA ", 
                                   bg=DOS_BLUE, fg=DOS_WHITE,
                                   font=self.dos_font_bold)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.right_text = scrolledtext.ScrolledText(
            right_frame,
            width=60,
            height=30,
            bg=DOS_BLACK,
            fg=DOS_WHITE,
            font=self.dos_font,
            insertbackground=DOS_YELLOW,
            selectbackground=DOS_YELLOW,
            selectforeground=DOS_BLACK
        )
        self.right_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_simple_status_bar(self):
        """Create simple status bar without function keys"""
        status_frame = tk.Frame(self, bg=DOS_WHITE, height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        # Just the status message
        self.status_msg = tk.Label(status_frame, 
                                  text="DOKKAEBI Ready - Press letter keys for menus (f, e, v, d, h)",
                                  bg=DOS_WHITE, fg=DOS_BLUE,
                                  font=self.dos_font)
        self.status_msg.pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        """Create DOS-style status bar with function key hints"""
        # Status frame
        status_frame = tk.Frame(self, bg=DOS_WHITE, height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        # Function key labels
        keys = [
            ("F1", "Help"),
            ("F2", "Save"),
            ("F3", "Load"),
            ("F4", "Exit"),
            ("F5", "Refresh"),
            ("F9", "Download"),
            ("F10", "Menu")
        ]
        
        for key, label in keys:
            key_label = tk.Label(status_frame, 
                                text=f" {key}={label} ",
                                bg=DOS_BLACK, fg=DOS_WHITE,
                                font=self.dos_font)
            key_label.pack(side=tk.LEFT, padx=1)
        
        # Status message on the right
        self.status_msg = tk.Label(status_frame, 
                                  text="Ready",
                                  bg=DOS_WHITE, fg=DOS_BLUE,
                                  font=self.dos_font)
        self.status_msg.pack(side=tk.RIGHT, padx=5)
        
    def setup_key_bindings(self):
        """Setup keyboard shortcuts - Mac-friendly version!"""
        self.bind('<F1>', lambda e: self.show_help())
        self.bind('<F2>', lambda e: self.file_save())
        self.bind('<F3>', lambda e: self.file_open())
        self.bind('<F4>', lambda e: self.quit())
        self.bind('<F5>', lambda e: self.refresh_data())
        self.bind('<F9>', lambda e: self.download_watchlist())
        self.bind('<F10>', lambda e: self.focus_menu())
        
        # Mac-friendly: Option key (Alt on PC)
        self.bind('<Option-f>', lambda e: self.show_file_menu())
        self.bind('<Option-e>', lambda e: self.show_edit_menu())
        self.bind('<Option-v>', lambda e: self.show_view_menu())
        self.bind('<Option-d>', lambda e: self.show_download_menu())
        self.bind('<Option-h>', lambda e: self.show_help_menu())
        
        # Also bind Cmd+key for Mac users
        self.bind('<Command-o>', lambda e: self.file_open())
        self.bind('<Command-s>', lambda e: self.file_save())
        self.bind('<Command-q>', lambda e: self.quit())
        
        # Simple letter keys for menus (fuck it, make it easy)
        self.bind('f', lambda e: self.show_file_menu())
        self.bind('e', lambda e: self.show_edit_menu())
        self.bind('v', lambda e: self.show_view_menu())
        self.bind('d', lambda e: self.show_download_menu())
        self.bind('h', lambda e: self.show_help_menu())
        
    def populate_sample_data(self):
        """Add sample data to the text areas"""
        # Watchlist symbols
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA",
                  "AMD", "INTC", "NFLX", "DIS", "PYPL", "SQ", "SHOP",
                  "COIN", "HOOD", "PLTR", "SOFI", "RIVN", "LCID",
                  "GME", "AMC", "BB", "NOK", "BBBY", "WISH", "CLOV",
                  "SPCE", "TLRY", "SNDL", "DOGE"]
        
        self.left_text.insert(tk.END, "═══ WATCHLIST SYMBOLS ═══\n\n")
        for symbol in symbols:
            self.left_text.insert(tk.END, f"  {symbol}\n")
        
        # Price data
        self.right_text.insert(tk.END, "═══ MARKET DATA ═══\n\n")
        self.right_text.insert(tk.END, "Symbol  Price    Change  Volume\n")
        self.right_text.insert(tk.END, "──────  ───────  ──────  ──────────\n")
        
        for symbol in symbols[:10]:
            price = random.uniform(10, 500)
            change = random.uniform(-5, 5)
            volume = random.randint(1000000, 50000000)
            color_tag = "green" if change > 0 else "red"
            
            line = f"{symbol:<6}  ${price:>7.2f}  {change:>+6.2f}%  {volume:>10,}\n"
            self.right_text.insert(tk.END, line)
        
        # Configure color tags
        self.right_text.tag_config("green", foreground=DOS_CYAN)
        self.right_text.tag_config("red", foreground=DOS_YELLOW)
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_msg.config(text=message)
        self.after(3000, lambda: self.status_msg.config(text="Ready"))
        
    # Menu command implementations
    def file_open(self):
        self.update_status("Open file...")
        # In real app, use tkinter.filedialog
        
    def file_save(self):
        self.update_status("Saving...")
        
    def file_save_as(self):
        self.update_status("Save as...")
        
    def refresh_data(self):
        self.update_status("Refreshing data...")
        # Add new random data
        self.right_text.insert(tk.END, f"\nRefreshed at {tk.StringVar()}\n")
        
    def clear_all(self):
        self.left_text.delete(1.0, tk.END)
        self.right_text.delete(1.0, tk.END)
        self.update_status("Cleared")
        
    def download_watchlist(self):
        self.update_status("Downloading watchlist...")
        self.right_text.insert(tk.END, "\n>>> DOWNLOADING WATCHLIST...\n")
        
    def download_custom(self):
        # This could open a dialog
        self.update_status("Custom download...")
        
    def view_cache(self):
        self.update_status("Viewing cache...")
        
    def show_help(self):
        messagebox.showinfo("Help", 
                          "DOKKAEBI Price System - Mac Edition\n\n"
                          "FUNCTION KEYS:\n"
                          "F1 - Help\n"
                          "F2 - Save\n"
                          "F5 - Refresh\n"
                          "F9 - Download\n\n"
                          "MENU ACCESS:\n"
                          "Just press: f, e, v, d, h\n"
                          "Or use: Option+letter\n"
                          "Or use: Cmd+O, Cmd+S, Cmd+Q")
        
    def show_about(self):
        messagebox.showinfo("About", 
                          "DOKKAEBI Price Downloader\n"
                          "Tkinter Edition\n\n"
                          "Because Textual sucks and\n"
                          "Tkinter just fucking works!")
        
    def focus_menu(self):
        """Focus on menu bar with F10"""
        self.tk_focusNext()
        
    def show_file_menu(self):
        """Programmatically show file menu"""
        messagebox.showinfo("BOINK!", "BOINK! You pressed F (File menu)")
        
    def show_edit_menu(self):
        messagebox.showinfo("BOINK!", "BOINK! You pressed E (Edit menu)")
        
    def show_view_menu(self):
        messagebox.showinfo("BOINK!", "BOINK! You pressed V (View menu)")
        
    def show_download_menu(self):
        messagebox.showinfo("BOINK!", "BOINK! You pressed D (Download menu)")
        
    def show_help_menu(self):
        messagebox.showinfo("BOINK!", "BOINK! You pressed H (Help menu)")


def main():
    """Run the DOS-style Tkinter app"""
    app = DOSApp()
    app.mainloop()


if __name__ == "__main__":
    main()