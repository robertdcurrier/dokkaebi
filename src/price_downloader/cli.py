"""
DOKKAEBI Price Downloader CLI

Command-line interface for downloading and managing price data.
Built with Click for the DOKKAEBI algorithmic trading platform.

Viper's bulletproof CLI - because command lines should be fucking elegant.
"""

import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# Fix import path for direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import box

from price_downloader.core.ticker_universe import TickerUniverse
from price_downloader.providers.alpaca_provider import AlpacaProvider
from price_downloader.storage.cache_v2 import PriceCacheV2
from price_downloader.filters.market_filters import (
    PriceFilter, 
    VolumeFilter, 
    MarketCapFilter,
    ExchangeFilter,
    LiquidityFilter,
    CompositeFilter
)


# Initialize rich console for beautiful output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@click.group()
@click.option(
    '--cache-path', 
    default='data/price_cache.duckdb',
    help='Path to DuckDB cache file'
)
@click.option(
    '--log-level',
    default='INFO',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    help='Logging level'
)
@click.pass_context
def cli(ctx, cache_path: str, log_level: str):
    """
    DOKKAEBI Price Downloader - Feed HebbNet with premium market data.
    
    A bulletproof price data downloader with intelligent caching,
    filtering, and exchange ticker management.
    """
    # Set up context
    ctx.ensure_object(dict)
    ctx.obj['cache_path'] = cache_path
    
    # Configure logging
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Display banner
    console.print(Panel.fit(
        "[bold magenta]DOKKAEBI Price Downloader[/bold magenta]\n"
        "[italic]Feeding HebbNet with premium market data[/italic]",
        border_style="bright_blue"
    ))




@cli.command()
@click.option(
    '--exchanges',
    multiple=True,
    default=['NASDAQ', 'NYSE'],
    help='Exchanges to fetch tickers from'
)
@click.option(
    '--output',
    help='Output file for ticker list (CSV format)'
)
@click.option(
    '--use-cache/--no-cache',
    default=True,
    help='Use cached ticker lists'
)
@click.pass_context
def fetch_tickers(ctx, exchanges: tuple, output: Optional[str], use_cache: bool):
    """Fetch ticker lists from exchanges."""
    
    ticker_universe = TickerUniverse()
    
    console.print(f"[cyan]Fetching tickers from {len(exchanges)} exchanges...[/cyan]")
    
    # Fetch tickers
    all_tickers = ticker_universe.get_all_tickers(
        list(exchanges), 
        use_cache=use_cache
    )
    
    # Display results
    table = Table(title="Exchange Ticker Counts")
    table.add_column("Exchange", style="cyan")
    table.add_column("Ticker Count", justify="right", style="green")
    
    total_tickers = 0
    for exchange, tickers in all_tickers.items():
        table.add_row(exchange, str(len(tickers)))
        total_tickers += len(tickers)
        
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{total_tickers}[/bold]")
    console.print(table)
    
    # Save to file if requested
    if output:
        combined_tickers = ticker_universe.get_combined_universe(
            list(exchanges)
        )
        
        df = pd.DataFrame({'symbol': combined_tickers})
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(combined_tickers)} tickers to {output}[/green]")


@cli.command()
@click.option(
    '--min-price',
    type=float,
    help='Minimum stock price'
)
@click.option(
    '--max-price',
    type=float,
    help='Maximum stock price'
)
@click.option(
    '--min-volume',
    type=int,
    help='Minimum daily volume'
)
@click.option(
    '--min-market-cap',
    type=float,
    help='Minimum market cap (millions)'
)
@click.option(
    '--exchanges',
    multiple=True,
    help='Exchanges to include'
)
@click.option(
    '--min-dollar-volume',
    type=float,
    default=1000000,
    help='Minimum daily dollar volume'
)
@click.option(
    '--output',
    help='Output file for filtered tickers'
)
@click.pass_context  
def filter_universe(
    ctx,
    min_price: Optional[float],
    max_price: Optional[float], 
    min_volume: Optional[int],
    min_market_cap: Optional[float],
    exchanges: tuple,
    min_dollar_volume: float,
    output: Optional[str]
):
    """Filter ticker universe based on criteria."""
    
    # Build filter list
    filters = []
    
    if min_price is not None or max_price is not None:
        filters.append(PriceFilter(min_price, max_price))
        
    if min_volume is not None:
        filters.append(VolumeFilter(min_volume=min_volume))
        
    if min_market_cap is not None:
        filters.append(MarketCapFilter(min_market_cap=min_market_cap))
        
    if exchanges:
        filters.append(ExchangeFilter(list(exchanges)))
        
    if min_dollar_volume > 0:
        filters.append(LiquidityFilter(min_dollar_volume=min_dollar_volume))
        
    if not filters:
        console.print("[red]No filter criteria specified[/red]")
        sys.exit(1)
        
    # Create composite filter
    composite_filter = CompositeFilter(filters, logic='AND')
    
    console.print(f"[cyan]Applying filters: {composite_filter.name}[/cyan]")
    
    # Get latest prices from cache
    with PriceDownloader(cache_path=ctx.obj['cache_path']) as downloader:
        latest_prices = downloader.cache.get_latest_prices()
        
    if latest_prices.empty:
        console.print("[red]No price data in cache. Run download first.[/red]")
        sys.exit(1)
        
    # Apply filters
    filtered_data = composite_filter.apply(latest_prices)
    
    # Display results
    console.print(f"[green]Filtered {len(latest_prices)} tickers down to {len(filtered_data)}[/green]")
    
    if not filtered_data.empty:
        # Show top 10 results
        top_results = filtered_data.head(10)
        
        table = Table(title="Top Filtered Tickers")
        table.add_column("Symbol", style="cyan")
        table.add_column("Price", justify="right", style="green")
        table.add_column("Volume", justify="right")
        table.add_column("Dollar Volume", justify="right")
        
        for _, row in top_results.iterrows():
            dollar_vol = row['close'] * row['volume']
            table.add_row(
                row['symbol'],
                f"${row['close']:.2f}",
                f"{row['volume']:,}",
                f"${dollar_vol:,.0f}"
            )
            
        console.print(table)
        
        # Save to file if requested
        if output:
            filtered_data.to_csv(output, index=False)
            console.print(f"[green]Saved {len(filtered_data)} filtered tickers to {output}[/green]")


@cli.command()
@click.pass_context
def cache_info(ctx):
    """Display cache statistics and information."""
    
    with PriceDownloader(cache_path=ctx.obj['cache_path']) as downloader:
        stats = downloader.get_cache_stats()
        cached_symbols = downloader.get_cached_symbols()
        
    # Display cache info
    info_table = Table(title="Cache Information")
    info_table.add_column("Metric", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Cache Path", stats['cache_path'])
    info_table.add_row("Cached Symbols", str(stats['cached_symbols']))
    info_table.add_row("Total Downloads", str(stats['download_stats']['symbols_downloaded']))
    info_table.add_row("Failed Downloads", str(stats['download_stats']['symbols_failed']))
    info_table.add_row("Cache Hits", str(stats['download_stats']['cache_hits']))
    
    console.print(info_table)
    
    # Show some example symbols
    if cached_symbols:
        console.print(f"\n[cyan]Sample cached symbols:[/cyan]")
        sample_symbols = cached_symbols[:20]
        console.print(", ".join(sample_symbols))
        
        if len(cached_symbols) > 20:
            console.print(f"... and {len(cached_symbols) - 20} more")


@cli.command()
@click.option(
    '--older-than-days',
    type=int,
    help='Delete data older than N days'
)
@click.option(
    '--confirm',
    is_flag=True,
    help='Skip confirmation prompt'
)
@click.pass_context
def clear_cache(ctx, older_than_days: Optional[int], confirm: bool):
    """Clear cached data."""
    
    if not confirm:
        if older_than_days:
            message = f"Clear data older than {older_than_days} days?"
        else:
            message = "Clear ALL cached data?"
            
        if not click.confirm(message):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
            
    with PriceDownloader(cache_path=ctx.obj['cache_path']) as downloader:
        rows_deleted = downloader.clear_cache(older_than_days)
        
    if rows_deleted > 0:
        console.print(f"[green]Cleared {rows_deleted} rows from cache[/green]")
    else:
        console.print("[yellow]No data was cleared[/yellow]")


def _display_download_results(results: dict, stats: dict) -> None:
    """Display download results in a formatted table."""
    
    # Create results table
    table = Table(title="Download Results")
    table.add_column("Symbol", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Rows", justify="right")
    table.add_column("Date Range")
    
    successful = 0
    failed = 0
    
    for symbol, data in results.items():
        if data is not None and not data.empty:
            status = "✓ Success"
            rows = str(len(data))
            date_range = f"{data.index.min().date()} to {data.index.max().date()}"
            successful += 1
        else:
            status = "✗ Failed"
            rows = "0"
            date_range = "N/A"
            failed += 1
            
        table.add_row(symbol, status, rows, date_range)
        
    console.print(table)
    
    # Summary
    total = len(results)
    success_rate = (successful / total * 100) if total > 0 else 0
    
    summary = (
        f"[green]Summary:[/green] {successful}/{total} successful "
        f"({success_rate:.1f}%), {failed} failed"
    )
    
    if 'cache_hits' in stats['download_stats']:
        cache_hits = stats['download_stats']['cache_hits']
        summary += f", {cache_hits} cache hits"
        
    console.print(f"\n{summary}")


@cli.command()
@click.argument('symbols', nargs=-1, required=False)
@click.option(
    '--file', '-f',
    type=click.Path(exists=True),
    default='data/watchlist.txt',
    help='Text file with symbols (one per line)'
)
@click.option(
    '--period',
    default='1mo',
    help='Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, max)'
)
@click.option(
    '--interval',
    default='1Day',
    help='Data interval (1Day, 1Hour, 5Min, 15Min, 30Min)'
)
@click.pass_context
def download(ctx, symbols: tuple, file: str, period: str, interval: str):
    """
    Download price data using Alpaca Markets.
    
    Professional-grade data with no rate limiting!
    """
    # Show fancy header
    console.print(
        Panel(
            "[bold cyan]DOKKAEBI Price Downloader - Alpaca Markets[/bold cyan]\n"
            "[yellow]Professional data without the bullshit![/yellow]",
            box=box.ROUNDED,
            style="bright_blue"
        )
    )
    
    # Get symbols from either command line or file
    symbol_list = list(symbols) if symbols else []
    
    # If no symbols provided via command line, try to read from file
    if not symbol_list:
        if os.path.exists(file):
            console.print(f"[cyan]Reading symbols from {file}...[/cyan]")
            try:
                with open(file, 'r') as f:
                    symbol_list = [line.strip().upper() for line in f 
                                  if line.strip() and not line.startswith('#')]
                console.print(f"[green]Loaded {len(symbol_list)} symbols from file[/green]")
            except Exception as e:
                console.print(f"[red]Error reading file: {e}[/red]")
                sys.exit(1)
        else:
            console.print(
                "[red]No symbols provided![/red]\n"
                "Use: download AAPL MSFT GOOGL\n"
                "Or: download --file watchlist.txt\n"
                "Or: Create data/watchlist.txt with symbols"
            )
            sys.exit(1)
    
    if not symbol_list:
        console.print("[red]No symbols to download![/red]")
        sys.exit(1)
    
    # Check for Alpaca credentials
    if not os.getenv('ALPACA_API_KEY'):
            console.print(
                Panel(
                    "[red]Alpaca API credentials not found![/red]\n\n"
                    "Please set environment variables:\n"
                    "  export ALPACA_API_KEY='your_key'\n"
                    "  export ALPACA_API_SECRET='your_secret'\n\n"
                    "Get FREE account at: https://alpaca.markets",
                    title="[bold red]Configuration Required[/bold red]",
                    border_style="red"
                )
            )
            sys.exit(1)
    
    console.print("[bold green]Using Alpaca Markets (no rate limits!)[/bold green]\n")
    
    try:
            from price_downloader.providers.alpaca_provider import AlpacaProvider
            alpaca = AlpacaProvider()
            
            # Test connection
            if not alpaca.test_connection():
                console.print("[red]Failed to connect to Alpaca![/red]")
                sys.exit(1)
            
            # Create results table
            table = Table(
                title="Download Results",
                show_header=True,
                header_style="bold magenta"
            )
            table.add_column("Symbol", style="cyan", width=8)
            table.add_column("Status", justify="center")
            table.add_column("Days", justify="right", style="green")
            table.add_column("Latest Close", justify="right", style="yellow")
            
            # Download each symbol
            success_count = 0
            fail_count = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Downloading {len(symbol_list)} symbols...", 
                    total=len(symbol_list)
                )
                
                for symbol in symbol_list:
                    # Get data
                    data = alpaca.get_historical_data(symbol, interval=interval)
                    
                    if not data.empty:
                        success_count += 1
                        latest_close = data['Close'].iloc[-1]
                        table.add_row(
                            symbol,
                            "[green]✅ Success[/green]",
                            str(len(data)),
                            f"${latest_close:.2f}"
                        )
                    else:
                        fail_count += 1
                        table.add_row(
                            symbol,
                            "[red]❌ Failed[/red]",
                            "0",
                            "N/A"
                        )
                    
                    progress.update(task, advance=1)
            
            # Display results
            console.print(table)
            console.print(
                f"\n[bold]Summary:[/bold] "
                f"[green]{success_count} succeeded[/green], "
                f"[red]{fail_count} failed[/red]"
            )
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def cache(ctx):
    """
    View DuckDB cache statistics.
    
    Shows what data is stored in the dual-table architecture.
    """
    console.print(
        Panel(
            "[bold cyan]DuckDB Cache Statistics[/bold cyan]\n"
            "[yellow]Diesel's dual-table architecture in action![/yellow]",
            box=box.ROUNDED,
            style="bright_blue"
        )
    )
    
    try:
        # Initialize cache
        cache = PriceCacheV2(ctx.obj['cache_path'])
        
        # Get statistics
        stats = cache.get_cache_stats()
        
        # Create tables for display
        daily_table = Table(
            title="Daily Prices Table",
            show_header=True,
            header_style="bold magenta"
        )
        daily_table.add_column("Metric", style="cyan")
        daily_table.add_column("Value", justify="right", style="yellow")
        
        daily_table.add_row("Symbols", str(stats['daily']['symbols']))
        daily_table.add_row("Total Rows", f"{stats['daily']['rows']:,}")
        daily_table.add_row("Earliest Date", str(stats['daily']['earliest']))
        daily_table.add_row("Latest Date", str(stats['daily']['latest']))
        daily_table.add_row("Data Type", "daily (explicit metadata)")
        
        console.print(daily_table)
        console.print()
        
        intraday_table = Table(
            title="Intraday Prices Table",
            show_header=True,
            header_style="bold magenta"
        )
        intraday_table.add_column("Metric", style="cyan")
        intraday_table.add_column("Value", justify="right", style="yellow")
        
        intraday_table.add_row("Symbols", str(stats['intraday']['symbols']))
        intraday_table.add_row("Total Rows", f"{stats['intraday']['rows']:,}")
        intraday_table.add_row("Earliest Time", str(stats['intraday']['earliest']))
        intraday_table.add_row("Latest Time", str(stats['intraday']['latest']))
        intraday_table.add_row("Data Type", "intraday (explicit metadata)")
        
        console.print(intraday_table)
        
        # Show cache path
        console.print(f"\n[dim]Cache location: {ctx.obj['cache_path']}[/dim]")
        
        # Check file size
        import os
        if os.path.exists(ctx.obj['cache_path']):
            size_mb = os.path.getsize(ctx.obj['cache_path']) / (1024 * 1024)
            console.print(f"[dim]Cache size: {size_mb:.2f} MB[/dim]")
        
        cache.close()
        
    except Exception as e:
        console.print(f"[red]Error accessing cache: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    cli()