#!/usr/bin/env python3
"""
DOKKAEBI Price Downloader Textual Interface - PRODUCTION VERSION

This is the REAL interface that actually works with our existing system:
- AlpacaProvider for downloads
- PriceCacheV2 for cache operations  
- data/watchlist.txt for symbol list
- data/price_cache.duckdb for actual data

REBELLIOUSLY ELEGANT but ACTUALLY FUNCTIONAL!
Built by VIPER - FUCKING FLAWLESS as always!
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import (
    Container,
    Horizontal,
    Vertical,
    ScrollableContainer,
    Grid,
    Center
)
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    Log,
    ProgressBar,
    RichLog,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)
from textual import work

from .providers.alpaca_provider import AlpacaProvider
from .storage.cache_v2 import PriceCacheV2

logger = logging.getLogger(__name__)


class DownloadProgress(Container):
    """Real-time download progress widget"""
    
    current_symbol = reactive("")
    total_symbols = reactive(0)
    completed_symbols = reactive(0)
    is_downloading = reactive(False)
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📥 Download Progress", classes="section-header")
            yield Label(id="progress-text")
            yield ProgressBar(id="progress-bar", total=100, show_eta=True)
            yield RichLog(id="download-log", max_lines=10)
    
    def update_progress(self, current: str, completed: int, total: int):
        """Update download progress"""
        self.current_symbol = current
        self.completed_symbols = completed
        self.total_symbols = total
        
        progress_text = self.query_one("#progress-text", Label)
        progress_text.update(
            f"Downloading {current} ({completed}/{total})"
        )
        
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        if total > 0:
            progress_bar.progress = (completed / total) * 100
        
        download_log = self.query_one("#download-log", RichLog)
        download_log.write(f"✅ Downloaded {current}")
    
    def start_download(self, total: int):
        """Start download process"""
        self.is_downloading = True
        self.total_symbols = total
        self.completed_symbols = 0
        
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_bar.total = total
        progress_bar.progress = 0
        
        download_log = self.query_one("#download-log", RichLog)
        download_log.clear()
        download_log.write(f"🚀 Starting download of {total} symbols...")
    
    def finish_download(self, success_count: int, error_count: int):
        """Finish download process"""
        self.is_downloading = False
        
        download_log = self.query_one("#download-log", RichLog)
        download_log.write(f"🎉 Download complete!")
        download_log.write(f"✅ Success: {success_count}")
        download_log.write(f"❌ Errors: {error_count}")


class CacheViewer(Container):
    """Real cache statistics viewer"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📊 Cache Statistics", classes="section-header")
            with Grid(id="cache-stats-grid"):
                yield Static("Loading cache stats...", id="daily-stats")
                yield Static("Loading cache stats...", id="intraday-stats")
            yield Button("🔄 Refresh Stats", id="refresh-cache-stats")
            yield Label("📋 Sample Data", classes="section-header")
            yield DataTable(id="sample-data-table")
    
    def update_cache_stats(self, cache: PriceCacheV2):
        """Update cache statistics display"""
        try:
            stats = cache.get_cache_stats()
            
            daily_widget = self.query_one("#daily-stats", Static)
            daily_widget.update(
                f"📈 Daily Prices\n"
                f"Symbols: {stats['daily']['symbols']}\n"
                f"Records: {stats['daily']['rows']:,}\n"
                f"Range: {stats['daily']['earliest']} to {stats['daily']['latest']}"
            )
            
            intraday_widget = self.query_one("#intraday-stats", Static)  
            intraday_widget.update(
                f"⚡ Intraday Prices\n"
                f"Symbols: {stats['intraday']['symbols']}\n"
                f"Records: {stats['intraday']['rows']:,}\n"
                f"Range: {stats['intraday']['earliest']} to {stats['intraday']['latest']}"
            )
            
            # Show sample data
            self._update_sample_data(cache)
            
        except Exception as e:
            logger.error(f"Failed to update cache stats: {e}")
            daily_widget = self.query_one("#daily-stats", Static)
            daily_widget.update(f"❌ Error loading stats: {e}")
    
    def _update_sample_data(self, cache: PriceCacheV2):
        """Update sample data table"""
        try:
            sample_table = self.query_one("#sample-data-table", DataTable)
            sample_table.clear(columns=True)
            sample_table.add_columns("Symbol", "Date", "Close", "Volume", "Type")
            
            # Get recent daily data
            with cache._get_connection() as conn:
                recent_data = conn.execute("""
                    SELECT symbol, trading_date, close, volume, 'daily' as type
                    FROM daily_prices 
                    ORDER BY trading_date DESC, symbol
                    LIMIT 10
                """).fetchall()
                
                for row in recent_data:
                    sample_table.add_row(
                        str(row[0]),
                        str(row[1]),
                        f"${row[2]:.2f}",
                        f"{row[3]:,}",
                        str(row[4])
                    )
        except Exception as e:
            logger.error(f"Failed to load sample data: {e}")


class WatchlistManager(Container):
    """Manage the watchlist.txt file"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📋 Watchlist Manager", classes="section-header")
            yield TextArea(id="watchlist-editor", language="text")
            with Horizontal():
                yield Button("💾 Save Watchlist", id="save-watchlist")
                yield Button("🔄 Reload Watchlist", id="reload-watchlist")
                yield Button("➕ Add Symbol", id="add-symbol")
            yield Input(placeholder="Enter symbol (e.g., AAPL)", id="symbol-input")
    
    def load_watchlist(self):
        """Load watchlist from file"""
        try:
            watchlist_path = Path("data/watchlist.txt")
            if watchlist_path.exists():
                content = watchlist_path.read_text()
                editor = self.query_one("#watchlist-editor", TextArea)
                editor.text = content
            else:
                editor = self.query_one("#watchlist-editor", TextArea)
                editor.text = "# DOKKAEBI Watchlist\n# Add symbols here\n\nAAPL\nMSFT\nGOOGL\n"
        except Exception as e:
            logger.error(f"Failed to load watchlist: {e}")
    
    def save_watchlist(self):
        """Save watchlist to file"""
        try:
            editor = self.query_one("#watchlist-editor", TextArea)
            content = editor.text
            
            watchlist_path = Path("data/watchlist.txt")
            watchlist_path.parent.mkdir(parents=True, exist_ok=True)
            watchlist_path.write_text(content)
            
            self.app.notify("✅ Watchlist saved successfully!")
        except Exception as e:
            logger.error(f"Failed to save watchlist: {e}")
            self.app.notify(f"❌ Failed to save: {e}")
    
    def add_symbol(self, symbol: str):
        """Add symbol to watchlist"""
        if symbol:
            editor = self.query_one("#watchlist-editor", TextArea)
            current_text = editor.text
            if symbol.upper() not in current_text.upper():
                editor.text = current_text + f"\n{symbol.upper()}"
    
    def get_symbols(self) -> List[str]:
        """Get symbols from editor"""
        try:
            editor = self.query_one("#watchlist-editor", TextArea)
            content = editor.text
            
            symbols = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    symbols.append(line.upper())
            
            return symbols
        except Exception as e:
            logger.error(f"Failed to parse symbols: {e}")
            return []


class PriceDownloaderInterface(App):
    """
    PRODUCTION Price Downloader Textual Interface
    
    Actually works with our real system components:
    - AlpacaProvider for downloads
    - PriceCacheV2 for cache operations
    - data/watchlist.txt for symbol management
    """
    
    CSS = """
    Screen {
        background: #1e1e2e;
        color: #cdd6f4;
    }
    
    .section-header {
        background: #89b4fa;
        color: #1e1e2e;
        text-style: bold;
        padding: 1;
        text-align: center;
        margin-bottom: 1;
    }
    
    #cache-stats-grid {
        grid-size: 2 1;
        grid-gutter: 1;
        margin: 1;
    }
    
    #daily-stats, #intraday-stats {
        background: #313244;
        border: solid #89b4fa;
        padding: 1;
        color: #cdd6f4;
    }
    
    Button {
        margin: 1;
    }
    
    DataTable {
        background: #313244;
        color: #cdd6f4;
        border: solid #89b4fa;
    }
    
    DataTable > .datatable--header {
        background: #89b4fa;
        color: #1e1e2e;
        text-style: bold;
    }
    
    TextArea {
        background: #313244;
        color: #cdd6f4;
        border: solid #89b4fa;
    }
    
    Input {
        background: #313244;
        color: #cdd6f4;
        border: solid #89b4fa;
    }
    
    ProgressBar > .bar--bar {
        color: #a6e3a1;
    }
    
    ProgressBar > .bar--complete {
        color: #a6e3a1;
    }
    
    RichLog {
        background: #313244;
        border: solid #89b4fa;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("d", "focus_download", "Download"),
        Binding("c", "focus_cache", "Cache"),
        Binding("w", "focus_watchlist", "Watchlist"),
    ]
    
    def __init__(self):
        super().__init__()
        self.title = "DOKKAEBI Price Downloader"
        self.sub_title = "Production Interface"
        
        # Initialize providers
        try:
            self.alpaca_provider = AlpacaProvider()
            self.cache = PriceCacheV2()
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")
            self.alpaca_provider = None
            self.cache = None
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with TabbedContent():
            with TabPane("📥 Download", id="download-tab"):
                with Vertical():
                    yield Label("🚀 Download Market Data", classes="section-header")
                    
                    with Horizontal():
                        yield Select(
                            [
                                ("1Day", "1Day"),
                                ("1Hour", "1Hour"),
                                ("30Min", "30Min"),
                                ("15Min", "15Min"),
                                ("5Min", "5Min"),
                            ],
                            value="1Day",
                            id="interval-select"
                        )
                        yield Button("📥 Download Watchlist", id="download-watchlist")
                        yield Button("📥 Download Custom", id="download-custom")
                    
                    yield Input(
                        placeholder="Enter symbols (comma-separated, e.g., AAPL,MSFT,GOOGL)",
                        id="custom-symbols"
                    )
                    
                    yield DownloadProgress(id="download-progress")
            
            with TabPane("📊 Cache", id="cache-tab"):
                yield CacheViewer(id="cache-viewer")
            
            with TabPane("📋 Watchlist", id="watchlist-tab"):
                yield WatchlistManager(id="watchlist-manager")
        
        yield Footer()
    
    def on_mount(self):
        """Initialize the interface"""
        if not self.alpaca_provider:
            self.notify("❌ AlpacaProvider not available. Check API credentials.")
        
        if not self.cache:
            self.notify("❌ PriceCacheV2 not available. Check database.")
        
        # Load watchlist
        watchlist_manager = self.query_one("#watchlist-manager", WatchlistManager)
        watchlist_manager.load_watchlist()
        
        # Load cache stats
        if self.cache:
            cache_viewer = self.query_one("#cache-viewer", CacheViewer)
            cache_viewer.update_cache_stats(self.cache)
    
    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "download-watchlist":
            await self._download_watchlist()
        
        elif button_id == "download-custom":
            await self._download_custom()
        
        elif button_id == "save-watchlist":
            watchlist_manager = self.query_one("#watchlist-manager", WatchlistManager)
            watchlist_manager.save_watchlist()
        
        elif button_id == "reload-watchlist":
            watchlist_manager = self.query_one("#watchlist-manager", WatchlistManager)
            watchlist_manager.load_watchlist()
        
        elif button_id == "add-symbol":
            symbol_input = self.query_one("#symbol-input", Input)
            symbol = symbol_input.value.strip().upper()
            if symbol:
                watchlist_manager = self.query_one("#watchlist-manager", WatchlistManager)
                watchlist_manager.add_symbol(symbol)
                symbol_input.value = ""
        
        elif button_id == "refresh-cache-stats":
            if self.cache:
                cache_viewer = self.query_one("#cache-viewer", CacheViewer)
                cache_viewer.update_cache_stats(self.cache)
    
    @work(exclusive=True)
    async def _download_watchlist(self):
        """Download data for all symbols in watchlist"""
        if not self.alpaca_provider:
            self.notify("❌ AlpacaProvider not available")
            return
        
        try:
            # Get symbols from watchlist
            watchlist_manager = self.query_one("#watchlist-manager", WatchlistManager)
            symbols = watchlist_manager.get_symbols()
            
            if not symbols:
                self.notify("❌ No symbols in watchlist")
                return
            
            # Get interval
            interval_select = self.query_one("#interval-select", Select)
            interval = str(interval_select.value)
            
            await self._perform_download(symbols, interval)
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            self.notify(f"❌ Download failed: {e}")
    
    @work(exclusive=True)
    async def _download_custom(self):
        """Download custom symbols"""
        if not self.alpaca_provider:
            self.notify("❌ AlpacaProvider not available")
            return
        
        try:
            # Get custom symbols
            custom_input = self.query_one("#custom-symbols", Input)
            symbols_text = custom_input.value.strip()
            
            if not symbols_text:
                self.notify("❌ Enter symbols to download")
                return
            
            symbols = [s.strip().upper() for s in symbols_text.split(',') if s.strip()]
            
            # Get interval
            interval_select = self.query_one("#interval-select", Select)
            interval = str(interval_select.value)
            
            await self._perform_download(symbols, interval)
            
        except Exception as e:
            logger.error(f"Custom download failed: {e}")
            self.notify(f"❌ Download failed: {e}")
    
    async def _perform_download(self, symbols: List[str], interval: str):
        """Perform the actual download"""
        progress = self.query_one("#download-progress", DownloadProgress)
        progress.start_download(len(symbols))
        
        success_count = 0
        error_count = 0
        
        for i, symbol in enumerate(symbols):
            try:
                progress.update_progress(symbol, i, len(symbols))
                
                # Download data
                data = self.alpaca_provider.get_historical_data(
                    symbol=symbol,
                    interval=interval,
                    start=datetime.now() - timedelta(days=365),
                    end=datetime.now()
                )
                
                if not data.empty:
                    success_count += 1
                    logger.info(f"Downloaded {len(data)} records for {symbol}")
                else:
                    error_count += 1
                    logger.warning(f"No data for {symbol}")
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to download {symbol}: {e}")
        
        progress.finish_download(success_count, error_count)
        
        # Refresh cache stats
        if self.cache:
            cache_viewer = self.query_one("#cache-viewer", CacheViewer)
            cache_viewer.update_cache_stats(self.cache)
        
        self.notify(f"✅ Download complete: {success_count} success, {error_count} errors")
    
    def action_focus_download(self):
        """Focus download tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "download-tab"
    
    def action_focus_cache(self):
        """Focus cache tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "cache-tab"
    
    def action_focus_watchlist(self):
        """Focus watchlist tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "watchlist-tab"


def main():
    """Run the price downloader interface"""
    try:
        app = PriceDownloaderInterface()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()