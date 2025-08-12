#!/usr/bin/env python3
"""
Demo script for the interactive CLI
Shows off the beautiful UI without requiring user input
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_downloader.interactive_cli import InteractivePriceDownloader
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule

console = Console()

def demo_ui_components():
    """Demo the beautiful UI components."""
    console.clear()
    
    # Initialize app for demo
    app = InteractivePriceDownloader("sandbox/demo_cache.duckdb")
    
    # Show banner
    app.show_banner()
    time.sleep(1)
    
    # Demo main menu
    console.print(Rule("[bold cyan]Main Menu Demo[/bold cyan]"))
    console.print()
    
    menu_table = Table(show_header=False, box=None, padding=(0, 2))
    menu_table.add_column("Option", style="bold yellow", width=4)
    menu_table.add_column("Action", style="bright_white")
    menu_table.add_column("Description", style="dim")
    
    menu_table.add_row("1", "Download Data", "Download price data from Alpaca")
    menu_table.add_row("2", "View Cache", "Examine cached data statistics")
    menu_table.add_row("3", "Manage Symbols", "Edit watchlist and symbols")
    menu_table.add_row("4", "Clear Cache", "Remove old cached data")
    menu_table.add_row("5", "Connection Status", "Check Alpaca connection")
    menu_table.add_row("q", "Quit", "Exit the application")
    
    console.print(menu_table)
    console.print()
    time.sleep(2)
    
    # Demo cache stats
    console.print(Rule("[bold green]Cache Statistics Demo[/bold green]"))
    console.print()
    
    # Create fake stats for demo
    daily_table = Table(
        title="📊 Daily Prices",
        show_header=True,
        header_style="bold green",
        border_style="green"
    )
    daily_table.add_column("Metric", style="cyan")
    daily_table.add_column("Value", justify="right", style="bright_white")
    
    daily_table.add_row("Symbols", "31")
    daily_table.add_row("Total Rows", "7,750")
    daily_table.add_row("Earliest", "2023-01-01")
    daily_table.add_row("Latest", "2024-01-01")
    daily_table.add_row("Data Type", "[green]daily[/green]")
    
    console.print(daily_table)
    console.print()
    time.sleep(2)
    
    # Demo download progress
    console.print(Rule("[bold yellow]Download Progress Demo[/bold yellow]"))
    console.print()
    
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    
    results_table = Table(
        title="Download Results",
        show_header=True,
        header_style="bold magenta"
    )
    results_table.add_column("Symbol", style="cyan", width=8)
    results_table.add_column("Status", justify="center", width=12)
    results_table.add_column("Rows", justify="right", style="green", width=8)
    results_table.add_column("Latest Close", justify="right", style="yellow")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]"),
        console=console
    ) as progress:
        task = progress.add_task("Downloading...", total=len(symbols))
        
        for i, symbol in enumerate(symbols):
            progress.update(task, description=f"[cyan]Downloading {symbol}...")
            time.sleep(0.5)
            
            # Add fake successful result
            results_table.add_row(
                symbol,
                "[green]✅ Success[/green]",
                "365",
                f"${150 + i * 50:.2f}"
            )
            
            progress.update(task, advance=1)
    
    console.print(results_table)
    console.print()
    time.sleep(1)
    
    # Demo summary
    console.print(Panel(
        "[bold green]🎉 Demo Complete![/bold green]\n\n"
        "The interactive CLI features:\n"
        "• Beautiful real-time progress displays\n"
        "• Color-coded status indicators\n"
        "• Professional data tables\n"
        "• Intuitive menu navigation\n"
        "• Live cache statistics\n"
        "• Symbol management tools\n\n"
        "[italic]REBELLIOUSLY ELEGANT by design![/italic]",
        title="[bold cyan]DOKKAEBI Interactive CLI[/bold cyan]",
        border_style="bright_blue"
    ))
    
    app.cache.close()

if __name__ == "__main__":
    console.print("[bold magenta]🎭 DOKKAEBI Interactive CLI Demo[/bold magenta]\n")
    demo_ui_components()
    console.print("\n[dim]Demo complete. Run 'python -m src.price_downloader.interactive_cli' to use the real thing![/dim]")