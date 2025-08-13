"""
DOKKAEBI API Routes
The REAL web API for our price downloader system!

All the endpoints Bob needs to dominate the markets.
Viper's implementation - FAST, CLEAN, and FUCKING EFFICIENT!
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel

# Import our WORKING price downloader components
from src.price_downloader.providers.alpaca_provider import AlpacaProvider
from src.price_downloader.storage.cache_v2 import PriceCacheV2


router = APIRouter()


# Response models
class DownloadResponse(BaseModel):
    """Response for download operations."""
    status: str
    message: str
    symbols: List[str]
    records_downloaded: int
    cache_updated: bool


class CacheStats(BaseModel):
    """Cache statistics response."""
    total_symbols: int
    daily_records: int  # Keep for compatibility
    intraday_records: int  # Keep for compatibility  
    total_records: int  # New combined field
    latest_update: Optional[str]
    cache_size_mb: float


class WatchlistResponse(BaseModel):
    """Watchlist response."""
    symbols: List[str]
    count: int


class WatchlistUpdate(BaseModel):
    """Request body for watchlist updates."""
    symbols: List[str]


class CacheClearResponse(BaseModel):
    """Response for cache clear operations."""
    status: str
    message: str
    daily_records_cleared: int
    intraday_records_cleared: int
    total_records_cleared: int


# Initialize our components
def get_alpaca_provider():
    """Get Alpaca provider instance."""
    try:
        return AlpacaProvider(cache_enabled=True)
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Alpaca configuration error: {str(e)}"
        )


def get_cache():
    """Get cache instance."""
    return PriceCacheV2("data/price_cache.duckdb")


def load_watchlist() -> List[str]:
    """Load watchlist from file."""
    watchlist_path = Path("data/watchlist.txt")
    if watchlist_path.exists():
        symbols = []
        with open(watchlist_path) as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    symbol = line.upper()
                    # Avoid duplicates
                    if symbol not in symbols:
                        symbols.append(symbol)
        return symbols
    return []


def save_watchlist(symbols: List[str]) -> None:
    """Save watchlist to file."""
    watchlist_path = Path("data/watchlist.txt")
    watchlist_path.parent.mkdir(parents=True, exist_ok=True)
    with open(watchlist_path, 'w') as f:
        for symbol in symbols:
            f.write(f"{symbol}\n")


async def download_symbol_data(provider: AlpacaProvider, symbol: str, days_back: int = 1) -> int:
    """
    Download 15-minute bar data for a single symbol going back specified days.
    Uses configurable date range based on days_back parameter.
    Special case: days_back=0 downloads only the latest bar (limit=1).

    Args:
        provider: AlpacaProvider instance
        symbol: Stock symbol to download
        days_back: Number of days to go back from current time (default: 1)
                  Set to 0 to get only the latest bar per symbol
        
    Returns:
        Number of records downloaded
    """
    try:
        interval = '15Min'
        
        from datetime import timezone
        # End with 16-minute delay (Alpaca free tier cannot access last 15 minutes)
        end_time = datetime.now(timezone.utc) - timedelta(minutes=16)
        
        # Special case: Latest only (days_back=0)
        if days_back == 0:
            print(f"Downloading LATEST {symbol} 15-minute bar using get_latest_bar()")
            
            # Use the fixed get_latest_bar() method instead of get_historical_data()
            data = provider.get_latest_bar(symbol=symbol, interval=interval)
            
            if data is not None and not data.empty:
                print(f"Got latest bar for {symbol}: {data.index[0]} - ${data['Close'].iloc[0]:.2f}")
            else:
                data = pd.DataFrame()  # Ensure data is set to empty DataFrame if None
        else:
            # Calculate start date based on days_back parameter
            start_date = end_time - timedelta(days=days_back)
            
            print(f"Downloading {symbol} 15-minute bars: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} ({days_back} days back)")
            
            data = provider.get_historical_data(
                symbol=symbol,
                start=start_date,
                end=end_time,
                interval=interval
            )
        
        print(f"Downloaded {len(data)} 15-minute records for {symbol}")
        return len(data)
        
    except Exception as e:
        print(f"Error downloading {symbol} 15-minute data: {e}")
        return 0


# API Endpoints

@router.post("/download/watchlist", response_model=DownloadResponse)
async def download_watchlist(days_back: int = Query(1, description="Number of days to go back (0 = Latest bar only)")):
    """
    Download price data for all symbols in the watchlist.
    Uses 15-minute bars with 16-minute delay, clears old data first.
    
    Args:
        days_back: Number of days to go back from current time (default: 1)
                  Set to 0 to get only the latest bar per symbol (optimal for automation)
    
    Returns:
        DownloadResponse: Download results
    """
    interval = '15Min'  # Always use 15-minute bars
    
    provider = get_alpaca_provider()
    symbols = load_watchlist()
    
    if not symbols:
        raise HTTPException(
            status_code=400,
            detail="No symbols in watchlist. Update watchlist first."
        )
    
    # Clear old intraday data first to prevent stale data display
    try:
        cache = get_cache()
        print("Clearing old intraday data to prevent stale display...")
        with cache._get_connection() as conn:
            result = conn.execute("DELETE FROM intraday_prices WHERE timeframe = '15min'").fetchone()
            conn.commit()
        print("Old 15-minute data cleared")
    except Exception as e:
        print(f"Warning: Could not clear old data: {e}")
    
    total_records = 0
    successful_symbols = []
    failed_symbols = []
    
    # Determine range description
    range_desc = "Latest bars only" if days_back == 0 else f"{days_back} days back"
    print(f"Starting watchlist download with 15-minute bars ({range_desc})")
    
    for symbol in symbols:
        if days_back == 0:
            print(f"Downloading {symbol} LATEST 15-minute bar...")
        else:
            print(f"Downloading {symbol} 15-minute bars ({days_back} days back)...")
        records = await download_symbol_data(provider, symbol, days_back)
        if records > 0:
            total_records += records
            successful_symbols.append(symbol)
        else:
            failed_symbols.append(symbol)
    
    status = "success" if len(failed_symbols) == 0 else "partial_success" if successful_symbols else "failure"
    range_text = "Latest bars" if days_back == 0 else f"{days_back} days back"
    message = f"Downloaded 15-minute data for {len(successful_symbols)}/{len(symbols)} symbols ({range_text})"
    if failed_symbols:
        message += f" (Failed: {', '.join(failed_symbols)})"
    
    return DownloadResponse(
        status=status,
        message=message,
        symbols=successful_symbols,
        records_downloaded=total_records,
        cache_updated=True
    )


@router.post("/download/symbol/{symbol}", response_model=DownloadResponse)
async def download_single_symbol(symbol: str, days_back: int = Query(1, description="Number of days to go back (0 = Latest bar only)")):
    """
    Download price data for a single symbol.
    Uses 15-minute bars with 16-minute delay.
    
    Args:
        symbol: Stock symbol to download
        days_back: Number of days to go back from current time (default: 1)
                  Set to 0 to get only the latest bar (optimal for automation)
        
    Returns:
        DownloadResponse: Download results
    """
    interval = '15Min'  # Always use 15-minute bars
    
    provider = get_alpaca_provider()
    symbol_upper = symbol.upper()
    
    if days_back == 0:
        print(f"Downloading {symbol_upper} LATEST 15-minute bar...")
    else:
        print(f"Downloading {symbol_upper} 15-minute bars ({days_back} days back)...")
    
    records = await download_symbol_data(provider, symbol_upper, days_back)
    
    if records > 0:
        range_text = "Latest bar" if days_back == 0 else f"{days_back} days back"
        return DownloadResponse(
            status="success",
            message=f"Downloaded {records} 15-minute records for {symbol_upper} ({range_text})",
            symbols=[symbol_upper],
            records_downloaded=records,
            cache_updated=True
        )
    else:
        range_text = "Latest bar" if days_back == 0 else f"{days_back} days back"
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download 15-minute data for {symbol_upper} ({range_text})"
        )


@router.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats():
    """
    Get cache statistics.
    
    Returns:
        CacheStats: Cache information
    """
    cache = get_cache()
    
    try:
        # Get stats from both tables
        with cache._get_connection() as conn:
            daily_count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
            intraday_count = conn.execute("SELECT COUNT(*) FROM intraday_prices").fetchone()[0]
            
            # Get unique symbols count
            total_symbols_query = """
            SELECT COUNT(DISTINCT symbol) FROM (
                SELECT DISTINCT symbol FROM daily_prices
                UNION 
                SELECT DISTINCT symbol FROM intraday_prices
            )
            """
            total_symbols = conn.execute(total_symbols_query).fetchone()[0]
            
            # Get latest update
            latest_query = """
            SELECT MAX(latest_date) FROM (
                SELECT MAX(trading_date) as latest_date FROM daily_prices
                UNION ALL
                SELECT MAX(bar_timestamp::date) as latest_date FROM intraday_prices
            )
            """
            result = conn.execute(latest_query).fetchone()
            latest_update = str(result[0]) if result and result[0] else None
        
        # Get cache file size
        cache_path = Path("data/price_cache.duckdb")
        cache_size_mb = cache_path.stat().st_size / (1024 * 1024) if cache_path.exists() else 0
        
        return CacheStats(
            total_symbols=total_symbols,
            daily_records=daily_count,
            intraday_records=intraday_count,
            total_records=daily_count + intraday_count,
            latest_update=latest_update,
            cache_size_mb=round(cache_size_mb, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting cache stats: {str(e)}"
        )


@router.get("/cache/recent")
async def get_recent_cache_data(
    symbol: Optional[str] = None,
    limit: int = 100
):
    """
    Get recent market data from cache (15-minute bars).
    
    Args:
        symbol: Optional symbol filter
        limit: Maximum number of records
        
    Returns:
        dict: Recent market data (15-minute bars)
    """
    cache = get_cache()
    
    try:
        with cache._get_connection() as conn:
            if symbol:
                query = """
                SELECT * FROM intraday_prices 
                WHERE symbol = ? AND timeframe = '15min'
                ORDER BY bar_timestamp DESC 
                LIMIT ?
                """
                result = conn.execute(query, [symbol.upper(), limit]).fetchall()
            else:
                query = """
                SELECT * FROM intraday_prices 
                WHERE timeframe = '15min'
                ORDER BY bar_timestamp DESC, symbol 
                LIMIT ?
                """
                result = conn.execute(query, [limit]).fetchall()
            
            # Get column names
            columns = [desc[0] for desc in conn.description]
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in result]
            
            return {
                "data": data,
                "count": len(data),
                "columns": columns
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recent cache data: {str(e)}"
        )


# Legacy endpoint kept for compatibility - redirects to recent data
@router.get("/cache/intraday")
async def get_intraday_cache_data(
    symbol: Optional[str] = None,
    interval: Optional[str] = None,  # Changed from timeframe for consistency
    limit: int = 100
):
    """
    Legacy endpoint - redirects to recent 15-minute data.
    
    Args:
        symbol: Optional symbol filter
        interval: Ignored - always returns 15-minute data
        limit: Maximum number of records
        
    Returns:
        dict: Recent 15-minute market data
    """
    # Redirect to recent endpoint (15-minute data)
    return await get_recent_cache_data(symbol=symbol, limit=limit)


# Legacy endpoint kept for compatibility - redirects to recent data
@router.get("/cache/daily")
async def get_daily_cache_data(
    symbol: Optional[str] = None,
    limit: int = 100
):
    """
    Legacy endpoint - redirects to recent 15-minute data.
    
    Args:
        symbol: Optional symbol filter
        limit: Maximum number of records
        
    Returns:
        dict: Recent 15-minute market data
    """
    # Redirect to recent endpoint (15-minute data)
    return await get_recent_cache_data(symbol=symbol, limit=limit)


@router.delete("/cache/clear", response_model=CacheClearResponse)
async def clear_cache():
    """
    Clear all price data from cache.
    
    Deletes all daily and intraday price records from the cache database.
    This is a destructive operation that cannot be undone.
    
    Returns:
        CacheClearResponse: Information about what was cleared
    """
    try:
        cache = get_cache()
        clear_result = cache.clear_all_cache()
        
        return CacheClearResponse(
            status="success",
            message=f"Cache cleared successfully. Removed {clear_result['total_records_cleared']} total records.",
            daily_records_cleared=clear_result['daily_records_cleared'],
            intraday_records_cleared=clear_result['intraday_records_cleared'],
            total_records_cleared=clear_result['total_records_cleared']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist():
    """
    Get current watchlist.
    
    Returns:
        WatchlistResponse: Current watchlist symbols
    """
    symbols = load_watchlist()
    return WatchlistResponse(
        symbols=symbols,
        count=len(symbols)
    )


@router.post("/watchlist", response_model=WatchlistResponse)
async def update_watchlist(watchlist_data: WatchlistUpdate):
    """
    Update the watchlist.
    
    Args:
        watchlist_data: New watchlist symbols
        
    Returns:
        WatchlistResponse: Updated watchlist
    """
    # Clean and validate symbols
    clean_symbols = []
    for symbol in watchlist_data.symbols:
        clean_symbol = symbol.strip().upper()
        if clean_symbol and clean_symbol not in clean_symbols:
            clean_symbols.append(clean_symbol)
    
    if not clean_symbols:
        raise HTTPException(
            status_code=400,
            detail="No valid symbols provided"
        )
    
    save_watchlist(clean_symbols)
    
    return WatchlistResponse(
        symbols=clean_symbols,
        count=len(clean_symbols)
    )


@router.get("/test/connection")
async def test_alpaca_connection():
    """
    Test Alpaca connection.
    
    Returns:
        dict: Connection test results
    """
    try:
        provider = get_alpaca_provider()
        success = provider.test_connection()
        
        return {
            "status": "success" if success else "failed",
            "provider": "Alpaca Markets",
            "message": "Connection successful" if success else "Connection failed"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "provider": "Alpaca Markets",
            "message": str(e)
        }