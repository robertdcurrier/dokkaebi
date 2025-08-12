"""
Market Data Fetcher - Real-time price and technical indicators
Gets the raw data we need to identify opportunities
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
# import ta  # Commented out - using simplified technical indicators
from functools import lru_cache
import asyncio
import aiohttp


class MarketDataFetcher:
    """
    Fetches and processes market data for analysis
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = timedelta(minutes=5)
        
    def get_ticker_data(self, ticker: str, period: str = '1mo') -> Dict:
        """
        Get comprehensive market data for a ticker
        """
        # Check cache
        if self._is_cached(ticker):
            return self.cache[ticker]
        
        try:
            # Fetch data from yfinance
            stock = yf.Ticker(ticker)
            
            # Get historical data
            hist = stock.history(period=period)
            
            if hist.empty:
                return {}
            
            # Get current info
            info = stock.info
            
            # Calculate technical indicators
            technical = self._calculate_technicals(hist)
            
            # Calculate volume metrics
            volume_metrics = self._calculate_volume_metrics(hist)
            
            # Compile data
            data = {
                'ticker': ticker,
                'price': hist['Close'].iloc[-1],
                'open': hist['Open'].iloc[-1],
                'high': hist['High'].iloc[-1],
                'low': hist['Low'].iloc[-1],
                'volume': hist['Volume'].iloc[-1],
                'prev_close': hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[-1],
                'change': hist['Close'].iloc[-1] - (hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[-1]),
                'change_percent': self._calculate_change_percent(hist),
                'market_cap': info.get('marketCap', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float': info.get('floatShares', 0),
                'short_interest': info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0,
                'short_ratio': info.get('shortRatio', 0),
                'beta': info.get('beta', 1.0),
                **technical,
                **volume_metrics
            }
            
            # Cache the data
            self._cache_data(ticker, data)
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return {}
    
    def _calculate_technicals(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators (simplified versions)"""
        try:
            # Simple RSI calculation
            current_rsi = self._calculate_rsi(df['Close'], 14)
            
            # Simple MACD calculation
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_line = (exp1 - exp2).iloc[-1] if len(df) > 26 else 0
            signal_line = (exp1 - exp2).ewm(span=9, adjust=False).mean().iloc[-1] if len(df) > 35 else 0
            macd_histogram = macd_line - signal_line
            
            # Simple Bollinger Bands
            sma_20 = df['Close'].rolling(window=20).mean()
            std_20 = df['Close'].rolling(window=20).std()
            bb_upper = (sma_20 + (std_20 * 2)).iloc[-1] if len(df) >= 20 else df['Close'].iloc[-1]
            bb_lower = (sma_20 - (std_20 * 2)).iloc[-1] if len(df) >= 20 else df['Close'].iloc[-1]
            bb_middle = sma_20.iloc[-1] if len(df) >= 20 else df['Close'].iloc[-1]
            
            current_price = df['Close'].iloc[-1]
            
            # Calculate Bollinger position (-1 to 1)
            if bb_upper and bb_lower and bb_upper != bb_lower:
                bb_position = (current_price - bb_middle) / (bb_upper - bb_middle) if current_price > bb_middle else (current_price - bb_middle) / (bb_middle - bb_lower)
                bb_position = max(-1, min(1, bb_position))
            else:
                bb_position = 0
            
            # Moving averages
            sma_20 = df['Close'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else current_price
            sma_50 = df['Close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else current_price
            sma_200 = df['Close'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else current_price
            
            # Volume-weighted average price (VWAP)
            vwap = (df['Close'] * df['Volume']).sum() / df['Volume'].sum() if df['Volume'].sum() > 0 else current_price
            
            # Simple ATR calculation for volatility
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            current_atr = true_range.rolling(14).mean().iloc[-1] if len(df) >= 14 else 0
            
            return {
                'rsi': current_rsi,
                'macd': macd_line,
                'macd_signal': signal_line,
                'macd_histogram': macd_histogram,
                'bollinger_upper': bb_upper,
                'bollinger_lower': bb_lower,
                'bollinger_middle': bb_middle,
                'bollinger_position': bb_position,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'vwap': vwap,
                'atr': current_atr,
                'volatility': (current_atr / current_price * 100) if current_price > 0 else 0
            }
            
        except Exception as e:
            print(f"Error calculating technicals: {e}")
            return {
                'rsi': 50,
                'macd': 0,
                'macd_signal': 0,
                'macd_histogram': 0,
                'bollinger_position': 0,
                'sma_20': 0,
                'sma_50': 0,
                'sma_200': 0
            }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss if loss.iloc[-1] != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_volume_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate volume-related metrics"""
        try:
            current_volume = df['Volume'].iloc[-1]
            
            # Average volume (20-day)
            avg_volume_20 = df['Volume'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else current_volume
            
            # Volume ratio
            volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
            
            # Volume trend (increasing/decreasing)
            volume_5d = df['Volume'].rolling(window=5).mean().iloc[-1] if len(df) >= 5 else current_volume
            volume_10d = df['Volume'].rolling(window=10).mean().iloc[-1] if len(df) >= 10 else current_volume
            volume_trend = (volume_5d - volume_10d) / volume_10d * 100 if volume_10d > 0 else 0
            
            # Simple On-Balance Volume (OBV) calculation
            obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
            current_obv = obv.iloc[-1] if len(obv) > 0 else 0
            
            # Simple Money Flow Index (MFI) calculation
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            raw_money_flow = typical_price * df['Volume']
            
            positive_flow = raw_money_flow.where(typical_price > typical_price.shift(1), 0)
            negative_flow = raw_money_flow.where(typical_price < typical_price.shift(1), 0)
            
            positive_mf = positive_flow.rolling(14).sum()
            negative_mf = negative_flow.rolling(14).sum()
            
            mfi_ratio = positive_mf / negative_mf if negative_mf.iloc[-1] != 0 else 100
            current_mfi = 100 - (100 / (1 + mfi_ratio.iloc[-1])) if len(df) >= 14 else 50
            
            return {
                'avg_volume_20': avg_volume_20,
                'volume_ratio': volume_ratio,
                'volume_trend': volume_trend,
                'obv': current_obv,
                'mfi': current_mfi,
                'high_volume': volume_ratio > 2.0,
                'extreme_volume': volume_ratio > 5.0
            }
            
        except Exception as e:
            print(f"Error calculating volume metrics: {e}")
            return {
                'avg_volume_20': 0,
                'volume_ratio': 1,
                'volume_trend': 0,
                'obv': 0,
                'mfi': 50
            }
    
    def _calculate_change_percent(self, df: pd.DataFrame) -> float:
        """Calculate percentage change"""
        if len(df) < 2:
            return 0
        
        current = df['Close'].iloc[-1]
        previous = df['Close'].iloc[-2]
        
        if previous == 0:
            return 0
            
        return ((current - previous) / previous) * 100
    
    def get_options_flow(self, ticker: str) -> Dict:
        """
        Get options flow data
        Note: This is a placeholder - would need real options data API
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get option chain
            options = stock.option_chain()
            
            if options:
                calls = options.calls
                puts = options.puts
                
                # Calculate metrics
                call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
                put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0
                
                call_oi = calls['openInterest'].sum() if 'openInterest' in calls.columns else 0
                put_oi = puts['openInterest'].sum() if 'openInterest' in puts.columns else 0
                
                put_call_ratio = put_volume / call_volume if call_volume > 0 else 1
                
                # Find unusual activity (simplified)
                unusual_activity = []
                for _, row in calls.iterrows():
                    if row.get('volume', 0) > row.get('openInterest', 0) * 0.5:
                        unusual_activity.append({
                            'type': 'call',
                            'strike': row['strike'],
                            'volume': row.get('volume', 0),
                            'oi': row.get('openInterest', 0)
                        })
                
                return {
                    'call_volume': call_volume,
                    'put_volume': put_volume,
                    'total_volume': call_volume + put_volume,
                    'put_call_ratio': put_call_ratio,
                    'call_oi': call_oi,
                    'put_oi': put_oi,
                    'unusual_activity': unusual_activity[:5]  # Top 5
                }
            
            return {}
            
        except Exception as e:
            print(f"Error fetching options data for {ticker}: {e}")
            return {}
    
    def get_intraday_data(self, ticker: str, interval: str = '5m') -> pd.DataFrame:
        """Get intraday price data"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get intraday data
            intraday = stock.history(period='1d', interval=interval)
            
            return intraday
            
        except Exception as e:
            print(f"Error fetching intraday data for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_sector_performance(self, ticker: str) -> Dict:
        """Get sector performance comparison"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            # Get sector ETF for comparison (simplified)
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV',
                'Financial': 'XLF',
                'Consumer Cyclical': 'XLY',
                'Consumer Defensive': 'XLP',
                'Energy': 'XLE',
                'Industrials': 'XLI',
                'Materials': 'XLB',
                'Real Estate': 'XLRE',
                'Utilities': 'XLU',
                'Communication Services': 'XLC'
            }
            
            sector_etf = sector_etfs.get(sector, 'SPY')
            
            # Get sector ETF performance
            etf_data = self.get_ticker_data(sector_etf)
            
            return {
                'sector': sector,
                'industry': industry,
                'sector_etf': sector_etf,
                'sector_performance': etf_data.get('change_percent', 0),
                'relative_strength': (
                    info.get('change_percent', 0) - etf_data.get('change_percent', 0)
                    if etf_data else 0
                )
            }
            
        except Exception as e:
            print(f"Error getting sector data for {ticker}: {e}")
            return {}
    
    def _is_cached(self, ticker: str) -> bool:
        """Check if data is cached and still valid"""
        if ticker not in self.cache:
            return False
        
        if ticker not in self.cache_expiry:
            return False
        
        return datetime.now() < self.cache_expiry[ticker]
    
    def _cache_data(self, ticker: str, data: Dict):
        """Cache data with expiry"""
        self.cache[ticker] = data
        self.cache_expiry[ticker] = datetime.now() + self.cache_duration
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
        self.cache_expiry = {}
    
    def get_multiple_tickers(self, tickers: List[str]) -> Dict[str, Dict]:
        """Get data for multiple tickers efficiently"""
        results = {}
        
        for ticker in tickers:
            data = self.get_ticker_data(ticker)
            if data:
                results[ticker] = data
        
        return results