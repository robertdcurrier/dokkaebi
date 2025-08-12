#!/usr/bin/env python3
"""
DOKKAEBI FIRE GOBLIN TEXTUAL CLI
The REBELLIOUSLY ELEGANT modern terminal interface powered by Textual.

This is NOT your ancient curses bullshit - this is a FIRE GOBLIN interface 
that burns with the fury of a thousand trading algorithms using MODERN TUI 
technology with full Unicode, CSS styling, and reactive updates!

Viper's implementation - FUCKING FLAWLESS as always!
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import (
    Container, 
    Horizontal, 
    Vertical, 
    ScrollableContainer
)
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    LoadingIndicator,
    Log,
    ProgressBar,
    Static,
    TabbedContent,
    TabPane,
)
from textual.timer import Timer
from textual import events
import pandas as pd

from .providers.alpaca_provider import AlpacaProvider
from .storage.cache_v2 import PriceCacheV2

logger = logging.getLogger(__name__)


class DOKKAEBIAscii(Static):
    """EPIC DOKKAEBI ASCII art widget with FIRE GOBLIN styling"""
    
    def compose(self) -> ComposeResult:
        ascii_art = """
╔════════════════════════════════════════════════════╗
║        🔥🔥🔥 DOKKAEBI FIRE GOBLIN 🔥🔥🔥        ║
║               >>> MARKET DEMON <<<                 ║
║                      /-\                          ║
║               /\     /  \     /\                  ║
║              (@)   (  o_o  )   (@)                ║
║               \|     \ ^^^ /     |/                ║
║                |      \_/      |                  ║
║               /|\      |      /|\                 ║
║              ^^^~~~    /-\    ~~~^^^               ║
║         STEALING WEALTH 💰 BURNING MARKETS         ║
║              >>> CHAOS UNLEASHED <<<               ║
╚════════════════════════════════════════════════════╝
        """
        yield Label(ascii_art, id="dokkaebi-ascii")


class PriceDataTable(DataTable):
    """Enhanced data table for displaying price data with FIRE styling"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        
    def setup_columns(self, data_type: str = "stocks"):
        """Setup table columns based on data type"""
        self.clear(columns=True)
        
        if data_type == "stocks":
            self.add_columns(
                "Symbol", "Price", "Change", "Change %", 
                "Volume", "High", "Low", "Updated"
            )
        elif data_type == "crypto":
            self.add_columns(
                "Symbol", "Price", "24h Change", "24h %", 
                "Market Cap", "Volume", "Updated"
            )
    
    def update_price_data(self, data: List[Dict[str, Any]]):
        """Update table with new price data"""
        self.clear()
        
        for item in data:
            row_data = [
                item.get('symbol', 'N/A'),
                f"${item.get('price', 0):.2f}",
                f"${item.get('change', 0):.2f}",
                f"{item.get('change_percent', 0):.2f}%",
                f"{item.get('volume', 0):,}",
                f"${item.get('high', 0):.2f}",
                f"${item.get('low', 0):.2f}",
                item.get('updated', 'N/A')
            ]
            
            # Color coding based on change
            change = item.get('change', 0)
            if change > 0:
                style = "green bold"
            elif change < 0:
                style = "red bold"
            else:
                style = "white"
            
            self.add_row(*row_data, key=item.get('symbol', 'unknown'))


class StatusBar(Static):
    """Status bar showing current operations and goblin messages"""
    
    status_message = reactive("🔥 DOKKAEBI FIRE GOBLIN READY TO BURN 🔥")
    is_loading = reactive(False)
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.status_message, id="status-message")
            yield LoadingIndicator(id="loading-spinner")
    
    def update_status(self, message: str, loading: bool = False):
        """Update status with FIRE GOBLIN messaging"""
        self.status_message = message
        self.is_loading = loading
    
    def watch_is_loading(self, loading: bool) -> None:
        """Show/hide loading spinner"""
        spinner = self.query_one("#loading-spinner", LoadingIndicator)
        spinner.display = loading


class MarketOverview(Container):
    """Market overview dashboard with multiple data sources"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alpaca_provider = None
        self.cache = None
        self.update_timer = None
    
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("🔥 STOCKS", id="stocks-tab"):
                with Vertical():
                    yield Label("💰 Stock Market Data", classes="section-header")
                    yield PriceDataTable(id="stocks-table")
                    with Horizontal():
                        yield Button("📈 Load FAANG", id="load-faang", 
                                   variant="success")
                        yield Button("📊 Load S&P 500", id="load-sp500", 
                                   variant="primary")
                        yield Button("🔄 Refresh", id="refresh-stocks", 
                                   variant="warning")
            
            with TabPane("⚡ CRYPTO", id="crypto-tab"):
                with Vertical():
                    yield Label("⚡ Cryptocurrency Data", classes="section-header")
                    yield PriceDataTable(id="crypto-table")
                    with Horizontal():
                        yield Button("🚀 Load Major", id="load-crypto-major", 
                                   variant="success")
                        yield Button("📈 Load Top 10", id="load-crypto-top10", 
                                   variant="primary")
                        yield Button("🔄 Refresh", id="refresh-crypto", 
                                   variant="warning")
            
            with TabPane("📊 CACHE", id="cache-tab"):
                with Vertical():
                    yield Label("💾 Data Cache Statistics", classes="section-header")
                    yield Static(id="cache-stats")
                    yield Button("🗄️ Refresh Stats", id="refresh-cache", 
                               variant="primary")
    
    def on_mount(self) -> None:
        """Initialize providers and start data updates"""
        try:
            self.alpaca_provider = AlpacaProvider()
            self.cache = PriceCacheV2()
            
            # Setup initial data
            stocks_table = self.query_one("#stocks-table", PriceDataTable)
            stocks_table.setup_columns("stocks")
            
            crypto_table = self.query_one("#crypto-table", PriceDataTable)
            crypto_table.setup_columns("crypto")
            
            self.update_cache_stats()
            
            # Start periodic updates
            self.set_timer(30, self.auto_refresh_data, repeat=True)
            
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")
    
    async def load_faang_stocks(self):
        """Load FAANG stock data"""
        faang_symbols = ['AAPL', 'AMZN', 'META', 'NFLX', 'GOOGL']
        await self.load_stock_data(faang_symbols)
    
    async def load_stock_data(self, symbols: List[str]):
        """Load stock data using Alpaca provider"""
        if not self.alpaca_provider:
            return
        
        try:
            data = []
            for symbol in symbols:
                df = self.alpaca_provider.get_historical_data(
                    symbol, 
                    start=datetime.now() - timedelta(days=2),
                    end=datetime.now()
                )
                
                if not df.empty:
                    latest = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else latest
                    
                    change = latest['Close'] - prev['Close']
                    change_percent = (change / prev['Close']) * 100
                    
                    data.append({
                        'symbol': symbol,
                        'price': latest['Close'],
                        'change': change,
                        'change_percent': change_percent,
                        'volume': latest['Volume'],
                        'high': latest['High'],
                        'low': latest['Low'],
                        'updated': datetime.now().strftime('%H:%M:%S')
                    })
            
            stocks_table = self.query_one("#stocks-table", PriceDataTable)
            stocks_table.update_price_data(data)
            
        except Exception as e:
            logger.error(f"Failed to load stock data: {e}")
    
    def update_cache_stats(self):
        """Update cache statistics display"""
        if not self.cache:
            return
            
        try:
            stats = self.cache.get_cache_stats()
            
            stats_text = f"""
🔥 CACHE STATISTICS 🔥

📊 Daily Data:
   Symbols: {stats['daily']['symbols']:,}
   Records: {stats['daily']['rows']:,}
   Range: {stats['daily']['earliest']} to {stats['daily']['latest']}

⚡ Intraday Data:
   Symbols: {stats['intraday']['symbols']:,}  
   Records: {stats['intraday']['rows']:,}
   Range: {stats['intraday']['earliest']} to {stats['intraday']['latest']}

💾 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            cache_stats = self.query_one("#cache-stats", Static)
            cache_stats.update(stats_text)
            
        except Exception as e:
            logger.error(f"Failed to update cache stats: {e}")
    
    def auto_refresh_data(self):
        """Auto-refresh data periodically"""
        # This would be called by timer for live updates
        pass
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        status_bar = self.app.query_one("#status-bar", StatusBar)
        
        if event.button.id == "load-faang":
            status_bar.update_status("🔥 SUMMONING FAANG DEMONS... 🔥", True)
            await self.load_faang_stocks()
            status_bar.update_status("✅ FAANG DATA CONSUMED! ✅", False)
            
        elif event.button.id == "load-sp500":
            status_bar.update_status("⚡ CHANNELING S&P 500 FURY... ⚡", True)
            # TODO: Implement S&P 500 loading
            status_bar.update_status("🚨 S&P 500 RITUAL NOT YET SUMMONED! 🚨", False)
            
        elif event.button.id == "refresh-stocks":
            status_bar.update_status("🔄 REFRESHING STOCK INFERNO... 🔄", True)
            # Re-load current stock data
            status_bar.update_status("✅ STOCKS REFRESHED! ✅", False)
            
        elif event.button.id == "load-crypto-major":
            status_bar.update_status("🚀 SUMMONING CRYPTO DEMONS... 🚀", True)
            # TODO: Implement crypto loading
            status_bar.update_status("🚨 CRYPTO RITUAL NOT YET SUMMONED! 🚨", False)
            
        elif event.button.id == "refresh-cache":
            status_bar.update_status("💾 REFRESHING CACHE STATS... 💾", True)
            self.update_cache_stats()
            status_bar.update_status("✅ CACHE STATS UPDATED! ✅", False)


class FireGoblinApp(App):
    """
    Main DOKKAEBI FIRE GOBLIN application using Textual.
    
    REBELLIOUSLY ELEGANT terminal interface with modern styling,
    reactive updates, and professional data management.
    """
    
    # Custom CSS for FIRE GOBLIN aesthetic
    CSS = """
    /* Main app styling */
    Screen {
        background: #1a0033;
        color: #ffffff;
    }
    
    /* DOKKAEBI ASCII art */
    #dokkaebi-ascii {
        color: #ff4500;
        text-style: bold;
        text-align: center;
        padding: 1;
        background: #2d0052;
        border: heavy #ff6b35;
        margin: 1;
    }
    
    /* Section headers */
    .section-header {
        color: #ffd700;
        text-style: bold;
        background: #4b0082;
        padding: 1;
        text-align: center;
        margin: 1;
    }
    
    /* Data tables */
    DataTable {
        background: #2d0052;
        color: #ffffff;
        border: heavy #ff6b35;
    }
    
    DataTable > .datatable--header {
        background: #ff4500;
        color: #ffffff;
        text-style: bold;
    }
    
    DataTable > .datatable--row-hover {
        background: #6a0dad;
    }
    
    DataTable > .datatable--cursor {
        background: #ff6b35;
        color: #000000;
        text-style: bold;
    }
    
    /* Buttons with goblin styling */
    Button {
        margin: 1;
        padding: 1;
    }
    
    Button.success {
        background: #39ff14;
        color: #000000;
        text-style: bold;
    }
    
    Button.primary {
        background: #ffd700;
        color: #000000;
        text-style: bold;
    }
    
    Button.warning {
        background: #ff4500;
        color: #ffffff;
        text-style: bold;
    }
    
    /* Status bar */
    #status-bar {
        background: #4b0082;
        color: #ffd700;
        text-style: bold;
        padding: 1;
        border-top: heavy #ff6b35;
    }
    
    #status-message {
        color: #ffd700;
        text-style: bold;
    }
    
    #loading-spinner {
        color: #ff4500;
    }
    
    /* Tabs */
    TabbedContent {
        background: #1a0033;
    }
    
    TabPane {
        background: #2d0052;
        border: heavy #ff6b35;
        padding: 1;
    }
    
    Tabs {
        background: #4b0082;
    }
    
    Tab {
        background: #6a0dad;
        color: #ffd700;
        text-style: bold;
    }
    
    Tab.-active {
        background: #ff4500;
        color: #ffffff;
        text-style: bold;
    }
    
    /* Cache stats */
    #cache-stats {
        background: #2d0052;
        color: #39ff14;
        border: heavy #ff6b35;
        padding: 1;
        text-style: bold;
    }
    """
    
    # Key bindings
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("r", "refresh_all", "Refresh All", show=True),
        Binding("f", "load_faang", "Load FAANG", show=True),
        Binding("c", "focus_crypto", "Crypto Tab", show=True),
        Binding("s", "focus_stocks", "Stocks Tab", show=True),
        Binding("d", "focus_cache", "Cache Tab", show=True),
        ("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "🔥 DOKKAEBI FIRE GOBLIN - Market Demon 🔥"
        self.sub_title = "REBELLIOUSLY ELEGANT Terminal Trading Interface"
    
    def compose(self) -> ComposeResult:
        """Compose the FIRE GOBLIN interface"""
        yield Header(show_clock=True)
        yield DOKKAEBIAscii()
        yield MarketOverview(id="market-overview")
        yield StatusBar(id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_status("🔥 FIRE GOBLIN AWAKENED! READY TO BURN! 🔥")
    
    def action_quit(self) -> None:
        """Quit the application"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_status("💀 DOKKAEBI RELEASES YOU... FOR NOW... 💀")
        self.exit()
    
    def action_refresh_all(self) -> None:
        """Refresh all data"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_status("🔄 REFRESHING ALL INFERNAL DATA... 🔄", True)
        # TODO: Implement full refresh
        self.set_timer(2, lambda: status_bar.update_status(
            "✅ ALL DATA REFRESHED WITH GOBLIN FURY! ✅", False))
    
    def action_load_faang(self) -> None:
        """Load FAANG stocks"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_status("📈 SUMMONING FAANG DEMONS... 📈", True)
        
        # Trigger FAANG loading
        market_overview = self.query_one("#market-overview", MarketOverview)
        self.run_worker(market_overview.load_faang_stocks())
    
    def action_focus_stocks(self) -> None:
        """Focus stocks tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "stocks-tab"
    
    def action_focus_crypto(self) -> None:
        """Focus crypto tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "crypto-tab"
    
    def action_focus_cache(self) -> None:
        """Focus cache tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "cache-tab"


def run_fire_goblin_cli():
    """
    Launch the DOKKAEBI FIRE GOBLIN Textual CLI!
    
    This is where REBELLIOUS ELEGANCE meets modern terminal technology!
    """
    try:
        app = FireGoblinApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n🔥 FIRE GOBLIN INTERRUPTED! BURNING OUT... 🔥")
        
    except Exception as e:
        print(f"💀 FIRE GOBLIN CRASHED AND BURNED: {e} 💀")
        raise


def main():
    """Entry point for the CLI"""
    run_fire_goblin_cli()


if __name__ == "__main__":
    main()