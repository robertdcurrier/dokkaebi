#!/usr/bin/env python3
"""
Usage example for the interactive CLI
Shows how easy it is to use programmatically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_downloader.interactive_cli import InteractivePriceDownloader
from rich.console import Console

console = Console()

def example_usage():
    """Example of using the InteractivePriceDownloader class."""
    console.print("[bold cyan]🚀 DOKKAEBI Interactive CLI Usage Example[/bold cyan]\n")
    
    # Initialize the downloader
    downloader = InteractivePriceDownloader("data/price_cache.duckdb")
    
    # Show the beautiful banner
    downloader.show_banner()
    
    # Check cache stats
    try:
        stats = downloader.cache.get_cache_stats()
        console.print(f"[green]✅ Cache stats: {stats['daily']['symbols']} daily symbols, {stats['intraday']['symbols']} intraday symbols[/green]")
    except Exception as e:
        console.print(f"[red]❌ Cache error: {e}[/red]")
    
    # Check Alpaca connection
    if downloader.alpaca:
        console.print("[green]✅ Alpaca connection available[/green]")
    else:
        console.print("[yellow]⚠️ Alpaca connection not available (no credentials)[/yellow]")
        console.print("[dim]Set ALPACA_API_KEY and ALPACA_API_SECRET to enable downloads[/dim]")
    
    # Example of getting cached symbols
    try:
        cached_symbols = downloader._get_cached_symbols()
        if cached_symbols:
            console.print(f"[cyan]📊 Found {len(cached_symbols)} cached symbols[/cyan]")
            console.print(f"[dim]Sample: {', '.join(cached_symbols[:5])}{'...' if len(cached_symbols) > 5 else ''}[/dim]")
        else:
            console.print("[yellow]⚠️ No cached symbols found[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error getting cached symbols: {e}[/red]")
    
    # Clean up
    downloader.cache.close()
    
    console.print("\n[bold green]✨ Ready to rock! Launch with: python run_interactive_cli.py[/bold green]")

if __name__ == "__main__":
    example_usage()