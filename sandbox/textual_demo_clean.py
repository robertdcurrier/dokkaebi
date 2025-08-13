#!/usr/bin/env python3
"""
Clean, Simple Textual DOS Demo App
==================================

A bulletproof DOS-style interface demonstration featuring:
- DOS menu bar at top
- Function key bar at bottom  
- Two independently scrollable text windows
- Classic blue DOS styling with white text

Requirements:
- Uses only documented Textual widgets
- Simple, working foundation
- No experimental features
- Proper keyboard navigation
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive




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
    Clean DOS-style demo application
    
    Features:
    - DOS blue background with white text
    - Menu bar and function key bar
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
    
    #menu-bar {
        background: white;
        color: #0000AA;
        text-style: bold;
        padding: 0 1;
        height: 1;
        dock: top;
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
        ("f1", "help", "Help"),
        ("f2", "save", "Save"),
        ("f3", "load", "Load"),
        ("f4", "exit_app", "Exit"),
        ("f5", "refresh", "Refresh"),
        ("f6", "options", "Options"),
        ("f7", "search", "Search"),
        ("f8", "delete", "Delete"),
        ("f9", "menu", "Menu"),
        ("f10", "quit", "Quit"),
        ("tab", "focus_next", "Next Window"),
        ("shift+tab", "focus_previous", "Previous Window"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Exit"),
    ]
    
    TITLE = "File  Edit  View  Tools  Options  Window  Help"
    SUB_TITLE = "DOS-Style Interface with Function Keys"

    def compose(self) -> ComposeResult:
        """Build the DOS-style interface"""
        # Custom DOS menu bar at top
        yield Static(
            " File  Edit  View  Tools  Options  Window  Help",
            id="menu-bar"
        )
        
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

    def on_key(self, event) -> None:
        """Handle additional keyboard input"""
        # Let built-in navigation handle scrolling
        # Arrow keys, Page Up/Down work automatically
        pass


def main():
    """Run the DOS demo application"""
    app = DOSDemo()
    app.run()


if __name__ == "__main__":
    main()