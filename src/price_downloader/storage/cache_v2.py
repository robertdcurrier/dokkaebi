"""
DuckDB Price Cache V2 - Diesel's Dual-Table Architecture

Separate tables for daily and intraday data with explicit metadata.
No confusion. No ambiguity. Just clean, fast data storage.

Diesel's design, Viper's implementation - REBELLIOUSLY ELEGANT!
"""

import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Union, Literal

import duckdb
import pandas as pd
from tqdm.auto import tqdm


logger = logging.getLogger(__name__)


class PriceCacheV2:
    """
    Dual-table DuckDB cache for daily and intraday price data.
    
    Features:
    - Separate tables for daily vs intraday (no confusion!)
    - Explicit data_type metadata in both tables
    - Efficient upsert operations
    - Optimized for HebbNet queries
    """
    
    def __init__(
        self, 
        db_path: Union[str, Path] = "data/price_cache.duckdb",
        read_only: bool = False
    ) -> None:
        """
        Initialize the dual-table cache.
        
        Args:
            db_path: Path to DuckDB database
            read_only: Open in read-only mode
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.read_only = read_only
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        
        self._ensure_schema()
    
    def _ensure_schema(self) -> None:
        """Create Diesel's dual-table schema if not exists."""
        with self._get_connection() as conn:
            # Daily prices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_prices (
                    symbol VARCHAR NOT NULL,
                    trading_date DATE NOT NULL,
                    open DECIMAL(18,6) NOT NULL,
                    high DECIMAL(18,6) NOT NULL,
                    low DECIMAL(18,6) NOT NULL,
                    close DECIMAL(18,6) NOT NULL,
                    volume BIGINT NOT NULL,
                    adj_close DECIMAL(18,6),
                    dividend DECIMAL(18,6) DEFAULT 0.0,
                    split_ratio DECIMAL(10,6) DEFAULT 1.0,
                    data_type VARCHAR DEFAULT 'daily' CHECK (data_type = 'daily'),
                    source VARCHAR DEFAULT 'alpaca_markets',
                    created_at TIMESTAMPTZ DEFAULT now(),
                    updated_at TIMESTAMPTZ DEFAULT now(),
                    PRIMARY KEY (symbol, trading_date)
                )
            """)
            
            # Intraday prices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intraday_prices (
                    symbol VARCHAR NOT NULL,
                    bar_timestamp TIMESTAMPTZ NOT NULL,
                    timeframe VARCHAR NOT NULL CHECK (
                        timeframe IN ('1min', '5min', '15min', '30min', '1hour')
                    ),
                    open DECIMAL(18,6) NOT NULL,
                    high DECIMAL(18,6) NOT NULL,
                    low DECIMAL(18,6) NOT NULL,
                    close DECIMAL(18,6) NOT NULL,
                    volume BIGINT NOT NULL,
                    vwap DECIMAL(18,6),
                    trade_count INTEGER,
                    data_type VARCHAR DEFAULT 'intraday' CHECK (data_type = 'intraday'),
                    source VARCHAR DEFAULT 'alpaca_markets',
                    created_at TIMESTAMPTZ DEFAULT now(),
                    updated_at TIMESTAMPTZ DEFAULT now(),
                    PRIMARY KEY (symbol, bar_timestamp, timeframe)
                )
            """)
            
            # Create indexes for performance
            self._create_indexes(conn)
            
            logger.info("Dual-table schema initialized")
    
    def _create_indexes(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Create Diesel's optimized indexes."""
        # Daily indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_symbol_date 
            ON daily_prices (symbol, trading_date DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_date 
            ON daily_prices (trading_date DESC)
        """)
        
        # Intraday indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_intraday_symbol_time 
            ON intraday_prices (symbol, bar_timestamp DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_intraday_timeframe 
            ON intraday_prices (timeframe, bar_timestamp DESC)
        """)
    
    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        # Always create a new connection for simplicity
        config = {
            'memory_limit': '2GB',
            'threads': 4
        }
        
        if self.read_only:
            config['access_mode'] = 'READ_ONLY'
        
        return duckdb.connect(str(self.db_path), config=config)
    
    def store_daily_prices(
        self,
        data: pd.DataFrame,
        symbol: str,
        show_progress: bool = False
    ) -> int:
        """
        Store daily price data.
        
        Args:
            data: DataFrame with OHLCV data (index should be dates)
            symbol: Stock symbol
            show_progress: Show progress bar
            
        Returns:
            Number of rows stored
        """
        if data.empty:
            logger.warning(f"No daily data to store for {symbol}")
            return 0
        
        # Prepare data
        records = []
        
        iterator = tqdm(data.iterrows(), total=len(data)) if show_progress else data.iterrows()
        
        for date_idx, row in iterator:
            # Convert timestamp to date
            trading_date = date_idx.date() if hasattr(date_idx, 'date') else date_idx
            
            records.append((
                symbol,
                trading_date,
                float(row.get('Open', row.get('open', 0))),
                float(row.get('High', row.get('high', 0))),
                float(row.get('Low', row.get('low', 0))),
                float(row.get('Close', row.get('close', 0))),
                int(row.get('Volume', row.get('volume', 0))),
                float(row.get('Adj Close', row.get('adj_close', row.get('Close', 0)))),
                0.0,  # dividend
                1.0,  # split_ratio
                'daily',
                'alpaca_markets',
                datetime.now(),
                datetime.now()
            ))
        
        # Bulk upsert
        with self._get_connection() as conn:
            conn.executemany("""
                INSERT INTO daily_prices (
                    symbol, trading_date, open, high, low, close, volume,
                    adj_close, dividend, split_ratio, data_type, source,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (symbol, trading_date)
                DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    adj_close = EXCLUDED.adj_close,
                    updated_at = EXCLUDED.updated_at
            """, records)
        
        logger.info(f"Stored {len(records)} daily records for {symbol}")
        return len(records)
    
    def store_intraday_prices(
        self,
        data: pd.DataFrame,
        symbol: str,
        timeframe: Literal['1min', '5min', '15min', '30min', '1hour'],
        show_progress: bool = False
    ) -> int:
        """
        Store intraday price data.
        
        Args:
            data: DataFrame with OHLCV data (index should be timestamps)
            symbol: Stock symbol
            timeframe: Bar timeframe
            show_progress: Show progress bar
            
        Returns:
            Number of rows stored
        """
        if data.empty:
            logger.warning(f"No intraday data to store for {symbol}")
            return 0
        
        # Prepare data
        records = []
        
        iterator = tqdm(data.iterrows(), total=len(data)) if show_progress else data.iterrows()
        
        for timestamp, row in iterator:
            records.append((
                symbol,
                timestamp,
                timeframe,
                float(row.get('Open', row.get('open', 0))),
                float(row.get('High', row.get('high', 0))),
                float(row.get('Low', row.get('low', 0))),
                float(row.get('Close', row.get('close', 0))),
                int(row.get('Volume', row.get('volume', 0))),
                float(row.get('VWAP', row.get('vwap', 0))),
                int(row.get('TradeCount', row.get('trade_count', 0))),
                'intraday',
                'alpaca_markets',
                datetime.now(),
                datetime.now()
            ))
        
        # Bulk upsert
        with self._get_connection() as conn:
            conn.executemany("""
                INSERT INTO intraday_prices (
                    symbol, bar_timestamp, timeframe, open, high, low, close,
                    volume, vwap, trade_count, data_type, source,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (symbol, bar_timestamp, timeframe)
                DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    vwap = EXCLUDED.vwap,
                    trade_count = EXCLUDED.trade_count,
                    updated_at = EXCLUDED.updated_at
            """, records)
        
        logger.info(f"Stored {len(records)} intraday records for {symbol} ({timeframe})")
        return len(records)
    
    def get_daily_prices(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Retrieve daily prices from cache.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            DataFrame with daily prices
        """
        query = """
            SELECT trading_date, open, high, low, close, volume, adj_close
            FROM daily_prices
            WHERE symbol = ? AND data_type = 'daily'
        """
        params = [symbol]
        
        if start_date:
            query += " AND trading_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND trading_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY trading_date"
        
        with self._get_connection() as conn:
            df = conn.execute(query, params).df()
        
        if not df.empty:
            df.set_index('trading_date', inplace=True)
            df.index = pd.to_datetime(df.index)
        
        return df
    
    def get_intraday_prices(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Retrieve intraday prices from cache.
        
        Args:
            symbol: Stock symbol
            timeframe: Bar timeframe
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            DataFrame with intraday prices
        """
        query = """
            SELECT bar_timestamp, open, high, low, close, volume, vwap
            FROM intraday_prices
            WHERE symbol = ? AND timeframe = ? AND data_type = 'intraday'
        """
        params = [symbol, timeframe]
        
        if start_time:
            query += " AND bar_timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND bar_timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY bar_timestamp"
        
        with self._get_connection() as conn:
            df = conn.execute(query, params).df()
        
        if not df.empty:
            df.set_index('bar_timestamp', inplace=True)
        
        return df
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        with self._get_connection() as conn:
            daily_stats = conn.execute("""
                SELECT 
                    COUNT(DISTINCT symbol) as symbols,
                    COUNT(*) as rows,
                    MIN(trading_date) as earliest,
                    MAX(trading_date) as latest
                FROM daily_prices
            """).fetchone()
            
            intraday_stats = conn.execute("""
                SELECT 
                    COUNT(DISTINCT symbol) as symbols,
                    COUNT(*) as rows,
                    MIN(bar_timestamp) as earliest,
                    MAX(bar_timestamp) as latest
                FROM intraday_prices
            """).fetchone()
        
        return {
            'daily': {
                'symbols': daily_stats[0] or 0,
                'rows': daily_stats[1] or 0,
                'earliest': daily_stats[2],
                'latest': daily_stats[3]
            },
            'intraday': {
                'symbols': intraday_stats[0] or 0,
                'rows': intraday_stats[1] or 0,
                'earliest': intraday_stats[2],
                'latest': intraday_stats[3]
            }
        }
    
    def clear_daily_cache(self) -> int:
        """
        Clear all daily price data from cache.
        
        Returns:
            Number of records deleted
        """
        with self._get_connection() as conn:
            # Get count before deletion
            count_result = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()
            record_count = count_result[0] if count_result else 0
            
            # Clear the table
            conn.execute("DELETE FROM daily_prices")
            
            logger.info(f"Cleared {record_count} daily price records from cache")
            return record_count
    
    def clear_intraday_cache(self) -> int:
        """
        Clear all intraday price data from cache.
        
        Returns:
            Number of records deleted
        """
        with self._get_connection() as conn:
            # Get count before deletion
            count_result = conn.execute("SELECT COUNT(*) FROM intraday_prices").fetchone()
            record_count = count_result[0] if count_result else 0
            
            # Clear the table
            conn.execute("DELETE FROM intraday_prices")
            
            logger.info(f"Cleared {record_count} intraday price records from cache")
            return record_count
    
    def clear_all_cache(self) -> Dict[str, int]:
        """
        Clear all price data from cache (both daily and intraday).
        
        Returns:
            Dictionary with counts of records deleted from each table
        """
        daily_cleared = self.clear_daily_cache()
        intraday_cleared = self.clear_intraday_cache()
        
        total_cleared = daily_cleared + intraday_cleared
        logger.info(f"Cleared total of {total_cleared} records from cache")
        
        return {
            'daily_records_cleared': daily_cleared,
            'intraday_records_cleared': intraday_cleared,
            'total_records_cleared': total_cleared
        }
    
    def clear_symbol_data(self, symbol: str) -> Dict[str, int]:
        """
        Clear all data for a specific symbol.
        
        Args:
            symbol: Stock symbol to clear
            
        Returns:
            Dictionary with counts of records deleted for the symbol
        """
        with self._get_connection() as conn:
            # Clear from daily_prices
            daily_count_result = conn.execute(
                "SELECT COUNT(*) FROM daily_prices WHERE symbol = ?", 
                [symbol]
            ).fetchone()
            daily_count = daily_count_result[0] if daily_count_result else 0
            
            conn.execute("DELETE FROM daily_prices WHERE symbol = ?", [symbol])
            
            # Clear from intraday_prices
            intraday_count_result = conn.execute(
                "SELECT COUNT(*) FROM intraday_prices WHERE symbol = ?", 
                [symbol]
            ).fetchone()
            intraday_count = intraday_count_result[0] if intraday_count_result else 0
            
            conn.execute("DELETE FROM intraday_prices WHERE symbol = ?", [symbol])
            
            total_cleared = daily_count + intraday_count
            logger.info(f"Cleared {total_cleared} records for symbol {symbol}")
            
            return {
                'symbol': symbol,
                'daily_records_cleared': daily_count,
                'intraday_records_cleared': intraday_count,
                'total_records_cleared': total_cleared
            }
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()