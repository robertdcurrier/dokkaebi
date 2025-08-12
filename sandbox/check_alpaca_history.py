#!/usr/bin/env python3
"""
Check exactly how much history we get from Alpaca with different periods.
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_downloader.providers.alpaca_provider import AlpacaProvider
from rich.console import Console
from rich.table import Table

console = Console()

def test_periods():
    """Test different period settings."""
    console.print("[bold cyan]Testing Alpaca History Periods[/bold cyan]\n")
    
    provider = AlpacaProvider()
    
    periods = {
        '1 Day': (datetime.now() - timedelta(days=1), datetime.now()),
        '1 Week': (datetime.now() - timedelta(days=7), datetime.now()),
        '1 Month': (datetime.now() - timedelta(days=30), datetime.now()),
        '3 Months': (datetime.now() - timedelta(days=90), datetime.now()),
        '6 Months': (datetime.now() - timedelta(days=180), datetime.now()),
        '1 Year': (datetime.now() - timedelta(days=365), datetime.now()),
        '2 Years': (datetime.now() - timedelta(days=730), datetime.now()),
    }
    
    table = Table(title="GME Data Available by Period", show_header=True)
    table.add_column("Period", style="cyan")
    table.add_column("Trading Days", justify="right", style="green")
    table.add_column("Date Range", style="yellow")
    table.add_column("First Price", justify="right", style="blue")
    table.add_column("Last Price", justify="right", style="blue")
    
    for period_name, (start, end) in periods.items():
        try:
            data = provider.get_historical_data('GME', start=start, end=end)
            
            if not data.empty:
                first_date = data.index[0].strftime('%Y-%m-%d')
                last_date = data.index[-1].strftime('%Y-%m-%d')
                first_price = data['Close'].iloc[0]
                last_price = data['Close'].iloc[-1]
                
                table.add_row(
                    period_name,
                    str(len(data)),
                    f"{first_date} to {last_date}",
                    f"${first_price:.2f}",
                    f"${last_price:.2f}"
                )
            else:
                table.add_row(period_name, "0", "No data", "N/A", "N/A")
                
        except Exception as e:
            table.add_row(period_name, "Error", str(e)[:30], "N/A", "N/A")
    
    console.print(table)
    
    # Test default (no dates specified)
    console.print("\n[bold]Default behavior (no dates specified):[/bold]")
    data = provider.get_historical_data('GME')
    if not data.empty:
        console.print(f"• Days returned: {len(data)}")
        console.print(f"• Date range: {data.index[0].date()} to {data.index[-1].date()}")
        console.print(f"• That's about {(data.index[-1] - data.index[0]).days} calendar days")
        console.print(f"• Or roughly {(data.index[-1] - data.index[0]).days / 30:.1f} months")

def check_current_cli_default():
    """Check what the CLI gives by default."""
    console.print("\n[bold yellow]Current CLI Defaults:[/bold yellow]")
    console.print("• Default period: 1mo (1 month)")
    console.print("• Default interval: 1Day (daily bars)")
    console.print("• This gives approximately 22 trading days of data")
    console.print("\n[bold green]To get different amounts:[/bold green]")
    console.print("• Quick check (5 days): --period 5d")
    console.print("• Standard (1 month): --period 1mo [DEFAULT]")
    console.print("• Full year: --period 1y")
    console.print("• Maximum available: --period max")

if __name__ == "__main__":
    test_periods()
    check_current_cli_default()