#!/usr/bin/env python3
"""
Working Dropdown Menu Implementation
Following the EXACT pattern from the instructions
"""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Label, Static
from textual.reactive import reactive
from textual.widget import Widget
from textual.binding import Binding


class DropdownMenu(Widget):
    """A custom dropdown menu widget."""

    is_open = reactive(False)

    def __init__(self, label: str, options: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.options = options
        self.selected_option = None

    def compose(self) -> ComposeResult:
        yield Button(self.label, id="dropdown-button")
        with Vertical(id="dropdown-options", classes="hidden"):
            for option in self.options:
                yield Button(option, id=f"option-{option.replace(' ', '-').replace('.', '')}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "dropdown-button":
            self.is_open = not self.is_open
            event.stop()
        elif event.button.id.startswith("option-"):
            self.selected_option = event.button.label
            self.query_one("#dropdown-button").label = self.selected_option
            self.is_open = False
            self.app.bell()  # Feedback
            event.stop()

    def watch_is_open(self, is_open: bool) -> None:
        """React to changes in the dropdown state."""
        options_container = self.query_one("#dropdown-options")
        if is_open:
            options_container.remove_class("hidden")
        else:
            options_container.add_class("hidden")


class MyApp(App):
    """A Textual app to demonstrate the dropdown."""
    
    CSS = """
    Screen {
        background: #0000AA;
    }
    
    #dropdown-button {
        background: white;
        color: #0000AA;
        border: heavy #0000AA;
        padding: 0 1;
        margin: 1;
    }
    
    #dropdown-options {
        background: white;
        border: heavy #0000AA;
        margin-top: 0;
        width: auto;
    }
    
    #dropdown-options.hidden {
        display: none;
    }
    
    #dropdown-options Button {
        background: white;
        color: #0000AA;
        border: none;
        text-align: left;
        width: 100%;
        padding: 0 1;
        margin: 0;
    }
    
    #dropdown-options Button:hover {
        background: #0000AA;
        color: white;
    }
    
    #status {
        color: white;
        margin: 2;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f", "open_file_menu", "File Menu"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Static("DOS-Style Dropdown Test", id="title")
        
        # Create the File dropdown menu
        yield DropdownMenu(
            "[bold red]F[/bold red]ile",
            ["Open...", "Save", "Save As...", "Exit"],
            id="file-dropdown"
        )
        
        yield Label("Press 'f' to open File menu", id="status")

    def action_quit(self) -> None:
        """Quit the app."""
        self.exit()
    
    def action_open_file_menu(self) -> None:
        """Open the File menu with 'f' key."""
        dropdown = self.query_one("#file-dropdown", DropdownMenu)
        dropdown.is_open = True


if __name__ == "__main__":
    app = MyApp()
    app.run()