#!/usr/bin/env python3
"""
Demo the beautiful interactive CLI features without requiring input.
Shows off Viper and Repo's collaborative masterpiece!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
import time

console = Console()

def show_ascii_banner():
    """Display the DOKKAEBI banner."""
    banner = """
    ██████╗  ██████╗ ██╗  ██╗██╗  ██╗ █████╗ ███████╗██████╗ ██╗
    ██╔══██╗██╔═══██╗██║ ██╔╝██║ ██╔╝██╔══██╗██╔════╝██╔══██╗██║
    ██║  ██║██║   ██║█████╔╝ █████╔╝ ███████║█████╗  ██████╔╝██║
    ██║  ██║██║   ██║██╔═██╗ ██╔═██╗ ██╔══██║██╔══╝  ██╔══██╗██║
    ██████╔╝╚██████╔╝██║  ██╗██║  ██╗██║  ██║███████╗██████╔╝██║
    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝
    """
    
    panel = Panel(
        f"[bright_cyan]{banner}[/]\n\n[bright_magenta]═══════════ AI-POWERED TRADING TERMINAL ═══════════[/]\n[bright_yellow]💰 Feeding HebbNet with premium market data 💰[/]",
        border_style="bright_cyan",
        padding=(1, 2)
    )
    console.print(panel)

def show_main_menu():
    """Display the beautiful main menu."""
    console.print("\n[bright_cyan]╭──────────────────────────────────────────────────────────────────────────────╮[/]")
    console.print("[bright_cyan]│ ◢■◣ COMMAND INTERFACE ◢■◣                                                    │[/]")
    console.print("[bright_cyan]╰──────────────────────────────────────────────────────────────────────────────╯[/]")
    
    menu_table = Table(show_header=True, header_style="bold bright_magenta", box=None)
    menu_table.add_column("Key", style="bright_yellow", width=4)
    menu_table.add_column("", width=3)  # Icon column
    menu_table.add_column("Action", style="bright_cyan")
    menu_table.add_column("Description", style="dim")
    
    menu_items = [
        ("1", "📊", "Download Data", "Download price data from Alpaca Markets"),
        ("2", "💾", "View Cache", "Display cached data statistics"),
        ("3", "📝", "Manage Watchlist", "Edit symbol watchlist"),
        ("4", "🗑️", "Clear Cache", "Remove cached data"),
        ("5", "🔗", "Test Connection", "Verify Alpaca API connection"),
        ("q", "🚪", "Exit", "Close terminal")
    ]
    
    for key, icon, action, desc in menu_items:
        if key == "1":
            key_style = "[bold bright_green]"
        elif key == "q":
            key_style = "[bold bright_red]"
        else:
            key_style = "[bold bright_yellow]"
        
        menu_table.add_row(
            f"{key_style}{key}[/]",
            icon,
            action,
            desc
        )
    
    console.print(menu_table)

def show_cache_stats():
    """Display cache statistics with beautiful formatting."""
    console.print("\n[bright_magenta]╭──────────────────────────────────────────────────────────────────────────────╮[/]")
    console.print("[bright_magenta]│ 💾 CACHE STATISTICS                                                          │[/]")
    console.print("[bright_magenta]╰──────────────────────────────────────────────────────────────────────────────╯[/]")
    
    # Create side-by-side tables
    daily_table = Table(title="📊 Daily Prices", show_header=True, header_style="bold bright_cyan")
    daily_table.add_column("Metric", style="cyan")
    daily_table.add_column("Value", justify="right", style="bright_yellow")
    
    daily_table.add_row("Symbols", "31")
    daily_table.add_row("Total Rows", "7,640")
    daily_table.add_row("Earliest", "2024-08-13")
    daily_table.add_row("Latest", "2025-08-12")
    daily_table.add_row("Data Type", "daily")
    
    intraday_table = Table(title="⚡ Intraday Prices", show_header=True, header_style="bold bright_magenta")
    intraday_table.add_column("Metric", style="magenta")
    intraday_table.add_column("Value", justify="right", style="bright_yellow")
    
    intraday_table.add_row("Symbols", "30")
    intraday_table.add_row("Total Rows", "213,144")
    intraday_table.add_row("Earliest", "2024-08-12 12:30:00")
    intraday_table.add_row("Latest", "2025-08-12 12:00:00")
    intraday_table.add_row("Data Type", "intraday")
    
    # Display tables side by side
    from rich.columns import Columns
    columns = Columns([daily_table, intraday_table], padding=5)
    console.print(columns)
    
    console.print("\n[dim]📁 Cache file: data/price_cache.duckdb[/]")
    console.print("[dim]💾 Size: 38.76 MB[/]")

def show_download_progress():
    """Simulate download progress with beautiful animations."""
    console.print("\n[bright_cyan]╭──────────────────────────────────────────────────────────────────────────────╮[/]")
    console.print("[bright_cyan]│ 🚀 DATA ACQUISITION IN PROGRESS                                              │[/]")
    console.print("[bright_cyan]╰──────────────────────────────────────────────────────────────────────────────╯[/]")
    
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        task1 = progress.add_task("[bright_yellow]Downloading GME...", total=100)
        task2 = progress.add_task("[bright_yellow]Downloading AMC...", total=100)
        task3 = progress.add_task("[bright_yellow]Downloading AAPL...", total=100)
        
        for i in range(100):
            progress.update(task1, advance=1)
            if i > 20:
                progress.update(task2, advance=1.2)
            if i > 40:
                progress.update(task3, advance=1.5)
            time.sleep(0.02)
    
    # Show results
    results = Table(show_header=True, header_style="bold bright_green")
    results.add_column("Symbol", style="cyan")
    results.add_column("Status", justify="center")
    results.add_column("Bars", justify="right", style="yellow")
    results.add_column("Latest", justify="right", style="green")
    
    results.add_row("GME", "[green]✅ Success[/]", "252", "$22.92")
    results.add_row("AMC", "[green]✅ Success[/]", "252", "$4.31")
    results.add_row("AAPL", "[green]✅ Success[/]", "252", "$185.23")
    
    console.print("\n", results)

def main():
    """Run the demo."""
    console.clear()
    
    # Show startup animation
    console.print("[bright_cyan]█[/] Initializing DOKKAEBI...")
    time.sleep(0.3)
    console.print("[bright_cyan]██[/] Loading neural network modules...")
    time.sleep(0.3)
    console.print("[bright_cyan]███[/] Connecting to market feeds...")
    time.sleep(0.3)
    console.print("[bright_cyan]████[/] System ready!")
    time.sleep(0.5)
    
    console.clear()
    
    # Show the banner
    show_ascii_banner()
    
    # Show main menu
    console.print("\n[bright_green]✨ Main Menu Demo:[/]")
    show_main_menu()
    
    time.sleep(2)
    
    # Show cache statistics
    console.print("\n[bright_green]✨ Cache Statistics Demo:[/]")
    show_cache_stats()
    
    time.sleep(2)
    
    # Show download progress
    console.print("\n[bright_green]✨ Download Progress Demo:[/]")
    show_download_progress()
    
    # Closing
    console.print("\n[bright_magenta]╭──────────────────────────────────────────────────────────────────────────────╮[/]")
    console.print("[bright_magenta]│ This interactive CLI was built by Viper (functionality) and Repo (aesthetics) │[/]")
    console.print("[bright_magenta]│ REBELLIOUSLY ELEGANT × AESTHETIC PERFECTION = TERMINAL NIRVANA              │[/]")
    console.print("[bright_magenta]╰──────────────────────────────────────────────────────────────────────────────╯[/]")

if __name__ == "__main__":
    main()