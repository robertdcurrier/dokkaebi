#!/usr/bin/env python3
"""
DOS Interface with Dropdown File Menu
=====================================

A DOS-style interface demonstration featuring:
- DOS menu bar at top with working File dropdown
- Function key bar at bottom  
- Two independently scrollable text windows
- Classic blue DOS styling with white text

Requirements:
- Uses only documented Textual widgets
- Implements Bob's exact dropdown pattern
- Proper keyboard navigation
"""

from textual.app import App, ComposeResult
from textual import events
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Button
from textual.reactive import reactive
from textual.widget import Widget
from textual.binding import Binding


class FileMenu(Widget):
    """DOS-style File dropdown menu."""
    
    is_open = reactive(False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_items = [
            "Open...",
            "Save", 
            "Save As...",
            "---",  # Separator
            "Exit"
        ]
    
    def compose(self) -> ComposeResult:
        yield Button("[bold red]F[/bold red]ile", id="file-button", classes="menu-button")
        with Vertical(id="file-dropdown", classes="dropdown hidden"):
            yield Button("[bold red]O[/bold red]pen...", id="file-open")
            yield Button("[bold red]S[/bold red]ave", id="file-save")
            yield Button("Save [bold red]A[/bold red]s...", id="file-save-as")
            yield Static("─────────", classes="separator")
            yield Button("E[bold red]x[/bold red]it", id="file-exit")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "file-button":
            self.is_open = not self.is_open
            if self.is_open:
                # Focus on the dropdown for keyboard navigation
                dropdown = self.query_one("#file-dropdown")
                dropdown.focus()
            event.stop()
        elif event.button.id.startswith("file-"):
            # Handle menu item selection
            if event.button.id == "file-exit":
                self.app.exit()
            else:
                self.app.bell()
            self.is_open = False
            event.stop()
    
    def watch_is_open(self, is_open: bool) -> None:
        """React to changes in dropdown state."""
        dropdown = self.query_one("#file-dropdown")
        if is_open:
            dropdown.remove_class("hidden")
            dropdown.styles.display = "block"  # Force visibility
            dropdown.focus()
        else:
            dropdown.add_class("hidden")
            dropdown.styles.display = "none"  # Force hidden

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard shortcuts when dropdown is open."""
        if self.is_open:
            key_lower = event.key.lower()
            if key_lower == "o":
                # Trigger Open
                self.app.bell()
                self.is_open = False
                event.stop()
            elif key_lower == "s":
                # Trigger Save
                self.app.bell()
                self.is_open = False
                event.stop()
            elif key_lower == "a":
                # Trigger Save As
                self.app.bell()
                self.is_open = False
                event.stop()
            elif key_lower == "x":
                # Trigger Exit
                self.app.exit()
                event.stop()
            elif event.key == "escape":
                # Close dropdown
                self.is_open = False
                event.stop()


class ScrollableTextWindow(ScrollableContainer):
    """A scrollable text window with sample data"""
    
    content_lines = reactive(list())
    
    def __init__(self, title: str, content_type: str = "lorem", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content_type = content_type
        
    def on_mount(self) -> None:
        """Populate with sample data when mounted"""
        if self.content_type == "lorem":
            self.content_lines = self.generate_lorem_content()
        else:
            self.content_lines = self.generate_number_content()
        self.refresh_content()
    
    def generate_lorem_content(self) -> list[str]:
        """Generate Lorem Ipsum style content"""
        lorem_lines = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse.",
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa.",
            "Qui officia deserunt mollit anim id est laborum.",
            "Sed ut perspiciatis unde omnis iste natus error sit voluptatem.",
            "Accusantium doloremque laudantium, totam rem aperiam.",
            "Eaque ipsa quae ab illo inventore veritatis et quasi architecto.",
            "Beatae vitae dicta sunt explicabo nemo enim ipsam voluptatem.",
            "Quia voluptas sit aspernatur aut odit aut fugit.",
            "Sed quia consequuntur magni dolores eos qui ratione.",
            "Voluptatem sequi nesciunt neque porro quisquam est.",
            "Qui dolorem ipsum quia dolor sit amet, consectetur.",
            "Adipisci velit sed quia non numquam eius modi tempora.",
            "Incidunt ut labore et dolore magnam aliquam quaerat.",
            "Voluptatem ut enim ad minima veniam, quis nostrum.",
            "Exercitationem ullam corporis suscipit laboriosam.",
            "Nisi ut aliquid ex ea commodi consequatur.",
            "Quis autem vel eum iure reprehenderit qui in ea.",
            "Voluptate esse quam nihil molestiae consequatur.",
            "Vel illum qui dolorem eum fugiat quo voluptas nulla.",
            "Pariatur excepteur sint occaecat cupidatat non proident.",
            "Sunt in culpa qui officia deserunt mollit anim.",
            "Id est laborum et dolorum fuga et harum quidem."
        ] * 5  # Repeat 5 times for scrolling
        
        return lorem_lines
    
    def generate_number_content(self) -> list[str]:
        """Generate numbered data content"""
        number_lines = []
        for i in range(1, 201):  # 200 lines for scrolling
            if i % 10 == 0:
                number_lines.append(f"Line {i:3d}: *** MILESTONE LINE ***")
            elif i % 5 == 0:
                number_lines.append(f"Line {i:3d}: -- Checkpoint --")
            else:
                number_lines.append(f"Line {i:3d}: Regular data entry with some content")
        
        return number_lines
    
    def refresh_content(self) -> None:
        """Update the scrollable content"""
        # Clear existing content
        self.remove_children()
        
        # Add title
        self.mount(Static(f"═══ {self.title} ═══", classes="window-title"))
        
        # Add all content lines as Static widgets
        for line in self.content_lines:
            self.mount(Static(line, classes="content-line"))


class DOSDemo(App):
    """
    Clean DOS-style demo application with File dropdown menu
    
    Features:
    - DOS blue background with white text
    - Working File dropdown menu
    - Two independent scrollable text windows
    - Classic keyboard navigation
    """
    
    CSS = """
    Screen {
        background: #0000AA;
        color: white;
    }
    
    Header {
        background: #0000AA;
        color: white;
        text-style: bold;
        border-bottom: thick white;
    }
    
    Footer {
        background: #0000AA;
        color: white;
        border-top: thick white;
    }
    
    #main-container {
        layout: horizontal;
        height: 100%;
        background: #0000AA;
    }
    
    #left-window {
        width: 50%;
        height: 100%;
        border: thick white;
        margin: 0 1 0 0;
    }
    
    #right-window {
        width: 50%;
        height: 100%;
        border: thick white;
        margin: 0 0 0 1;
    }
    
    .window-title {
        color: yellow;
        text-style: bold;
        text-align: center;
        background: #0000AA;
        margin: 0 0 1 0;
    }
    
    .content-line {
        background: #0000AA;
        color: white;
        padding: 0 1;
    }
    
    ScrollableContainer {
        background: #0000AA;
        color: white;
    }
    
    ScrollableContainer:focus {
        border: thick yellow;
    }
    
    .menu-button {
        background: white;
        color: #0000AA;
        border: none;
        padding: 0 1;
        height: 1;
        margin: 0 1;
    }
    
    .menu-button:hover {
        background: #0000AA;
        color: white;
    }
    
    #menu-bar {
        layout: horizontal;
        background: white;
        height: 1;
        dock: top;
    }
    
    .dropdown {
        background: white;
        color: #0000AA;
        border: thick #0000AA;
        margin-top: 1;
        width: 20;
        layer: overlay;
    }
    
    .dropdown.hidden {
        display: none;
    }
    
    .dropdown Button {
        background: white;
        color: #0000AA;
        border: none;
        text-align: left;
        width: 100%;
        padding: 0 1;
    }
    
    .dropdown Button:hover {
        background: #0000AA;
        color: white;
    }
    
    .separator {
        color: #0000AA;
        padding: 0 1;
    }
    
    #function-bar {
        background: white;
        color: #0000AA;
        text-style: bold;
        padding: 0 1;
        height: 1;
        dock: bottom;
    }
    """
    
    BINDINGS = [
        Binding("f", "open_file_menu", "File Menu"),
        Binding("alt+f", "open_file_menu", "File Menu Alt"),
        Binding("f1", "help", "Help"),
        Binding("f2", "save", "Save"),
        Binding("f3", "load", "Load"),
        Binding("f4", "exit_app", "Exit"),
        Binding("f5", "refresh", "Refresh"),
        Binding("f6", "options", "Options"),
        Binding("f7", "search", "Search"),
        Binding("f8", "delete", "Delete"),
        Binding("f9", "menu", "Menu"),
        Binding("f10", "quit", "Quit"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Exit"),
    ]
    
    TITLE = "DOS-Style Interface with Dropdown Menus"
    SUB_TITLE = "File dropdown menu test"

    def compose(self) -> ComposeResult:
        """Build the DOS-style interface with dropdown File menu"""
        # Menu bar with File dropdown and other static items
        with Horizontal(id="menu-bar"):
            yield FileMenu()
            yield Button("[bold red]E[/bold red]dit", id="edit-button", classes="menu-button")
            yield Button("[bold red]V[/bold red]iew", id="view-button", classes="menu-button")
            yield Button("[bold red]T[/bold red]ools", id="tools-button", classes="menu-button")
            yield Button("[bold red]O[/bold red]ptions", id="options-button", classes="menu-button")
            yield Button("[bold red]W[/bold red]indow", id="window-button", classes="menu-button")
            yield Button("[bold red]H[/bold red]elp", id="help-button", classes="menu-button")
        
        # Main content area with two windows
        with Container(id="main-container"):
            yield ScrollableTextWindow(
                title="Left Window - Lorem Ipsum",
                content_type="lorem",
                id="left-window"
            )
            yield ScrollableTextWindow(
                title="Right Window - Numbered Data", 
                content_type="numbers",
                id="right-window"
            )
        
        # Custom function key bar at bottom
        yield Static(
            "F1=Help  F2=Save  F3=Load  F4=Exit  F5=Refresh  F6=Options  F7=Search  F8=Delete  F9=Menu  F10=Quit",
            id="function-bar"
        )

    def on_mount(self) -> None:
        """Initialize the demo when app starts"""
        # Set initial focus to left window
        self.query_one("#left-window").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu button presses (non-File menu)"""
        # Only handle non-File menu buttons (File is handled by FileMenu widget)
        if event.button.id in ["edit-button", "view-button", "tools-button", 
                               "options-button", "window-button", "help-button"]:
            self.bell()  # DOS-style beep for now
            event.stop()

    def action_help(self) -> None:
        """Show help information"""
        self.bell()  # DOS-style beep
        # In a real app, would show help dialog
        
    def action_save(self) -> None:
        """Save action (F2)"""
        self.bell()
        
    def action_load(self) -> None:
        """Load action (F3)"""
        self.bell()
        
    def action_exit_app(self) -> None:
        """Exit application (F4)"""
        self.exit()
        
    def action_refresh(self) -> None:
        """Refresh action (F5)"""
        self.bell()
        # Refresh content in both windows
        left_window = self.query_one("#left-window")
        right_window = self.query_one("#right-window")
        left_window.refresh_content()
        right_window.refresh_content()
        
    def action_options(self) -> None:
        """Options action (F6)"""
        self.bell()
        
    def action_search(self) -> None:
        """Search action (F7)"""
        self.bell()
        
    def action_delete(self) -> None:
        """Delete action (F8)"""
        self.bell()
        
    def action_menu(self) -> None:
        """Menu action (F9)"""
        self.bell()
        
    def action_focus_next(self) -> None:
        """Move focus to next window (Tab)"""
        focused = self.focused
        if focused and focused.id == "left-window":
            self.query_one("#right-window").focus()
        else:
            self.query_one("#left-window").focus()
    
    def action_focus_previous(self) -> None:
        """Move focus to previous window (Shift+Tab)"""
        # Same logic as next for two windows
        self.action_focus_next()

    def action_open_file_menu(self) -> None:
        """Open the File menu with keyboard."""
        self.bell()  # Debug: make a sound to confirm action is triggered
        file_menu = self.query_one(FileMenu)
        file_menu.is_open = True
        # Focus on the dropdown
        dropdown = file_menu.query_one("#file-dropdown")
        dropdown.focus()
    
    def on_key(self, event: events.Key) -> None:
        """Fallback key handler if bindings don't work."""
        if event.key in ('f', 'F'):
            self.action_open_file_menu()
            event.stop()



def main():
    """Run the DOS demo application"""
    app = DOSDemo()
    app.run()


if __name__ == "__main__":
    main()