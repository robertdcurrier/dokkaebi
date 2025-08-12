"""
DuckDB Price Data Cache - REBELLIOUSLY ELEGANT Storage

Optimized for high-frequency tick data with compression and indexing.
Designed to make HebbNet trading decisions lightning fast.

Viper's bulletproof implementation using Diesel's preferred DuckDB.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import duckdb
import pandas as pd
from tqdm.auto import tqdm


logger = logging.getLogger(__name__)


class PriceCache:
    """
    High-performance DuckDB cache for price data.
    
    Optimized for:
    - Fast HebbNet feature extraction
    - Efficient time-series queries
    - Minimal storage overhead
    - Concurrent read access
    """

    def __init__(
        self, 
        db_path: Union[str, Path] = "data/price_cache.duckdb",
        read_only: bool = False
    ) -> None:
        """
        Initialize price cache with optimized schema.
        
        Args:
            db_path: Path to DuckDB database file
            read_only: Open in read-only mode for concurrent access
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.read_only = read_only
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        
        self._ensure_schema()
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
        
    def _ensure_schema(self) -> None:
        """Create optimized tables if they don't exist."""
        with self._get_connection() as conn:
            # Main tick data table - optimized for time-series queries
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tick_data (
                    symbol VARCHAR NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    open DOUBLE NOT NULL,
                    high DOUBLE NOT NULL,
                    low DOUBLE NOT NULL,
                    close DOUBLE NOT NULL,
                    volume BIGINT NOT NULL,
                    adj_close DOUBLE,
                    created_at TIMESTAMPTZ DEFAULT now(),
                    PRIMARY KEY (symbol, timestamp)
                )
            """)
            
            # Metadata table for symbol information
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbol_metadata (
                    symbol VARCHAR PRIMARY KEY,
                    exchange VARCHAR,
                    sector VARCHAR,
                    industry VARCHAR,
                    market_cap BIGINT,
                    shares_outstanding BIGINT,
                    last_updated TIMESTAMPTZ DEFAULT now()
                )
            """)
            
            # Optimized indexes for HebbNet queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tick_symbol_time 
                ON tick_data (symbol, timestamp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tick_timestamp 
                ON tick_data (timestamp DESC)
            """)
            
            # View for latest prices (HebbNet real-time features)
            conn.execute("""
                CREATE OR REPLACE VIEW latest_prices AS
                SELECT DISTINCT ON (symbol) 
                    symbol, timestamp, close, volume, adj_close
                FROM tick_data 
                ORDER BY symbol, timestamp DESC
            """)
            
    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get database connection with optimal settings."""
        if self._conn is None:
            config = {
                'memory_limit': '2GB',
                'threads': 4
            }
            
            if self.read_only:
                config['access_mode'] = 'READ_ONLY'
                
            self._conn = duckdb.connect(str(self.db_path), config=config)
            
        return self._conn
        
    def store_tick_data(
        self, 
        data: pd.DataFrame, 
        symbol: str,
        show_progress: bool = True
    ) -> int:
        """
        Store tick data with batch optimization.
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Stock symbol
            show_progress: Show progress bar for large datasets
            
        Returns:
            Number of rows inserted
        """
        if data.empty:
            logger.warning(f"No data to store for {symbol}")
            return 0
            
        # Prepare data for insertion
        data_clean = data.copy()
        data_clean['symbol'] = symbol
        data_clean['timestamp'] = pd.to_datetime(
            data_clean.index, utc=True
        )
        
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in data_clean.columns:
                raise ValueError(f"Missing required column: {col}")
                
        # Optional adj_close column
        if 'adj close' in data_clean.columns:
            data_clean['adj_close'] = data_clean['adj close']
        elif 'Adj Close' in data_clean.columns:
            data_clean['adj_close'] = data_clean['Adj Close']
            
        # Select and order columns for insertion
        insert_cols = [
            'symbol', 'timestamp', 'open', 'high', 
            'low', 'close', 'volume'
        ]
        if 'adj_close' in data_clean.columns:
            insert_cols.append('adj_close')
            
        data_final = data_clean[insert_cols]
        
        with self._get_connection() as conn:
            # Use UPSERT for handling duplicates efficiently
            rows_before = conn.execute(
                "SELECT COUNT(*) FROM tick_data WHERE symbol = ?", 
                [symbol]
            ).fetchone()[0]
            
            # Batch insert with progress tracking
            if show_progress and len(data_final) > 1000:
                chunk_size = 10000
                chunks = [
                    data_final[i:i + chunk_size] 
                    for i in range(0, len(data_final), chunk_size)
                ]
                
                for chunk in tqdm(chunks, desc=f"Storing {symbol}"):
                    conn.execute(
                        "INSERT OR REPLACE INTO tick_data SELECT * FROM chunk"
                    )
            else:
                conn.execute(
                    "INSERT OR REPLACE INTO tick_data SELECT * FROM data_final"
                )
                
            rows_after = conn.execute(
                "SELECT COUNT(*) FROM tick_data WHERE symbol = ?", 
                [symbol]
            ).fetchone()[0]
            
        rows_inserted = rows_after - rows_before
        logger.info(f"Stored {rows_inserted} new rows for {symbol}")
        return rows_inserted
        
    def get_price_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Retrieve price data with time filtering.
        
        Args:
            symbol: Stock symbol
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of rows
            
        Returns:
            DataFrame with price data
        """
        query = "SELECT * FROM tick_data WHERE symbol = ?"
        params = [symbol]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
            
        with self._get_connection() as conn:
            result = conn.execute(query, params).df()
            
        if not result.empty:
            result.set_index('timestamp', inplace=True)
            
        return result
        
    def get_latest_prices(
        self, 
        symbols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get latest prices for HebbNet real-time processing.
        
        Args:
            symbols: List of symbols to filter, None for all
            
        Returns:
            DataFrame with latest prices
        """
        query = "SELECT * FROM latest_prices"
        params = []
        
        if symbols:
            placeholders = ','.join(['?' for _ in symbols])
            query += f" WHERE symbol IN ({placeholders})"
            params = symbols
            
        query += " ORDER BY symbol"
        
        with self._get_connection() as conn:
            return conn.execute(query, params).df()
            
    def store_symbol_metadata(
        self, 
        metadata: Dict[str, Any]
    ) -> None:
        """
        Store symbol metadata for filtering.
        
        Args:
            metadata: Dictionary with symbol metadata
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO symbol_metadata 
                (symbol, exchange, sector, industry, market_cap, 
                 shares_outstanding)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                metadata.get('symbol'),
                metadata.get('exchange'),
                metadata.get('sector'),
                metadata.get('industry'),
                metadata.get('market_cap'),
                metadata.get('shares_outstanding')
            ])
            
    def get_symbol_count(self) -> int:
        """Get total number of symbols in cache."""
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT COUNT(DISTINCT symbol) FROM tick_data"
            ).fetchone()[0]
            
    def get_date_range(self, symbol: str) -> tuple:
        """
        Get date range for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Tuple of (start_date, end_date)
        """
        with self._get_connection() as conn:
            result = conn.execute("""
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM tick_data 
                WHERE symbol = ?
            """, [symbol]).fetchone()
            
        return result if result[0] else (None, None)
        
    def cleanup_old_data(self, days_to_keep: int = 365) -> int:
        """
        Remove old data to manage storage.
        
        Args:
            days_to_keep: Number of days to retain
            
        Returns:
            Number of rows deleted
        """
        cutoff_date = datetime.now(timezone.utc) - pd.Timedelta(
            days=days_to_keep
        )
        
        with self._get_connection() as conn:
            result = conn.execute("""
                DELETE FROM tick_data 
                WHERE timestamp < ?
            """, [cutoff_date])
            
            # Vacuum to reclaim space
            conn.execute("VACUUM")
            
        rows_deleted = result.rowcount
        logger.info(f"Cleaned up {rows_deleted} old records")
        return rows_deleted
        
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