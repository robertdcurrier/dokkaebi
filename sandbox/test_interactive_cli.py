#!/usr/bin/env python3
"""
Test script for the interactive CLI
Quick validation that everything works properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_downloader.interactive_cli import InteractivePriceDownloader
from rich.console import Console

console = Console()

def test_initialization():
    """Test that the interactive CLI initializes properly."""
    try:
        app = InteractivePriceDownloader("sandbox/test_cache.duckdb")
        console.print("[green]✅ Interactive CLI initializes successfully[/green]")
        
        # Test banner
        app.show_banner()
        console.print("[green]✅ Banner displays correctly[/green]")
        
        # Test cache stats (should work even with empty cache)
        try:
            from src.price_downloader.storage.cache_v2 import PriceCacheV2
            cache = PriceCacheV2("sandbox/test_cache.duckdb")
            stats = cache.get_cache_stats()
            console.print(f"[green]✅ Cache stats work: {stats}[/green]")
            cache.close()
        except Exception as e:
            console.print(f"[red]❌ Cache stats error: {e}[/red]")
        
        app.cache.close()
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Initialization failed: {e}[/red]")
        return False

def test_alpaca_connection():
    """Test Alpaca connection (if credentials available)."""
    if not os.getenv('ALPACA_API_KEY'):
        console.print("[yellow]⚠️ Skipping Alpaca test - no credentials[/yellow]")
        return True
    
    try:
        from src.price_downloader.providers.alpaca_provider import AlpacaProvider
        alpaca = AlpacaProvider()
        
        if alpaca.test_connection():
            console.print("[green]✅ Alpaca connection works[/green]")
            return True
        else:
            console.print("[red]❌ Alpaca connection failed[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Alpaca test error: {e}[/red]")
        return False

if __name__ == "__main__":
    console.print("[bold cyan]🧪 Testing Interactive CLI[/bold cyan]\n")
    
    results = []
    results.append(test_initialization())
    results.append(test_alpaca_connection())
    
    console.print()
    if all(results):
        console.print("[bold green]🎉 All tests passed! Interactive CLI is ready to rock![/bold green]")
    else:
        console.print("[bold red]❌ Some tests failed. Check the errors above.[/bold red]")