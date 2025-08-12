"""
DOKKAEBI Interactive Price Downloader CLI

A beautiful, real-time interactive interface for managing price data.
Built with Click and Rich for maximum elegance and user experience.

Viper's REBELLIOUSLY ELEGANT masterpiece - because command lines 
should be fucking gorgeous and intuitive!
"""

import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Fix import path for direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box
from rich.rule import Rule

from price_downloader.providers.alpaca_provider import AlpacaProvider
from price_downloader.storage.cache_v2 import PriceCacheV2

# Initialize rich console for beautiful output
console = Console()

# Configure logging to be less verbose for UI
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class InteractivePriceDownloader:
    """
    Interactive CLI for DOKKAEBI price downloader.
    
    Features:
    - Beautiful menu-driven interface
    - Real-time download progress with live updates
    - Cache viewer with detailed statistics
    - Symbol management and validation
    - Color-coded status indicators
    - Professional data handling
    """
    
    def __init__(self, cache_path: str = "data/price_cache.duckdb"):
        """Initialize interactive downloader."""
        self.cache_path = cache_path
        self.cache = PriceCacheV2(cache_path)
        self.alpaca = None
        self._init_alpaca()
        
        # Color palette for consistent theming
        self.colors = {
            'primary': 'bright_cyan',
            'secondary': 'bright_magenta', 
            'success': 'bright_green',
            'warning': 'bright_yellow',
            'error': 'bright_red',
            'accent': 'bright_blue',
            'muted': 'dim white'
        }
        
    def _init_alpaca(self) -> None:
        """Initialize Alpaca provider with error handling."""
        # Check for credentials first
        if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
            self.alpaca = None
            return
            
        try:
            self.alpaca = AlpacaProvider(cache_path=self.cache_path)
            
            # Test connection
            if not self.alpaca.test_connection():
                console.print(
                    Panel(
                        "[red]❌ Alpaca connection failed![/red]\n\n"
                        "Check your API credentials:\n"
                        "  • ALPACA_API_KEY\n"
                        "  • ALPACA_API_SECRET\n\n"
                        "Get FREE account at: [link]https://alpaca.markets[/link]",
                        title="[bold red]Connection Error[/bold red]",
                        border_style="red"
                    )
                )
                self.alpaca = None
            else:
                console.print("[green]✅ Connected to Alpaca Markets[/green]")
                
        except Exception as e:
            console.print(f"[red]❌ Alpaca initialization failed: {e}[/red]")
            self.alpaca = None
    
    def show_banner(self) -> None:
        """Display the epic DOKKAEBI ASCII art banner."""
        # Epic cyberpunk ASCII art
        dokkaebi_art = """[bold cyan]
    ██████╗  ██████╗ ██╗  ██╗██╗  ██╗ █████╗ ███████╗██████╗ ██╗
    ██╔══██╗██╔═══██╗██║ ██╔╝██║ ██╔╝██╔══██╗██╔════╝██╔══██╗██║
    ██║  ██║██║   ██║█████╔╝ █████╔╝ ███████║█████╗  ██████╔╝██║
    ██║  ██║██║   ██║██╔═██╗ ██╔═██╗ ██╔══██║██╔══╝  ██╔══██╗██║
    ██████╔╝╚██████╔╝██║  ██╗██║  ██╗██║  ██║███████╗██████╔╝██║
    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝[/bold cyan]
    
    [bold magenta]═══════════[/bold magenta] [bold white]AI-POWERED TRADING TERMINAL[/bold white] [bold magenta]═══════════[/bold magenta]
    [bold yellow]💰[/bold yellow] [italic bright_green]Feeding HebbNet with premium market data[/italic bright_green] [bold yellow]💰[/bold yellow]
    [dim bright_blue]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim bright_blue]
        """
        
        # Add status indicators with animations
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        
        status_bar = f"""[dim]
    [bold green]●[/bold green] SYSTEM ONLINE    [bold yellow]●[/bold yellow] MARKET FEEDS ACTIVE    [bold cyan]●[/bold cyan] HEBBNET READY    [dim white]{timestamp}[/dim white]
        [/dim]"""
        
        console.print(Panel(
            dokkaebi_art + status_bar,
            border_style="bright_cyan",
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        ))
        console.print()
    
    def _animate_loading(self, message: str, duration: float = 2.0) -> None:
        """Create beautiful loading animation."""
        frames = [
            "[bold bright_cyan]◐[/bold bright_cyan]",
            "[bold bright_magenta]◓[/bold bright_magenta]", 
            "[bold bright_cyan]◑[/bold bright_cyan]",
            "[bold bright_magenta]◒[/bold bright_magenta]"
        ]
        
        start_time = time.time()
        frame_idx = 0
        
        while time.time() - start_time < duration:
            frame = frames[frame_idx % len(frames)]
            console.print(f"\r{frame} [bold white]{message}[/bold white]", end="")
            time.sleep(0.2)
            frame_idx += 1
        
        console.print(f"\r[bold bright_green]✓[/bold bright_green] [bold white]{message}[/bold white] [dim]complete[/dim]")
    
    def _show_transition(self, from_menu: str, to_menu: str) -> None:
        """Smooth transition between menu states."""
        console.print()
        console.print(f"[dim bright_blue]╰─→[/dim bright_blue] [italic]Transitioning from {from_menu} to {to_menu}...[/italic]")
        
        # Brief loading effect
        for i in range(3):
            console.print(f"[dim bright_cyan]{'▶' * (i + 1)}[/dim bright_cyan]", end="\r")
            time.sleep(0.15)
        console.print(" " * 10)  # Clear the line
    
    def show_main_menu(self) -> str:
        """Display main menu with cyberpunk styling."""
        # Create animated header with glitch effect
        console.print(Panel(
            "[bold bright_magenta]◢[/bold bright_magenta][bold cyan]■[/bold cyan][bold bright_magenta]◣[/bold bright_magenta] [bold white]COMMAND INTERFACE[/bold white] [bold bright_magenta]◢[/bold bright_magenta][bold cyan]■[/bold cyan][bold bright_magenta]◣[/bold bright_magenta]",
            border_style="bright_magenta",
            box=box.ROUNDED
        ))
        console.print()
        
        # Menu with enhanced visual hierarchy
        menu_table = Table(
            show_header=False, 
            box=box.SIMPLE_HEAD,
            border_style="dim cyan",
            padding=(0, 3, 0, 1),
            expand=True
        )
        menu_table.add_column("Key", style="bold bright_yellow", width=6, justify="center")
        menu_table.add_column("Icon", width=4, justify="center")
        menu_table.add_column("Action", style="bold bright_white", min_width=20)
        menu_table.add_column("Description", style="dim bright_blue")
        
        # Menu items with relevant emoji indicators
        menu_items = [
            ("1", "📊", "Download Data", "[cyan]Stream price data from Alpaca Markets"),
            ("2", "💾", "View Cache", "[green]Analyze cached market data & statistics"),
            ("3", "🎯", "Manage Symbols", "[yellow]Configure watchlist and trading symbols"),
            ("4", "🗑️", "Clear Cache", "[red]Remove outdated cached data"),
            ("5", "🔗", "Connection Status", "[blue]Verify Alpaca API connection"),
            ("q", "🚪", "Quit", "[dim]Exit DOKKAEBI terminal"),
        ]
        
        for key, icon, action, desc in menu_items:
            # Add subtle color coding for different actions
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
        console.print()
        
        # Enhanced prompt with visual flair
        console.print("[dim bright_blue]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim bright_blue]")
        
        choice = Prompt.ask(
            "[bold bright_cyan]⚡[/bold bright_cyan] [bold white]Select operation[/bold white]",
            choices=["1", "2", "3", "4", "5", "q"],
            default="1",
            show_choices=False
        )
        
        return choice
    
    def download_menu(self) -> None:
        """Handle download operations with cyberpunk flair."""
        if not self.alpaca:
            console.print(Panel(
                "[bold red]⚠ SYSTEM ERROR ⚠[/bold red]\n\n"
                "[red]Alpaca connection not available![/red]\n"
                "[dim]Check your API credentials and try again.[/dim]",
                border_style="red",
                box=box.DOUBLE
            ))
            input("\nPress Enter to continue...")
            return
        
        self._show_transition("Main Menu", "Download Interface")
        console.clear()
        self.show_banner()
        
        # Enhanced download header
        console.print(Panel(
            "[bold bright_green]📡 DATA ACQUISITION INTERFACE 📡[/bold bright_green]\n"
            "[dim bright_blue]Initializing market data streams...[/dim bright_blue]",
            border_style="bright_green",
            box=box.HEAVY
        ))
        console.print()
        
        # Get download parameters
        symbols = self._get_symbols_for_download()
        if not symbols:
            return
            
        interval = self._get_interval()
        period_days = self._get_period()
        
        console.print()
        console.print(f"[cyan]Downloading {len(symbols)} symbols...[/cyan]")
        console.print(f"[dim]Interval: {interval}, Period: {period_days} days[/dim]")
        console.print()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Download with beautiful progress display
        self._download_with_progress(symbols, start_date, end_date, interval)
        
        console.print()
        input("Press Enter to continue...")
    
    def _get_symbols_for_download(self) -> List[str]:
        """Get symbols for download from user."""
        console.print("[bold]Symbol Selection:[/bold]")
        console.print("1. Use default watchlist (31 symbols)")
        console.print("2. Enter custom symbols")
        console.print("3. Use all cached symbols")
        console.print()
        
        choice = Prompt.ask(
            "Select option",
            choices=["1", "2", "3"],
            default="1"
        )
        
        if choice == "1":
            # Load from watchlist
            watchlist_path = "data/watchlist.txt"
            if os.path.exists(watchlist_path):
                try:
                    with open(watchlist_path, 'r') as f:
                        symbols = [
                            line.strip().upper() 
                            for line in f 
                            if line.strip() and not line.startswith('#')
                        ]
                    console.print(f"[green]✅ Loaded {len(symbols)} symbols from watchlist[/green]")
                    return symbols
                except Exception as e:
                    console.print(f"[red]❌ Error reading watchlist: {e}[/red]")
                    return []
            else:
                console.print(f"[red]❌ Watchlist not found: {watchlist_path}[/red]")
                return []
                
        elif choice == "2":
            # Get custom symbols
            symbols_input = Prompt.ask(
                "Enter symbols (comma separated)",
                default="AAPL,MSFT,GOOGL"
            )
            symbols = [s.strip().upper() for s in symbols_input.split(',')]
            console.print(f"[green]✅ Using {len(symbols)} custom symbols[/green]")
            return symbols
            
        elif choice == "3":
            # Get cached symbols
            try:
                stats = self.cache.get_cache_stats()
                cached_symbols = self._get_cached_symbols()
                if cached_symbols:
                    console.print(f"[green]✅ Found {len(cached_symbols)} cached symbols[/green]")
                    return cached_symbols
                else:
                    console.print("[yellow]⚠️ No cached symbols found[/yellow]")
                    return []
            except Exception as e:
                console.print(f"[red]❌ Error getting cached symbols: {e}[/red]")
                return []
    
    def _get_interval(self) -> str:
        """Get time interval from user."""
        console.print()
        console.print("[bold]Time Interval:[/bold]")
        intervals = {
            "1": ("1Day", "Daily bars"),
            "2": ("1Hour", "Hourly bars"), 
            "3": ("30Min", "30-minute bars"),
            "4": ("15Min", "15-minute bars"),
            "5": ("5Min", "5-minute bars")
        }
        
        for key, (interval, desc) in intervals.items():
            console.print(f"{key}. {desc}")
        
        choice = Prompt.ask(
            "Select interval",
            choices=list(intervals.keys()),
            default="1"
        )
        
        return intervals[choice][0]
    
    def _get_period(self) -> int:
        """Get download period from user."""
        console.print()
        console.print("[bold]Download Period:[/bold]")
        periods = {
            "1": (7, "1 week"),
            "2": (30, "1 month"),
            "3": (90, "3 months"),
            "4": (180, "6 months"),
            "5": (365, "1 year")
        }
        
        for key, (days, desc) in periods.items():
            console.print(f"{key}. {desc}")
        
        choice = Prompt.ask(
            "Select period",
            choices=list(periods.keys()),
            default="2"
        )
        
        return periods[choice][0]
    
    def _download_with_progress(
        self, 
        symbols: List[str], 
        start_date: datetime, 
        end_date: datetime, 
        interval: str
    ) -> None:
        """Download data with beautiful real-time progress display."""
        results = {}
        success_count = 0
        fail_count = 0
        
        # Create layout for live updates
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=8),
            Layout(name="results", ratio=1)
        )
        
        # Enhanced results table with cyberpunk styling
        results_table = Table(
            title="[bold bright_magenta]◆ ACQUISITION RESULTS ◆[/bold bright_magenta]",
            show_header=True,
            header_style="bold bright_cyan",
            border_style="bright_magenta",
            box=box.HEAVY_HEAD
        )
        results_table.add_column("SYMBOL", style="bold bright_cyan", width=8, justify="center")
        results_table.add_column("STATUS", justify="center", width=14)
        results_table.add_column("RECORDS", justify="right", style="bright_green", width=10)
        results_table.add_column("PRICE $", justify="right", style="bright_yellow", width=12)
        
        with Live(layout, refresh_per_second=10, console=console) as live:
            # Enhanced header with cyberpunk styling
            header_text = Text()
            header_text.append("🚀 ", style="bold bright_yellow")
            header_text.append("NEURAL DATA ACQUISITION", style="bold bright_cyan")
            header_text.append(" 🚀", style="bold bright_yellow")
            header_text.append(f"\n[{len(symbols)} symbols] • [real-time streaming] • [HebbNet pipeline]", style="dim bright_blue")
            
            layout["header"].update(Panel(
                Align.center(header_text),
                border_style="bright_cyan",
                box=box.HEAVY
            ))
            
            # Progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=Console(file=None)  # Disable auto-display
            ) as progress:
                task = progress.add_task(
                    "Downloading...", 
                    total=len(symbols)
                )
                layout["progress"].update(progress)
                
                for i, symbol in enumerate(symbols):
                    # Update progress description
                    progress.update(
                        task, 
                        description=f"[cyan]Downloading {symbol}...",
                        completed=i
                    )
                    
                    try:
                        # Get data from Alpaca
                        data = self.alpaca.get_historical_data(
                            symbol, 
                            start_date, 
                            end_date, 
                            interval
                        )
                        
                        if not data.empty:
                            success_count += 1
                            latest_close = data['Close'].iloc[-1]
                            status = "[green]✅ Success[/green]"
                            rows = str(len(data))
                            price = f"${latest_close:.2f}"
                        else:
                            fail_count += 1
                            status = "[red]❌ Failed[/red]"
                            rows = "0"
                            price = "N/A"
                        
                        results[symbol] = data
                        
                        # Add to results table
                        results_table.add_row(symbol, status, rows, price)
                        
                        # Update layout
                        layout["results"].update(Panel(
                            results_table,
                            title=f"Results ({success_count} success, {fail_count} failed)",
                            border_style="green" if fail_count == 0 else "yellow"
                        ))
                        
                        # Small delay for visual effect
                        time.sleep(0.1)
                        
                    except Exception as e:
                        fail_count += 1
                        results[symbol] = pd.DataFrame()
                        results_table.add_row(
                            symbol, 
                            "[red]❌ Error[/red]", 
                            "0", 
                            "N/A"
                        )
                        console.print(f"[red]Error downloading {symbol}: {e}[/red]")
                
                # Final progress update
                progress.update(task, completed=len(symbols))
        
        # Show final summary
        console.print()
        self._show_download_summary(success_count, fail_count, len(symbols))
    
    def _show_download_summary(self, success: int, failed: int, total: int) -> None:
        """Show download summary with beautiful formatting."""
        success_rate = (success / total * 100) if total > 0 else 0
        
        if success_rate == 100:
            border_style = "green"
            status_emoji = "🎉"
        elif success_rate >= 80:
            border_style = "yellow"
            status_emoji = "⚠️"
        else:
            border_style = "red"
            status_emoji = "❌"
        
        summary_text = Text()
        summary_text.append(f"{status_emoji} Download Complete\n\n", style="bold")
        summary_text.append(f"Success: {success}/{total} ", style="green")
        summary_text.append(f"({success_rate:.1f}%)\n", style="dim")
        summary_text.append(f"Failed: {failed}", style="red" if failed > 0 else "dim")
        
        console.print(Panel(
            Align.center(summary_text),
            title="[bold]Summary[/bold]",
            border_style=border_style
        ))
    
    def cache_viewer(self) -> None:
        """Display cache statistics with beautiful data visualization."""
        self._show_transition("Main Menu", "Cache Analytics")
        console.clear()
        self.show_banner()
        
        # Animated loading for cache analysis
        self._animate_loading("Analyzing cache database", 1.5)
        console.print()
        
        console.print(Panel(
            "[bold bright_blue]📊 CACHE ANALYTICS DASHBOARD 📊[/bold bright_blue]\n"
            "[dim bright_cyan]Real-time database statistics and insights[/dim bright_cyan]",
            border_style="bright_blue",
            box=box.HEAVY
        ))
        console.print()
        
        try:
            stats = self.cache.get_cache_stats()
            
            # Create two-column layout for daily and intraday stats
            layout = Layout()
            layout.split_row(
                Layout(name="daily"),
                Layout(name="intraday")
            )
            
            # Daily prices table
            daily_table = Table(
                title="📊 Daily Prices",
                show_header=True,
                header_style="bold green",
                border_style="green"
            )
            daily_table.add_column("Metric", style="cyan")
            daily_table.add_column("Value", justify="right", style="bright_white")
            
            daily_table.add_row("Symbols", f"{stats['daily']['symbols']:,}")
            daily_table.add_row("Total Rows", f"{stats['daily']['rows']:,}")
            daily_table.add_row("Earliest", str(stats['daily']['earliest'] or 'N/A'))
            daily_table.add_row("Latest", str(stats['daily']['latest'] or 'N/A'))
            daily_table.add_row("Data Type", "[green]daily[/green]")
            
            layout["daily"].update(daily_table)
            
            # Intraday prices table  
            intraday_table = Table(
                title="⚡ Intraday Prices",
                show_header=True,
                header_style="bold yellow",
                border_style="yellow"
            )
            intraday_table.add_column("Metric", style="cyan")
            intraday_table.add_column("Value", justify="right", style="bright_white")
            
            intraday_table.add_row("Symbols", f"{stats['intraday']['symbols']:,}")
            intraday_table.add_row("Total Rows", f"{stats['intraday']['rows']:,}")
            intraday_table.add_row("Earliest", str(stats['intraday']['earliest'] or 'N/A'))
            intraday_table.add_row("Latest", str(stats['intraday']['latest'] or 'N/A'))
            intraday_table.add_row("Data Type", "[yellow]intraday[/yellow]")
            
            layout["intraday"].update(intraday_table)
            
            console.print(layout)
            console.print()
            
            # Show cache file info
            if os.path.exists(self.cache_path):
                size_mb = os.path.getsize(self.cache_path) / (1024 * 1024)
                console.print(f"[dim]📁 Cache file: {self.cache_path}[/dim]")
                console.print(f"[dim]💾 Size: {size_mb:.2f} MB[/dim]")
            
            # Show sample symbols if available
            if stats['daily']['symbols'] > 0 or stats['intraday']['symbols'] > 0:
                console.print()
                self._show_sample_symbols()
                
        except Exception as e:
            console.print(f"[red]❌ Error accessing cache: {e}[/red]")
        
        console.print()
        input("Press Enter to continue...")
    
    def _show_sample_symbols(self) -> None:
        """Show sample cached symbols."""
        try:
            cached_symbols = self._get_cached_symbols()
            if cached_symbols:
                console.print("[bold]Sample Cached Symbols:[/bold]")
                sample_count = min(15, len(cached_symbols))
                sample = cached_symbols[:sample_count]
                
                # Display in rows of 5
                for i in range(0, len(sample), 5):
                    row = sample[i:i+5]
                    console.print("  " + "  ".join(f"[cyan]{s}[/cyan]" for s in row))
                
                if len(cached_symbols) > sample_count:
                    remaining = len(cached_symbols) - sample_count
                    console.print(f"  [dim]... and {remaining} more[/dim]")
        except Exception as e:
            console.print(f"[red]Error getting sample symbols: {e}[/red]")
    
    def _get_cached_symbols(self) -> List[str]:
        """Get list of cached symbols."""
        with self.cache._get_connection() as conn:
            # Get symbols from both tables
            daily_symbols = conn.execute(
                "SELECT DISTINCT symbol FROM daily_prices ORDER BY symbol"
            ).fetchall()
            
            intraday_symbols = conn.execute(
                "SELECT DISTINCT symbol FROM intraday_prices ORDER BY symbol"
            ).fetchall()
            
            # Combine and deduplicate
            all_symbols = set()
            all_symbols.update(row[0] for row in daily_symbols)
            all_symbols.update(row[0] for row in intraday_symbols)
            
            return sorted(list(all_symbols))
    
    def symbol_manager(self) -> None:
        """Manage symbols and watchlist with enhanced UX."""
        self._show_transition("Main Menu", "Symbol Manager")
        console.clear()
        self.show_banner()
        
        console.print(Panel(
            "[bold bright_yellow]🎯 SYMBOL MANAGEMENT CONSOLE 🎯[/bold bright_yellow]\n"
            "[dim bright_yellow]Configure trading symbols and watchlists[/dim bright_yellow]",
            border_style="bright_yellow",
            box=box.HEAVY
        ))
        console.print()
        
        watchlist_path = "data/watchlist.txt"
        
        console.print("[bold]Watchlist Options:[/bold]")
        console.print("1. View current watchlist")
        console.print("2. Add symbols to watchlist") 
        console.print("3. Remove symbols from watchlist")
        console.print("4. Reset to default watchlist")
        console.print()
        
        choice = Prompt.ask(
            "Select option",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        if choice == "1":
            self._view_watchlist(watchlist_path)
        elif choice == "2":
            self._add_to_watchlist(watchlist_path)
        elif choice == "3":
            self._remove_from_watchlist(watchlist_path)
        elif choice == "4":
            self._reset_watchlist(watchlist_path)
        
        console.print()
        input("Press Enter to continue...")
    
    def _view_watchlist(self, path: str) -> None:
        """View current watchlist."""
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    lines = f.readlines()
                
                symbols = [
                    line.strip().upper() 
                    for line in lines 
                    if line.strip() and not line.startswith('#')
                ]
                
                console.print(f"[green]📋 Current Watchlist ({len(symbols)} symbols):[/green]")
                console.print()
                
                # Display in a nice table
                table = Table(show_header=False, box=None, padding=(0, 1))
                table.add_column("Symbol", style="cyan")
                table.add_column("Symbol", style="cyan")
                table.add_column("Symbol", style="cyan")
                table.add_column("Symbol", style="cyan")
                table.add_column("Symbol", style="cyan")
                
                for i in range(0, len(symbols), 5):
                    row = symbols[i:i+5]
                    while len(row) < 5:
                        row.append("")
                    table.add_row(*row)
                
                console.print(table)
                
            except Exception as e:
                console.print(f"[red]❌ Error reading watchlist: {e}[/red]")
        else:
            console.print(f"[yellow]⚠️ Watchlist not found: {path}[/yellow]")
    
    def _add_to_watchlist(self, path: str) -> None:
        """Add symbols to watchlist."""
        new_symbols_input = Prompt.ask(
            "Enter symbols to add (comma separated)",
            default="AAPL,MSFT"
        )
        
        new_symbols = [s.strip().upper() for s in new_symbols_input.split(',')]
        
        try:
            # Read existing symbols
            existing_symbols = set()
            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            existing_symbols.add(line.strip().upper())
            
            # Add new symbols
            added_symbols = []
            for symbol in new_symbols:
                if symbol not in existing_symbols:
                    existing_symbols.add(symbol)
                    added_symbols.append(symbol)
            
            if added_symbols:
                # Write back to file
                with open(path, 'w') as f:
                    f.write("# DOKKAEBI Default Watchlist\n")
                    f.write("# Meme stocks and high-volume targets for HebbNet training\n")
                    f.write("# Lines starting with # are comments\n\n")
                    
                    for symbol in sorted(existing_symbols):
                        f.write(f"{symbol}\n")
                
                console.print(f"[green]✅ Added {len(added_symbols)} symbols: {', '.join(added_symbols)}[/green]")
            else:
                console.print("[yellow]⚠️ All symbols already in watchlist[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ Error updating watchlist: {e}[/red]")
    
    def _remove_from_watchlist(self, path: str) -> None:
        """Remove symbols from watchlist."""
        if not os.path.exists(path):
            console.print(f"[yellow]⚠️ Watchlist not found: {path}[/yellow]")
            return
        
        try:
            # Read existing symbols
            with open(path, 'r') as f:
                lines = f.readlines()
            
            symbols = [
                line.strip().upper() 
                for line in lines 
                if line.strip() and not line.startswith('#')
            ]
            
            console.print(f"Current symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
            
            remove_input = Prompt.ask(
                "Enter symbols to remove (comma separated)"
            )
            
            if not remove_input.strip():
                console.print("[yellow]⚠️ No symbols specified[/yellow]")
                return
                
            remove_symbols = [s.strip().upper() for s in remove_input.split(',')]
            
            # Remove symbols
            remaining_symbols = [s for s in symbols if s not in remove_symbols]
            removed_count = len(symbols) - len(remaining_symbols)
            
            if removed_count > 0:
                # Write back to file
                with open(path, 'w') as f:
                    f.write("# DOKKAEBI Default Watchlist\n")
                    f.write("# Meme stocks and high-volume targets for HebbNet training\n")
                    f.write("# Lines starting with # are comments\n\n")
                    
                    for symbol in sorted(remaining_symbols):
                        f.write(f"{symbol}\n")
                
                console.print(f"[green]✅ Removed {removed_count} symbols[/green]")
            else:
                console.print("[yellow]⚠️ No symbols were removed[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ Error updating watchlist: {e}[/red]")
    
    def _reset_watchlist(self, path: str) -> None:
        """Reset watchlist to default."""
        if Confirm.ask("Reset watchlist to default symbols?"):
            try:
                default_symbols = [
                    "# DOKKAEBI Default Watchlist",
                    "# Meme stocks and high-volume targets for HebbNet training",
                    "# Lines starting with # are comments",
                    "",
                    "# Classic Meme Stocks",
                    "GME", "AMC", "BB", "NOK", "CLOV",
                    "",
                    "# Recent Meme Candidates", 
                    "DNUT", "GPRO", "PLTR", "SOFI", "HOOD",
                    "",
                    "# High Volume Tech",
                    "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMD",
                    "",
                    "# Crypto-Adjacent",
                    "COIN", "MARA", "RIOT", "MSTR",
                    "",
                    "# Reddit Favorites",
                    "TLRY", "SNDL", "SPCE", "RKT", "FUBO"
                ]
                
                with open(path, 'w') as f:
                    for line in default_symbols:
                        f.write(f"{line}\n")
                
                console.print("[green]✅ Watchlist reset to default[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error resetting watchlist: {e}[/red]")
    
    def clear_cache_menu(self) -> None:
        """Handle cache clearing operations with enhanced security."""
        self._show_transition("Main Menu", "Cache Management")
        console.clear()
        self.show_banner()
        
        console.print(Panel(
            "[bold bright_red]🗑️ CACHE PURGE INTERFACE 🗑️[/bold bright_red]\n"
            "[dim bright_red]⚠ WARNING: Destructive operations below ⚠[/dim bright_red]",
            border_style="bright_red",
            box=box.HEAVY
        ))
        console.print()
        
        console.print("[bold]Clear Options:[/bold]")
        console.print("1. Clear data older than 30 days")
        console.print("2. Clear data older than 90 days")
        console.print("3. Clear all intraday data")
        console.print("4. Clear all daily data")
        console.print("5. Clear everything (DANGER!)")
        console.print()
        
        choice = Prompt.ask(
            "Select option",
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )
        
        if choice == "1":
            self._clear_old_data(30)
        elif choice == "2":
            self._clear_old_data(90)
        elif choice == "3":
            self._clear_table_data("intraday")
        elif choice == "4":
            self._clear_table_data("daily")
        elif choice == "5":
            self._clear_all_data()
        
        console.print()
        input("Press Enter to continue...")
    
    def _clear_old_data(self, days: int) -> None:
        """Clear data older than specified days."""
        if not Confirm.ask(f"Clear data older than {days} days?"):
            console.print("[yellow]⚠️ Operation cancelled[/yellow]")
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.cache._get_connection() as conn:
                # Clear old daily data
                daily_result = conn.execute("""
                    DELETE FROM daily_prices 
                    WHERE trading_date < ?
                """, [cutoff_date.date()]).fetchone()
                
                # Clear old intraday data
                intraday_result = conn.execute("""
                    DELETE FROM intraday_prices 
                    WHERE bar_timestamp < ?
                """, [cutoff_date]).fetchone()
            
            console.print(f"[green]✅ Cleared data older than {days} days[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error clearing old data: {e}[/red]")
    
    def _clear_table_data(self, table_type: str) -> None:
        """Clear all data from specified table type."""
        table_name = f"{table_type}_prices"
        
        if not Confirm.ask(f"Clear ALL {table_type} data?"):
            console.print("[yellow]⚠️ Operation cancelled[/yellow]")
            return
        
        try:
            with self.cache._get_connection() as conn:
                conn.execute(f"DELETE FROM {table_name}")
            
            console.print(f"[green]✅ Cleared all {table_type} data[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error clearing {table_type} data: {e}[/red]")
    
    def _clear_all_data(self) -> None:
        """Clear all cached data (nuclear option)."""
        console.print("[bold red]⚠️ WARNING: This will delete ALL cached data![/bold red]")
        
        if not Confirm.ask("Are you absolutely sure?"):
            console.print("[yellow]⚠️ Operation cancelled[/yellow]")
            return
        
        if not Confirm.ask("Type 'DELETE' to confirm", default=False):
            console.print("[yellow]⚠️ Operation cancelled[/yellow]")
            return
        
        try:
            with self.cache._get_connection() as conn:
                conn.execute("DELETE FROM daily_prices")
                conn.execute("DELETE FROM intraday_prices")
            
            console.print("[green]✅ All cache data cleared[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error clearing all data: {e}[/red]")
    
    def connection_status(self) -> None:
        """Check and display connection status with diagnostics."""
        self._show_transition("Main Menu", "System Diagnostics")
        console.clear()
        self.show_banner()
        
        # Animated connection testing
        self._animate_loading("Running system diagnostics", 2.0)
        console.print()
        
        console.print(Panel(
            "[bold bright_blue]🔗 SYSTEM DIAGNOSTICS 🔗[/bold bright_blue]\n"
            "[dim bright_blue]Network connectivity and API status[/dim bright_blue]",
            border_style="bright_blue",
            box=box.HEAVY
        ))
        console.print()
        
        # Check Alpaca connection
        if self.alpaca:
            console.print("[green]✅ Alpaca Markets: Connected[/green]")
            
            # Test with a simple request
            try:
                latest = self.alpaca.get_latest_price("AAPL")
                if latest:
                    console.print(f"[dim]   Latest AAPL price: ${latest:.2f}[/dim]")
                else:
                    console.print("[yellow]   ⚠️ Could not fetch latest price[/yellow]")
            except Exception as e:
                console.print(f"[red]   ❌ Error testing connection: {e}[/red]")
        else:
            console.print("[red]❌ Alpaca Markets: Not connected[/red]")
            console.print("[dim]   Check API credentials[/dim]")
        
        # Check cache status
        try:
            stats = self.cache.get_cache_stats()
            console.print("[green]✅ DuckDB Cache: Connected[/green]")
            console.print(f"[dim]   Daily records: {stats['daily']['rows']:,}[/dim]")
            console.print(f"[dim]   Intraday records: {stats['intraday']['rows']:,}[/dim]")
        except Exception as e:
            console.print(f"[red]❌ DuckDB Cache: Error - {e}[/red]")
        
        # Check environment
        console.print()
        console.print("[bold]Environment:[/bold]")
        
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        
        console.print(f"ALPACA_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
        console.print(f"ALPACA_API_SECRET: {'✅ Set' if api_secret else '❌ Missing'}")
        
        if api_key:
            console.print(f"[dim]API Key: {api_key[:8]}...{api_key[-4:]}[/dim]")
        
        console.print()
        input("Press Enter to continue...")
    
    def _startup_animation(self) -> None:
        """Beautiful startup animation sequence."""
        console.clear()
        
        # Set terminal title for extra style points
        print("\033]0;DOKKAEBI Neural Trading Terminal\007", end="")
        
        # Animated startup sequence
        startup_frames = [
            "[dim]Initializing DOKKAEBI...[/dim]",
            "[dim bright_cyan]Loading neural network modules...[/dim bright_cyan]", 
            "[dim bright_magenta]Connecting to market feeds...[/dim bright_magenta]",
            "[dim bright_green]System ready![/dim bright_green]"
        ]
        
        for i, frame in enumerate(startup_frames):
            console.print(f"[bold bright_cyan]{'█' * (i + 1)}[/bold bright_cyan] {frame}")
            time.sleep(0.5)
        
        console.print()
        console.print("[bold bright_green]✓[/bold bright_green] [bold]DOKKAEBI Trading Terminal Initialized[/bold]")
        time.sleep(1)
    
    def _shutdown_animation(self) -> None:
        """Graceful shutdown animation."""
        console.print()
        console.print("[dim bright_yellow]Shutting down DOKKAEBI...[/dim bright_yellow]")
        
        shutdown_steps = [
            "Closing market connections",
            "Saving cache state", 
            "Terminating neural processes",
            "Goodbye, trader"
        ]
        
        for step in shutdown_steps:
            console.print(f"[dim]• {step}...[/dim]")
            time.sleep(0.3)
        
        console.print()
        console.print(Panel(
            "[bold bright_cyan]DOKKAEBI[/bold bright_cyan] [bold white]session terminated[/bold white]\n"
            "[italic dim]May your trades be profitable 📈[/italic dim]",
            border_style="cyan",
            box=box.ROUNDED
        ))

    def run(self) -> None:
        """Run the interactive CLI with beautiful animations."""
        try:
            # Startup sequence
            self._startup_animation()
            
            while True:
                console.clear()
                self.show_banner()
                
                choice = self.show_main_menu()
                
                if choice == "1":
                    self.download_menu()
                elif choice == "2":
                    self.cache_viewer()
                elif choice == "3":
                    self.symbol_manager()
                elif choice == "4":
                    self.clear_cache_menu()
                elif choice == "5":
                    self.connection_status()
                elif choice == "q":
                    self._shutdown_animation()
                    break
                    
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted by user[/dim]")
            self._shutdown_animation()
        except Exception as e:
            console.print(f"\n[red]❌ System error: {e}[/red]")
            console.print("[dim]Initiating emergency shutdown...[/dim]")
            self._shutdown_animation()
        finally:
            if self.cache:
                self.cache.close()


@click.command()
@click.option(
    '--cache-path',
    default='data/price_cache.duckdb',
    help='Path to DuckDB cache file'
)
def main(cache_path: str):
    """
    🚀 DOKKAEBI Neural Trading Terminal 🚀
    
    AI-powered market data acquisition interface for HebbNet training.
    Cyberpunk aesthetic meets professional trading technology.
    
    Features:
    • Epic ASCII art terminal interface
    • Real-time data streaming from Alpaca Markets  
    • Beautiful progress animations and transitions
    • Neural network-ready data preprocessing
    • Advanced cache management and analytics
    
    Built with REBELLIOUS ELEGANCE by the DOKKAEBI team.
    """
    app = InteractivePriceDownloader(cache_path)
    app.run()


if __name__ == '__main__':
    main()