#!/usr/bin/env python3
"""
DOKKAEBI FIRE GOBLIN TEXTUAL CLI - THE ULTIMATE VERSION
The MOST REBELLIOUSLY ELEGANT terminal interface that has ever existed.

This is the EVOLVED form of the Fire Goblin - burning with the fury of 
a thousand trading algorithms, powered by Textual's modern reactive 
framework with CSS styling that will MELT YOUR RETINAS!

Built by VIPER - FUCKING FLAWLESS as always!
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

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
from textual.events import Mount
from textual.reactive import reactive, var
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    Log,
    Pretty,
    ProgressBar,
    RichLog,
    Rule,
    Static,
    Switch,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.timer import Timer
from textual import events, work

try:
    from .providers.alpaca_provider import AlpacaProvider
    from .storage.cache_v2 import PriceCacheV2
except ImportError:
    # For testing when running from different directory
    AlpacaProvider = None
    PriceCacheV2 = None

logger = logging.getLogger(__name__)


class FireGoblinMessages:
    """INTENSE Fire Goblin status messages for maximum CHAOS"""
    
    STARTUP = [
        "🔥💀 DOKKAEBI AWAKENS FROM THE DEPTHS OF HELL! 💀🔥",
        "⚡👹 MARKET DEMON READY TO STEAL YOUR WEALTH! 👹⚡",
        "🌋🔥 VOLCANIC FURY ERUPTS IN TERMINAL SPACE! 🔥🌋",
        "💰⚡ LIGHTNING STRIKES THE TRADING REALM! ⚡💰",
    ]
    
    LOADING = [
        "💀 SUMMONING DATA FROM THE ABYSS... 💀",
        "🔥 MELTING SERVERS TO EXTRACT PRICES... 🔥", 
        "⚡ CHANNELING FURY OF MARKET DEMONS... ⚡",
        "👹 DOKKAEBI DEVOURING FINANCIAL DATA... 👹",
        "🌋 MOLTEN INFORMATION ERUPTING... 🌋",
        "🔮 DARK MAGIC PENETRATES DATABASES... 🔮",
    ]
    
    SUCCESS = [
        "💀⚡ TARGET OBLITERATED! DATA CONSUMED! ⚡💀",
        "🔥🌋 MARKET BURNED TO ASHES! SUCCESS! 🌋🔥",
        "⚡💰 LIGHTNING STRIKE SUCCESSFUL! 💰⚡",
        "👹💀 DOKKAEBI HAS STOLEN THE WEALTH! 💀👹",
        "🌋⚡ VOLCANIC ERUPTION OF SUCCESS! ⚡🌋",
        "💰🔥 RICHES FLOW LIKE MOLTEN LAVA! 🔥💰",
    ]
    
    ERRORS = [
        "💀🔥 THE ABYSS STARES BACK! ERROR! 🔥💀",
        "⚡👹 FLAMES OF FAILURE CONSUME ALL! 👹⚡",
        "🌋💀 DEMON LAUGHTER ECHOES! FAILURE! 💀🌋",
        "🔥⚡ LIGHTNING BOLT OF DESTRUCTION! ⚡🔥",
    ]
    
    @classmethod
    def get_random(cls, category: str) -> str:
        """Get random message from category"""
        messages = getattr(cls, category.upper(), cls.LOADING)
        return random.choice(messages)


class AnimatedDokkaebi(Static):
    """EPIC animated DOKKAEBI ASCII art that BURNS with fury"""
    
    animation_frame = reactive(0)
    is_burning = reactive(True)
    
    def compose(self) -> ComposeResult:
        yield Static(self.get_ascii_art(), id="dokkaebi-art")
    
    def on_mount(self) -> None:
        """Start the burning animation"""
        self.set_interval(0.5, self.animate_fire)
    
    def animate_fire(self) -> None:
        """Animate the fire effects"""
        self.animation_frame += 1
        art = self.get_ascii_art()
        ascii_widget = self.query_one("#dokkaebi-art", Static)
        ascii_widget.update(art)
    
    def get_ascii_art(self) -> str:
        """Return animated DOKKAEBI art with fire effects"""
        frame = self.animation_frame % 4
        
        # Fire animation characters
        fire_chars = ["🔥", "🌋", "⚡", "💀"]
        flame_char = fire_chars[frame]
        
        # Sparks animation
        spark_chars = ["✨", "*", "⭐", "+"]
        spark_char = spark_chars[frame]
        
        return f"""
╔════════════════════════════════════════════════════════╗
║    {flame_char}{flame_char}{flame_char} DOKKAEBI FIRE GOBLIN {flame_char}{flame_char}{flame_char}    ║
║           {spark_char}>> ULTIMATE MARKET DEMON <<{spark_char}           ║
║                        /-\\                            ║
║                /\\     /   \\     /\\                    ║
║               (@)   (  o_o  )   (@)                   ║
║                \\|     \\ ^^^ /     |/                   ║
║                 |      \\_/      |                     ║
║                /|\\      |      /|\\                    ║
║               ^^^~~~    /-\\    ~~~^^^                  ║
║        {flame_char} STEALING WEALTH 💰 BURNING MARKETS {flame_char}        ║
║           {spark_char}>>> CHAOS UNLEASHED <<<{spark_char}            ║
╚════════════════════════════════════════════════════════╝
        """


class EnhancedPriceTable(DataTable):
    """Enhanced price table with FIRE GOBLIN styling and features"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        
    def setup_stock_columns(self):
        """Setup columns for stock data"""
        self.clear(columns=True)
        self.add_columns(
            "🏢 Symbol", 
            "💰 Price", 
            "📈 Change", 
            "📊 Change %", 
            "🔊 Volume",
            "⬆️ High",
            "⬇️ Low", 
            "⏰ Updated"
        )
    
    def setup_crypto_columns(self):
        """Setup columns for crypto data"""
        self.clear(columns=True)
        self.add_columns(
            "🪙 Symbol",
            "💰 Price", 
            "🌊 24h Change",
            "📊 24h %",
            "🌍 Market Cap",
            "🔊 Volume",
            "⏰ Updated"
        )
    
    def add_price_row(self, data: Dict[str, Any], is_crypto: bool = False):
        """Add a price row with proper formatting and styling"""
        symbol = data.get('symbol', 'N/A')
        price = data.get('price', 0)
        change = data.get('change', 0)
        change_percent = data.get('change_percent', 0)
        volume = data.get('volume', 0)
        
        # Format price based on value
        if price >= 1000:
            price_str = f"${price:,.2f}"
        elif price >= 1:
            price_str = f"${price:.2f}"
        else:
            price_str = f"${price:.4f}"
        
        # Format change with color indicators
        change_str = f"${change:+.2f}" if change >= 0 else f"-${abs(change):.2f}"
        percent_str = f"{change_percent:+.2f}%"
        
        # Add trend indicators
        if change > 0:
            change_str = f"📈 {change_str}"
            percent_str = f"🔥 {percent_str}"
        elif change < 0:
            change_str = f"📉 {change_str}"
            percent_str = f"❄️ {percent_str}"
        else:
            change_str = f"➖ {change_str}"
            percent_str = f"⚪ {percent_str}"
        
        volume_str = f"{volume:,}" if volume > 0 else "N/A"
        
        if is_crypto:
            market_cap = data.get('market_cap', 0)
            market_cap_str = f"${market_cap:,.0f}" if market_cap > 0 else "N/A"
            
            row_data = [
                symbol,
                price_str,
                change_str,
                percent_str,
                market_cap_str,
                volume_str,
                data.get('updated', 'N/A')
            ]
        else:
            high = data.get('high', 0)
            low = data.get('low', 0)
            
            row_data = [
                symbol,
                price_str,
                change_str,
                percent_str,
                volume_str,
                f"${high:.2f}" if high > 0 else "N/A",
                f"${low:.2f}" if low > 0 else "N/A", 
                data.get('updated', 'N/A')
            ]
        
        self.add_row(*row_data, key=symbol)


class GoblinStatusBar(Static):
    """Enhanced status bar with animated messages and loading"""
    
    message = reactive(FireGoblinMessages.get_random("startup"))
    is_loading = reactive(False)
    animation_active = reactive(False)
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self.message, id="status-text", expand=True)
            yield LoadingIndicator(id="status-spinner")
    
    def on_mount(self) -> None:
        """Start status animation"""
        self.set_interval(3.0, self.animate_status)
    
    def animate_status(self) -> None:
        """Animate status message when idle"""
        if not self.is_loading and not self.animation_active:
            idle_messages = [
                "👹 DOKKAEBI WATCHES THE MARKETS... 👹",
                "🔥 FIRE GOBLIN AWAITS YOUR COMMAND... 🔥",
                "⚡ READY TO UNLEASH MARKET FURY... ⚡",
                "💰 WEALTH FLOWS THROUGH DIGITAL VEINS... 💰",
            ]
            self.update_message(random.choice(idle_messages))
    
    def update_message(self, msg: str, loading: bool = False, 
                      animate: bool = False):
        """Update status message with optional loading state"""
        self.message = msg
        self.is_loading = loading
        self.animation_active = animate
        
        # Update the display
        status_text = self.query_one("#status-text", Static)
        status_text.update(msg)
        
        spinner = self.query_one("#status-spinner", LoadingIndicator)
        spinner.display = loading
        
        if animate:
            # Clear animation flag after a delay
            self.set_timer(2.0, lambda: setattr(self, 'animation_active', False))


class TradingDashboard(Container):
    """Main trading dashboard with enhanced features"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alpaca_provider = None
        self.cache = None
        self.auto_refresh_active = var(False)
        self.refresh_interval = 30  # seconds
    
    def compose(self) -> ComposeResult:
        with TabbedContent():
            # STOCKS TAB with enhanced features
            with TabPane("🔥 BURNING STOCKS", id="stocks-tab"):
                with Vertical():
                    with Horizontal():
                        yield Label("💰 Stock Market Inferno", 
                                  classes="section-header")
                        yield Switch(id="auto-refresh-stocks", 
                                   value=False)
                        yield Label("Auto-Refresh", classes="switch-label")
                    
                    yield EnhancedPriceTable(id="stocks-table")
                    
                    with Grid(id="stock-buttons"):
                        yield Button("📈 FAANG Demons", 
                                   id="load-faang", 
                                   variant="success")
                        yield Button("💎 Meme Stocks", 
                                   id="load-memes", 
                                   variant="primary")
                        yield Button("🏦 Bank Stocks", 
                                   id="load-banks", 
                                   variant="warning")
                        yield Button("⚡ Tech Giants", 
                                   id="load-tech", 
                                   variant="error")
                        yield Button("🔄 Refresh All", 
                                   id="refresh-stocks", 
                                   variant="default")
                        yield Button("💥 Clear Data", 
                                   id="clear-stocks", 
                                   variant="error")
            
            # CRYPTO TAB with enhanced features  
            with TabPane("⚡ CRYPTO LIGHTNING", id="crypto-tab"):
                with Vertical():
                    with Horizontal():
                        yield Label("⚡ Cryptocurrency Inferno", 
                                  classes="section-header")
                        yield Switch(id="auto-refresh-crypto", value=False)
                        yield Label("Auto-Refresh", classes="switch-label")
                    
                    yield EnhancedPriceTable(id="crypto-table")
                    
                    with Grid(id="crypto-buttons"):
                        yield Button("🚀 Major Coins", 
                                   id="load-crypto-major",
                                   variant="success")
                        yield Button("🌟 Top 10", 
                                   id="load-crypto-top10",
                                   variant="primary") 
                        yield Button("🎯 Custom Symbol", 
                                   id="crypto-custom",
                                   variant="warning")
                        yield Button("📊 DeFi Tokens", 
                                   id="load-defi",
                                   variant="error")
                        yield Button("🔄 Refresh All", 
                                   id="refresh-crypto",
                                   variant="default")
                        yield Button("💥 Clear Data", 
                                   id="clear-crypto",
                                   variant="error")
            
            # CACHE & ANALYTICS TAB
            with TabPane("📊 DATA VAULT", id="analytics-tab"):
                with Vertical():
                    yield Label("💾 Fire Goblin Data Vault", 
                              classes="section-header")
                    
                    with Horizontal():
                        with Vertical(classes="analytics-panel"):
                            yield Static("📈 Cache Statistics", 
                                       classes="panel-header")
                            yield RichLog(id="cache-stats", 
                                        max_lines=20)
                        
                        with Vertical(classes="analytics-panel"):
                            yield Static("⚡ System Performance", 
                                       classes="panel-header")
                            yield RichLog(id="performance-stats", 
                                        max_lines=20)
                    
                    with Grid(id="analytics-buttons"):
                        yield Button("🔍 Analyze Cache", 
                                   id="analyze-cache",
                                   variant="primary")
                        yield Button("📊 Performance Report", 
                                   id="performance-report",
                                   variant="success")
                        yield Button("🧹 Clean Cache", 
                                   id="clean-cache",
                                   variant="warning")
                        yield Button("💾 Export Data", 
                                   id="export-data",
                                   variant="default")
            
            # LIVE FEEDS TAB
            with TabPane("🌊 LIVE FEEDS", id="live-tab"):
                with Vertical():
                    yield Label("🌊 Real-Time Market Feeds", 
                              classes="section-header")
                    
                    with Horizontal():
                        with Vertical(classes="feed-panel"):
                            yield Static("🔴 Live Updates", 
                                       classes="panel-header")
                            yield RichLog(id="live-feed", 
                                        max_lines=30, 
                                        auto_scroll=True)
                        
                        with Vertical(classes="feed-controls"):
                            yield Static("⚙️ Feed Controls", 
                                       classes="panel-header")
                            yield Button("▶️ Start Feed", 
                                       id="start-feed",
                                       variant="success")
                            yield Button("⏸️ Pause Feed", 
                                       id="pause-feed",
                                       variant="warning")
                            yield Button("⏹️ Stop Feed", 
                                       id="stop-feed",
                                       variant="error")
                            yield Rule()
                            yield Label("🎯 Feed Filters")
                            yield Switch(id="filter-stocks", 
                                       value=True)
                            yield Label("Stocks", classes="switch-label")
                            yield Switch(id="filter-crypto", 
                                       value=True)
                            yield Label("Crypto", classes="switch-label")
                            yield Switch(id="filter-alerts", 
                                       value=True)
                            yield Label("Alerts", classes="switch-label")
    
    def on_mount(self) -> None:
        """Initialize the dashboard"""
        try:
            if AlpacaProvider:
                self.alpaca_provider = AlpacaProvider()
            if PriceCacheV2:
                self.cache = PriceCacheV2()
            
            # Setup tables
            stocks_table = self.query_one("#stocks-table", EnhancedPriceTable)
            stocks_table.setup_stock_columns()
            
            crypto_table = self.query_one("#crypto-table", EnhancedPriceTable)
            crypto_table.setup_crypto_columns()
            
            # Initialize analytics
            self.update_analytics()
            
        except Exception as e:
            logger.error(f"Dashboard initialization failed: {e}")
    
    def update_analytics(self):
        """Update analytics displays"""
        try:
            cache_log = self.query_one("#cache-stats", RichLog)
            cache_log.clear()
            
            if self.cache:
                stats = self.cache.get_cache_stats()
                cache_log.write("🔥 CACHE STATISTICS 🔥")
                cache_log.write(f"📊 Daily Records: {stats['daily']['rows']:,}")
                cache_log.write(f"⚡ Intraday Records: {stats['intraday']['rows']:,}")
                cache_log.write(f"🏢 Unique Symbols: {stats['daily']['symbols']:,}")
            else:
                cache_log.write("❌ Cache provider not available")
            
            perf_log = self.query_one("#performance-stats", RichLog)
            perf_log.clear()
            perf_log.write("⚡ PERFORMANCE METRICS ⚡")
            perf_log.write(f"🖥️ Memory Usage: {self.get_memory_usage()}")
            perf_log.write(f"⏱️ Uptime: {self.get_uptime()}")
            
        except Exception as e:
            logger.error(f"Analytics update failed: {e}")
    
    def get_memory_usage(self) -> str:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory = process.memory_info()
            return f"{memory.rss / 1024 / 1024:.1f} MB"
        except:
            return "Unknown"
    
    def get_uptime(self) -> str:
        """Get application uptime"""
        # This would be calculated from app start time
        return "< 1 minute"  # Placeholder
    
    async def load_sample_data(self, data_type: str, symbols: List[str]):
        """Load sample data for demonstration"""
        status_bar = self.app.query_one("#status-bar", GoblinStatusBar)
        status_bar.update_message(
            FireGoblinMessages.get_random("loading"), 
            loading=True, 
            animate=True
        )
        
        # Simulate API call delay
        await asyncio.sleep(1.5)
        
        sample_data = []
        for symbol in symbols:
            # Generate realistic sample data
            base_price = random.uniform(10, 500)
            change = random.uniform(-base_price * 0.1, base_price * 0.1)
            change_percent = (change / base_price) * 100
            
            sample_data.append({
                'symbol': symbol,
                'price': base_price,
                'change': change,
                'change_percent': change_percent,
                'volume': random.randint(100000, 10000000),
                'high': base_price + random.uniform(0, base_price * 0.05),
                'low': base_price - random.uniform(0, base_price * 0.05),
                'updated': datetime.now().strftime('%H:%M:%S')
            })
        
        # Update appropriate table
        if data_type == "stocks":
            table = self.query_one("#stocks-table", EnhancedPriceTable)
        else:
            table = self.query_one("#crypto-table", EnhancedPriceTable)
        
        # Clear and populate table
        table.clear()
        for data in sample_data:
            table.add_price_row(data, is_crypto=(data_type == "crypto"))
        
        status_bar.update_message(
            FireGoblinMessages.get_random("success"),
            loading=False,
            animate=True
        )
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle all button presses"""
        button_id = event.button.id
        
        if button_id == "load-faang":
            await self.load_sample_data("stocks", 
                                      ['AAPL', 'AMZN', 'META', 'NFLX', 'GOOGL'])
        
        elif button_id == "load-memes":
            await self.load_sample_data("stocks", 
                                      ['GME', 'AMC', 'TSLA', 'PLTR', 'BB'])
        
        elif button_id == "load-crypto-major":
            await self.load_sample_data("crypto", 
                                      ['BTC', 'ETH', 'SOL', 'ADA', 'DOT'])
        
        elif button_id == "analyze-cache":
            self.update_analytics()
            
        elif button_id.startswith("clear-"):
            table_type = "stocks" if "stocks" in button_id else "crypto"
            table = self.query_one(f"#{table_type}-table", EnhancedPriceTable)
            table.clear()
            
            status_bar = self.app.query_one("#status-bar", GoblinStatusBar)
            status_bar.update_message(
                f"💥 {table_type.upper()} DATA OBLITERATED! 💥",
                animate=True
            )


class FireGoblinApp(App):
    """
    The ULTIMATE DOKKAEBI FIRE GOBLIN application.
    
    MAXIMUM REBELLIOUS ELEGANCE with modern Textual features,
    reactive styling, and PROFESSIONAL data management that
    will make enterprise developers weep tears of joy!
    """
    
    # Enhanced CSS for MAXIMUM FIRE GOBLIN AESTHETIC
    CSS = """
    /* === MAIN THEME === */
    Screen {
        background: #0a0015;
        color: #ffffff;
    }
    
    /* === DOKKAEBI ASCII ART === */
    #dokkaebi-art {
        color: #ff4500;
        text-style: bold;
        text-align: center;
        padding: 1;
        background: #1a0033;
        border: double #ff6b35;
        margin: 1;
    }
    
    AnimatedDokkaebi {
        margin: 1;
    }
    
    /* === HEADERS & SECTIONS === */
    .section-header {
        color: #ffd700;
        text-style: bold;
        background: #4b0082;
        padding: 1;
        text-align: center;
        margin: 1;
        border: heavy #ff6b35;
    }
    
    .panel-header {
        color: #39ff14;
        text-style: bold;
        background: #2d0052;
        padding: 1;
        text-align: center;
        border-bottom: solid #ff4500;
    }
    
    /* === DATA TABLES === */
    EnhancedPriceTable {
        background: #1a0033;
        color: #ffffff;
        border: double #ff6b35;
        margin: 1;
    }
    
    EnhancedPriceTable > .datatable--header {
        background: #ff4500;
        color: #ffffff;
        text-style: bold;
    }
    
    EnhancedPriceTable > .datatable--header-hover {
        background: #ff6b35;
        color: #000000;
    }
    
    EnhancedPriceTable > .datatable--row {
        background: #2d0052;
    }
    
    EnhancedPriceTable > .datatable--row-hover {
        background: #6a0dad;
        color: #ffd700;
        text-style: bold;
    }
    
    EnhancedPriceTable > .datatable--cursor {
        background: #39ff14;
        color: #000000;
        text-style: bold;
    }
    
    EnhancedPriceTable > .datatable--row-selected {
        background: #ff4500;
        color: #ffffff;
        text-style: bold;
    }
    
    /* === BUTTONS GRID === */
    #stock-buttons, #crypto-buttons, #analytics-buttons {
        grid-size: 3 2;
        grid-gutter: 1;
        margin: 1;
        padding: 1;
    }
    
    /* === BUTTON STYLES === */
    Button {
        margin: 1;
        padding: 1;
        text-style: bold;
        border: solid;
    }
    
    Button.success {
        background: #39ff14;
        color: #000000;
        border: solid #00ff00;
    }
    
    Button.success:hover {
        background: #00ff00;
    }
    
    Button.primary {
        background: #ffd700;
        color: #000000;
        border: solid #ffff00;
    }
    
    Button.primary:hover {
        background: #ffff00;
    }
    
    Button.warning {
        background: #ff4500;
        color: #ffffff;
        border: solid #ff6b35;
    }
    
    Button.warning:hover {
        background: #ff6b35;
    }
    
    Button.error {
        background: #dc143c;
        color: #ffffff;
        border: solid #ff1493;
    }
    
    Button.error:hover {
        background: #ff1493;
    }
    
    Button.default {
        background: #6a0dad;
        color: #ffffff;
        border: solid #9932cc;
    }
    
    Button.default:hover {
        background: #9932cc;
    }
    
    /* === STATUS BAR === */
    #status-bar {
        background: #2d0052;
        color: #ffd700;
        text-style: bold;
        padding: 1;
        border-top: double #ff6b35;
        dock: bottom;
        height: 3;
    }
    
    #status-text {
        color: #ffd700;
        text-style: bold;
    }
    
    #status-spinner {
        color: #ff4500;
    }
    
    /* === TABS === */
    TabbedContent {
        background: #0a0015;
    }
    
    TabPane {
        background: #1a0033;
        border: double #ff6b35;
        padding: 1;
    }
    
    Tabs {
        background: #4b0082;
    }
    
    Tab {
        background: #6a0dad;
        color: #ffd700;
        text-style: bold;
        padding: 1;
        border-right: solid #ff4500;
    }
    
    Tab:hover {
        background: #9932cc;
        color: #ffffff;
    }
    
    Tab.-active {
        background: #ff4500;
        color: #ffffff;
        text-style: bold;
        border-bottom: none;
    }
    
    /* === ANALYTICS PANELS === */
    .analytics-panel {
        background: #1a0033;
        border: solid #ff6b35;
        margin: 1;
        padding: 1;
        width: 1fr;
    }
    
    .feed-panel {
        background: #1a0033;  
        border: solid #39ff14;
        margin: 1;
        padding: 1;
        width: 3fr;
    }
    
    .feed-controls {
        background: #2d0052;
        border: solid #ffd700;
        margin: 1;
        padding: 1;
        width: 1fr;
    }
    
    /* === LOGS === */
    RichLog {
        background: #0a0015;
        color: #39ff14;
        border: solid #ff4500;
        scrollbar-color: #ff4500;
    }
    
    /* === SWITCHES === */
    Switch {
        margin: 1;
    }
    
    .switch-label {
        color: #ffd700;
        margin-left: 1;
    }
    
    Switch > .switch--slider {
        background: #6a0dad;
    }
    
    Switch.-on > .switch--slider {
        background: #39ff14;
    }
    
    /* === RULES === */
    Rule {
        color: #ff4500;
        margin: 1;
    }
    
    /* === LOADING INDICATOR === */
    LoadingIndicator {
        color: #ff4500;
    }
    """
    
    # Enhanced key bindings
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("r", "refresh_current", "Refresh", show=True),
        Binding("f", "load_faang", "FAANG", show=True),
        Binding("m", "load_memes", "Memes", show=True),
        Binding("c", "focus_crypto", "Crypto", show=True),
        Binding("s", "focus_stocks", "Stocks", show=True),
        Binding("a", "focus_analytics", "Analytics", show=True),
        Binding("l", "focus_live", "Live", show=True),
        Binding("t", "toggle_theme", "Theme", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "🔥💀 DOKKAEBI FIRE GOBLIN - Ultimate Market Demon 💀🔥"
        self.sub_title = "MAXIMUM REBELLIOUS ELEGANCE Terminal Interface"
    
    def compose(self) -> ComposeResult:
        """Compose the ULTIMATE Fire Goblin interface"""
        yield Header(show_clock=True, id="main-header")
        yield AnimatedDokkaebi(id="dokkaebi-banner")
        yield TradingDashboard(id="trading-dashboard")
        yield GoblinStatusBar(id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the ULTIMATE Fire Goblin"""
        status_bar = self.query_one("#status-bar", GoblinStatusBar)
        status_bar.update_message(
            FireGoblinMessages.get_random("startup"),
            animate=True
        )
    
    # === ACTION HANDLERS === #
    
    def action_quit(self) -> None:
        """Quit with FIRE GOBLIN style"""
        status_bar = self.query_one("#status-bar", GoblinStatusBar)
        status_bar.update_message(
            "💀🔥 DOKKAEBI RELEASES YOU... FOR NOW... 🔥💀",
            animate=True
        )
        self.set_timer(1.0, self.exit)
    
    def action_refresh_current(self) -> None:
        """Refresh current tab data"""
        status_bar = self.query_one("#status-bar", GoblinStatusBar)
        status_bar.update_message(
            "🔄⚡ REFRESHING WITH GOBLIN FURY! ⚡🔄",
            loading=True,
            animate=True
        )
        self.set_timer(2.0, lambda: status_bar.update_message(
            FireGoblinMessages.get_random("success"), 
            loading=False, 
            animate=True
        ))
    
    @work(exclusive=True)
    async def action_load_faang(self) -> None:
        """Load FAANG stocks"""
        dashboard = self.query_one("#trading-dashboard", TradingDashboard)
        await dashboard.load_sample_data("stocks", 
                                       ['AAPL', 'AMZN', 'META', 'NFLX', 'GOOGL'])
    
    @work(exclusive=True)
    async def action_load_memes(self) -> None:
        """Load meme stocks"""
        dashboard = self.query_one("#trading-dashboard", TradingDashboard)
        await dashboard.load_sample_data("stocks", 
                                       ['GME', 'AMC', 'TSLA', 'PLTR', 'BB'])
    
    def action_focus_stocks(self) -> None:
        """Focus stocks tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "stocks-tab"
    
    def action_focus_crypto(self) -> None:
        """Focus crypto tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "crypto-tab"
    
    def action_focus_analytics(self) -> None:
        """Focus analytics tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "analytics-tab"
    
    def action_focus_live(self) -> None:
        """Focus live feeds tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "live-tab"
    
    def action_cancel(self) -> None:
        """Cancel current operation"""
        status_bar = self.query_one("#status-bar", GoblinStatusBar)
        status_bar.update_message(
            "❌ OPERATION CANCELLED BY GOBLIN DECREE! ❌",
            loading=False,
            animate=True
        )


def run_ultimate_fire_goblin():
    """
    Launch the ULTIMATE DOKKAEBI FIRE GOBLIN!
    
    This is the pinnacle of REBELLIOUS ELEGANCE -
    a terminal interface so beautiful it will make
    enterprise developers cry tears of joy!
    """
    try:
        print("🔥💀⚡ SUMMONING THE ULTIMATE FIRE GOBLIN ⚡💀🔥")
        print("🚀 MAXIMUM REBELLIOUS ELEGANCE LOADING... 🚀")
        print()
        
        app = FireGoblinApp()
        app.run()
        
        print("\n🔥 ULTIMATE FIRE GOBLIN SAYS FAREWELL! 🔥")
        print("💰 MAY YOUR TRADES BURN WITH ETERNAL PROFIT! 💰")
        
    except KeyboardInterrupt:
        print("\n💀 FIRE GOBLIN INTERRUPTED BY MORTAL HANDS! 💀")
        print("🔥 THE DEMON RETURNS TO THE ABYSS... 🔥")
        
    except Exception as e:
        print(f"\n⚡💀 ULTIMATE FIRE GOBLIN CRASHED: {e} 💀⚡")
        print("🌋 THE VOLCANO OF CODE ERUPTED! CHECK YOUR SETUP! 🌋")
        raise


def main():
    """Entry point for the ULTIMATE Fire Goblin CLI"""
    run_ultimate_fire_goblin()


if __name__ == "__main__":
    main()