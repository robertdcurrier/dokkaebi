#!/usr/bin/env python3
"""
Demo of Viper's REBELLIOUSLY ELEGANT colorful CLI features!
This shows what the price downloader CLI looks like in action.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
import time

console = Console()

def demo_header():
    """Show the beautiful header."""
    header = Panel(
        "[bold cyan]DOKKAEBI Price Downloader[/bold cyan]\n"
        "[yellow]Feeding HebbNet with premium market data[/yellow]",
        box=box.ROUNDED,
        style="bright_blue"
    )
    console.print(header)

def demo_download_progress():
    """Show the download progress bars."""
    console.print("\n[bold green]Downloading price data...[/bold green]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        # Main download task
        main_task = progress.add_task("[cyan]Downloading symbols", total=5)
        
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        for i, symbol in enumerate(symbols):
            # Sub-task for each symbol
            sub_task = progress.add_task(f"[yellow]${symbol}", total=100)
            
            for _ in range(100):
                time.sleep(0.01)
                progress.update(sub_task, advance=1)
            
            progress.update(main_task, advance=1)
            console.print(f"✅ [green]{symbol}: Downloaded 252 days of data[/green]")

def demo_cache_stats():
    """Show cache statistics table."""
    console.print("\n[bold cyan]Cache Statistics[/bold cyan]\n")
    
    table = Table(
        title="DuckDB Price Cache",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED
    )
    
    table.add_column("Metric", style="cyan", width=25)
    table.add_column("Value", justify="right", style="green")
    
    table.add_row("Total Symbols", "1,247")
    table.add_row("Total Rows", "314,244")
    table.add_row("Cache Size", "48.3 MB")
    table.add_row("Oldest Data", "2023-01-01")
    table.add_row("Latest Update", "2025-08-12 14:55:00")
    table.add_row("Cache Hits Today", "523")
    table.add_row("Downloads Today", "47")
    
    console.print(table)

def demo_filter_results():
    """Show filtered universe results."""
    console.print("\n[bold yellow]Filtered Universe Results[/bold yellow]\n")
    
    # Create a fancy table
    table = Table(
        title="🚀 Meme Stock Candidates (Price < $10, Volume > 1M)",
        show_header=True,
        header_style="bold yellow on blue",
        box=box.DOUBLE_EDGE,
        title_style="bold red"
    )
    
    table.add_column("Symbol", style="cyan", width=8)
    table.add_column("Price", justify="right", style="green")
    table.add_column("Volume", justify="right", style="yellow")
    table.add_column("Market Cap", justify="right", style="magenta")
    table.add_column("Exchange", justify="center", style="blue")
    
    # Add some example data
    stocks = [
        ("DNUT", "$8.45", "2.3M", "$1.2B", "NASDAQ"),
        ("GPRO", "$2.12", "5.7M", "$320M", "NASDAQ"),
        ("BB", "$3.78", "8.9M", "$2.1B", "NYSE"),
        ("WISH", "$0.89", "15.2M", "$890M", "NASDAQ"),
        ("CLOV", "$1.23", "4.5M", "$580M", "NASDAQ"),
    ]
    
    for stock in stocks:
        table.add_row(*stock)
    
    console.print(table)
    console.print(f"\n[green]Found {len(stocks)} stocks matching criteria[/green]")

def demo_error_handling():
    """Show error messages with style."""
    console.print("\n[bold red]Error Handling Example[/bold red]\n")
    
    error_panel = Panel(
        "[red]⚠️  Yahoo Finance Rate Limit Detected[/red]\n\n"
        "The API is temporarily blocking requests.\n"
        "Suggested actions:\n"
        "  • Wait 15-30 minutes\n"
        "  • Use cached data\n"
        "  • Try alternative data source",
        title="[bold red]Error[/bold red]",
        border_style="red"
    )
    console.print(error_panel)

def demo_success_message():
    """Show success message."""
    success_text = Text()
    success_text.append("✨ ", style="yellow")
    success_text.append("Download Complete!", style="bold green")
    success_text.append(" ✨", style="yellow")
    
    success_panel = Panel(
        success_text,
        box=box.DOUBLE,
        style="green",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(success_panel)
    
    # Summary stats
    console.print("\n[bold]Summary:[/bold]")
    console.print("  • Downloaded: [green]47 symbols[/green]")
    console.print("  • Cache hits: [cyan]523 symbols[/cyan]")
    console.print("  • Failed: [red]3 symbols[/red]")
    console.print("  • Total time: [yellow]12.3 seconds[/yellow]")

if __name__ == "__main__":
    console.clear()
    
    # Show all the colorful features
    demo_header()
    time.sleep(1)
    
    demo_download_progress()
    time.sleep(1)
    
    demo_cache_stats()
    time.sleep(1)
    
    demo_filter_results()
    time.sleep(1)
    
    demo_error_handling()
    time.sleep(1)
    
    demo_success_message()
    
    console.print("\n[dim]This is what Viper's CLI looks like in action! 🐍⚡[/dim]\n")