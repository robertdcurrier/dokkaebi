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


async def download_symbol_data(provider: AlpacaProvider, symbol: str, days_back: int = 1, interval: str = '15Min') -> int:
    """
    Download market data for a single symbol with configurable interval.
    Uses configurable date range based on days_back parameter.
    Special case: days_back=0 downloads only the latest bar (limit=1).

    Args:
        provider: AlpacaProvider instance
        symbol: Stock symbol to download
        days_back: Number of days to go back from current time (default: 1)
                  Set to 0 to get only the latest bar per symbol
        interval: Time interval (Daily, Hourly, 30Min, 15Min)
        
    Returns:
        Number of records downloaded
    """
    try:
        
        from datetime import timezone
        # End with 16-minute delay (Alpaca free tier cannot access last 15 minutes)
        end_time = datetime.now(timezone.utc) - timedelta(minutes=16)
        
        # Special case: Latest only (days_back=0)
        if days_back == 0:
            print(f"Downloading LATEST {symbol} {interval} bar using get_latest_bar()")
            
            # Use the fixed get_latest_bar() method instead of get_historical_data()
            data = provider.get_latest_bar(symbol=symbol, interval=interval)
            
            if data is not None and not data.empty:
                print(f"Got latest bar for {symbol}: {data.index[0]} - ${data['Close'].iloc[0]:.2f}")
            else:
                data = pd.DataFrame()  # Ensure data is set to empty DataFrame if None
        else:
            # Calculate start date based on days_back parameter
            start_date = end_time - timedelta(days=days_back)
            
            print(f"Downloading {symbol} {interval} bars: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} ({days_back} days back)")
            
            data = provider.get_historical_data(
                symbol=symbol,
                start=start_date,
                end=end_time,
                interval=interval
            )
        
        print(f"Downloaded {len(data)} {interval} records for {symbol}")
        return len(data)
        
    except Exception as e:
        print(f"Error downloading {symbol} {interval} data: {e}")
        return 0


# API Endpoints

@router.post("/download/watchlist", response_model=DownloadResponse)
async def download_watchlist(days_back: int = Query(1, description="Number of days to go back (0 = Latest bar only)"), interval: str = Query('15Min', description="Time interval (Daily, Hourly, 30Min, 15Min)")):
    """
    Download price data for all symbols in the watchlist.
    Uses configurable interval with appropriate delay, clears old data first.
    
    Args:
        days_back: Number of days to go back from current time (default: 1)
                  Set to 0 to get only the latest bar per symbol (optimal for automation)
        interval: Time interval (Daily, Hourly, 30Min, 15Min)
    
    Returns:
        DownloadResponse: Download results
    """
    # Map UI intervals to Alpaca format
    interval_mapping = {
        'Daily': '1Day',
        'Hourly': '1Hour', 
        '30Min': '30Min',
        '15Min': '15Min'
    }
    
    # Convert interval to Alpaca format
    alpaca_interval = interval_mapping.get(interval, '15Min')
    
    provider = get_alpaca_provider()
    symbols = load_watchlist()
    
    if not symbols:
        raise HTTPException(
            status_code=400,
            detail="No symbols in watchlist. Update watchlist first."
        )
    
    # Clear old data first to prevent stale data display
    try:
        cache = get_cache()
        print(f"Clearing old {interval} data to prevent stale display...")
        with cache._get_connection() as conn:
            if interval == 'Daily':
                result = conn.execute("DELETE FROM daily_prices").fetchone()
            else:
                # Map interval to timeframe for intraday clearing
                timeframe_map = {
                    'Hourly': '1hour',
                    '30Min': '30min', 
                    '15Min': '15min'
                }
                timeframe = timeframe_map.get(interval, '15min')
                result = conn.execute("DELETE FROM intraday_prices WHERE timeframe = ?", [timeframe]).fetchone()
            conn.commit()
        print(f"Old {interval} data cleared")
    except Exception as e:
        print(f"Warning: Could not clear old data: {e}")
    
    total_records = 0
    successful_symbols = []
    failed_symbols = []
    
    # Determine range description
    range_desc = "Latest bars only" if days_back == 0 else f"{days_back} days back"
    print(f"Starting watchlist download with {interval} bars ({range_desc})")
    
    for symbol in symbols:
        if days_back == 0:
            print(f"Downloading {symbol} LATEST {interval} bar...")
        else:
            print(f"Downloading {symbol} {interval} bars ({days_back} days back)...")
        records = await download_symbol_data(provider, symbol, days_back, alpaca_interval)
        if records > 0:
            total_records += records
            successful_symbols.append(symbol)
        else:
            failed_symbols.append(symbol)
    
    status = "success" if len(failed_symbols) == 0 else "partial_success" if successful_symbols else "failure"
    range_text = "Latest bars" if days_back == 0 else f"{days_back} days back"
    message = f"Downloaded {interval} data for {len(successful_symbols)}/{len(symbols)} symbols ({range_text})"
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
async def download_single_symbol(symbol: str, days_back: int = Query(1, description="Number of days to go back (0 = Latest bar only)"), interval: str = Query('15Min', description="Time interval (Daily, Hourly, 30Min, 15Min)")):
    """
    Download price data for a single symbol.
    Uses configurable interval with appropriate delay.
    
    Args:
        symbol: Stock symbol to download
        days_back: Number of days to go back from current time (default: 1)
                  Set to 0 to get only the latest bar (optimal for automation)
        interval: Time interval (Daily, Hourly, 30Min, 15Min)
        
    Returns:
        DownloadResponse: Download results
    """
    # Map UI intervals to Alpaca format
    interval_mapping = {
        'Daily': '1Day',
        'Hourly': '1Hour', 
        '30Min': '30Min',
        '15Min': '15Min'
    }
    
    # Convert interval to Alpaca format
    alpaca_interval = interval_mapping.get(interval, '15Min')
    
    provider = get_alpaca_provider()
    symbol_upper = symbol.upper()
    
    if days_back == 0:
        print(f"Downloading {symbol_upper} LATEST {interval} bar...")
    else:
        print(f"Downloading {symbol_upper} {interval} bars ({days_back} days back)...")
    
    records = await download_symbol_data(provider, symbol_upper, days_back, alpaca_interval)
    
    if records > 0:
        range_text = "Latest bar" if days_back == 0 else f"{days_back} days back"
        return DownloadResponse(
            status="success",
            message=f"Downloaded {records} {interval} records for {symbol_upper} ({range_text})",
            symbols=[symbol_upper],
            records_downloaded=records,
            cache_updated=True
        )
    else:
        range_text = "Latest bar" if days_back == 0 else f"{days_back} days back"
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download {interval} data for {symbol_upper} ({range_text})"
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
    limit: int = 100,
    interval: Optional[str] = None
):
    """
    Get recent market data from cache - SMART QUERY for both daily and intraday data.
    
    Args:
        symbol: Optional symbol filter
        limit: Maximum number of records
        interval: Optional interval filter (Daily, Hourly, 30Min, 15Min)
        
    Returns:
        dict: Recent market data (daily or intraday based on what's available)
    """
    cache = get_cache()
    
    try:
        with cache._get_connection() as conn:
            # VIPER'S SMART LOGIC: Check which data is available and prioritize accordingly
            data = []
            columns = []
            
            # If specific interval requested, query that table
            if interval == 'Daily':
                # Query daily_prices table
                if symbol:
                    query = """
                    SELECT symbol, trading_date, open, high, low, close, volume,
                           trading_date as bar_timestamp
                    FROM daily_prices 
                    WHERE symbol = ?
                    ORDER BY trading_date DESC 
                    LIMIT ?
                    """
                    result = conn.execute(query, [symbol.upper(), limit]).fetchall()
                else:
                    query = """
                    SELECT symbol, trading_date, open, high, low, close, volume,
                           trading_date as bar_timestamp
                    FROM daily_prices 
                    ORDER BY trading_date DESC, symbol 
                    LIMIT ?
                    """
                    result = conn.execute(query, [limit]).fetchall()
                
                columns = ['symbol', 'trading_date', 'open', 'high', 'low', 'close', 'volume', 'bar_timestamp']
                data = [dict(zip(columns, row)) for row in result]
                
            elif interval in ['Hourly', '30Min', '15Min']:
                # Query intraday_prices table with specific timeframe
                timeframe_map = {
                    'Hourly': '1hour',
                    '30Min': '30min', 
                    '15Min': '15min'
                }
                timeframe = timeframe_map.get(interval, '15min')
                
                if symbol:
                    query = """
                    SELECT * FROM intraday_prices 
                    WHERE symbol = ? AND timeframe = ?
                    ORDER BY bar_timestamp DESC 
                    LIMIT ?
                    """
                    result = conn.execute(query, [symbol.upper(), timeframe, limit]).fetchall()
                else:
                    query = """
                    SELECT * FROM intraday_prices 
                    WHERE timeframe = ?
                    ORDER BY bar_timestamp DESC, symbol 
                    LIMIT ?
                    """
                    result = conn.execute(query, [timeframe, limit]).fetchall()
                    
                columns = [desc[0] for desc in conn.description]
                data = [dict(zip(columns, row)) for row in result]
                
            else:
                # NO INTERVAL SPECIFIED - SMART AUTO-DETECTION
                # Check what data we have and show the most recent/relevant
                
                # First check for daily data
                daily_count_query = "SELECT COUNT(*) FROM daily_prices"
                daily_count = conn.execute(daily_count_query).fetchone()[0]
                
                # Check for intraday data
                intraday_count_query = "SELECT COUNT(*) FROM intraday_prices"
                intraday_count = conn.execute(intraday_count_query).fetchone()[0]
                
                if daily_count > 0 and intraday_count == 0:
                    # Only daily data available - show daily
                    if symbol:
                        query = """
                        SELECT symbol, trading_date, open, high, low, close, volume,
                               trading_date as bar_timestamp
                        FROM daily_prices 
                        WHERE symbol = ?
                        ORDER BY trading_date DESC 
                        LIMIT ?
                        """
                        result = conn.execute(query, [symbol.upper(), limit]).fetchall()
                    else:
                        query = """
                        SELECT symbol, trading_date, open, high, low, close, volume,
                               trading_date as bar_timestamp
                        FROM daily_prices 
                        ORDER BY trading_date DESC, symbol 
                        LIMIT ?
                        """
                        result = conn.execute(query, [limit]).fetchall()
                    
                    columns = ['symbol', 'trading_date', 'open', 'high', 'low', 'close', 'volume', 'bar_timestamp']
                    data = [dict(zip(columns, row)) for row in result]
                    
                elif intraday_count > 0:
                    # Intraday data available - show 15min (default)
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
                    
                    columns = [desc[0] for desc in conn.description]
                    data = [dict(zip(columns, row)) for row in result]
                    
                else:
                    # No data available
                    data = []
                    columns = []
            
            return {
                "data": data,
                "count": len(data),
                "columns": columns,
                "data_source": "daily" if interval == 'Daily' or (not interval and daily_count > 0 and intraday_count == 0) else "intraday"
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


# =============================================================================
# HEBBNET MODEL INTEGRATION - BIOLOGICAL NEURAL NETWORKS FOR TRADING
# =============================================================================

class ModelStatusResponse(BaseModel):
    """Model status response."""
    status: str  # UNTRAINED, TRAINED, TRAINING
    confidence: float  # 0-100
    last_signal: Optional[str]  # BUY, SELL, HOLD, NONE
    accuracy: Optional[float]  # Model accuracy percentage


class TrainingRequest(BaseModel):
    """Training request body."""
    model: str  # hebbnet_v1, hebbnet_v2, hebbnet_v3
    epochs: int
    learning_rate: float
    symbols: List[str]


class TrainingStatusResponse(BaseModel):
    """Training status response."""
    status: str  # training, completed, failed, not_started
    current_epoch: Optional[int]
    total_epochs: Optional[int]
    current_loss: Optional[float]
    final_loss: Optional[float]
    error: Optional[str]


class PredictionRequest(BaseModel):
    """Prediction request body."""
    model: str
    symbols: Optional[List[str]] = None


class PredictionResponse(BaseModel):
    """Prediction response."""
    status: str
    message: str
    predictions: List[Dict[str, Any]]
    accuracy: Optional[float]


# Global model state management
model_states = {
    'hebbnet_v1': {'status': 'UNTRAINED', 'confidence': 0.0, 'last_signal': 'NONE'},
    'hebbnet_v2': {'status': 'UNTRAINED', 'confidence': 0.0, 'last_signal': 'NONE'},
    'hebbnet_v3': {'status': 'UNTRAINED', 'confidence': 0.0, 'last_signal': 'NONE'}
}

training_state = {
    'status': 'not_started',
    'current_epoch': 0,
    'total_epochs': 0,
    'current_loss': 0.0,
    'model': None,
    'should_stop': False
}


@router.get("/models/list")
async def list_models():
    """
    List available HebbNet models.
    
    Returns:
        dict: Available models with their status
    """
    models = []
    for model_id, state in model_states.items():
        model_name = {
            'hebbnet_v1': 'HebbNet v1.0 - Basic Spike Learning',
            'hebbnet_v2': 'HebbNet v2.0 - Advanced Plasticity', 
            'hebbnet_v3': 'HebbNet v3.0 - Multi-Layer STDP'
        }.get(model_id, model_id)
        
        models.append({
            'id': model_id,
            'name': model_name,
            'status': state['status'],
            'confidence': state['confidence'],
            'last_signal': state['last_signal']
        })
    
    return {
        'status': 'success',
        'models': models,
        'count': len(models)
    }


@router.get("/models/status/{model_id}", response_model=ModelStatusResponse)
async def get_model_status(model_id: str):
    """
    Get status of a specific HebbNet model.
    
    Args:
        model_id: Model identifier (hebbnet_v1, hebbnet_v2, hebbnet_v3)
        
    Returns:
        ModelStatusResponse: Model status information
    """
    if model_id not in model_states:
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_id} not found. Available: {list(model_states.keys())}"
        )
    
    state = model_states[model_id]
    return ModelStatusResponse(
        status=state['status'],
        confidence=state['confidence'],
        last_signal=state['last_signal'],
        accuracy=state.get('accuracy', None)
    )


@router.post("/models/save/{model_id}")
async def save_model(model_id: str):
    """
    Save trained HebbNet model weights to persistent storage.
    
    Args:
        model_id: Model identifier to save
        
    Returns:
        dict: Save operation result
    """
    if model_id not in model_states:
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_id} not found"
        )
    
    state = model_states[model_id]
    if state['status'] != 'TRAINED':
        raise HTTPException(
            status_code=400,
            detail=f"Cannot save untrained model. Status: {state['status']}"
        )
    
    try:
        # Create models directory if it doesn't exist
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # Save model metadata (weights will be implemented with actual HebbNet)
        model_file = models_dir / f"{model_id}.json"
        model_data = {
            'model_id': model_id,
            'status': state['status'],
            'confidence': state['confidence'],
            'last_signal': state['last_signal'],
            'accuracy': state.get('accuracy', 0.0),
            'saved_at': datetime.now().isoformat(),
            'weights_file': f"{model_id}_weights.pkl"  # Placeholder for actual weights
        }
        
        with open(model_file, 'w') as f:
            import json
            json.dump(model_data, f, indent=2)
        
        return {
            'status': 'success',
            'message': f'Model {model_id} saved successfully',
            'file': str(model_file)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save model: {str(e)}"
        )


@router.post("/models/load/{model_id}")
async def load_model(model_id: str):
    """
    Load HebbNet model weights from persistent storage.
    
    Args:
        model_id: Model identifier to load
        
    Returns:
        dict: Load operation result
    """
    if model_id not in model_states:
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_id} not found"
        )
    
    try:
        model_file = Path("models") / f"{model_id}.json"
        if not model_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No saved weights found for {model_id}"
            )
        
        with open(model_file, 'r') as f:
            import json
            model_data = json.load(f)
        
        # Update model state
        model_states[model_id].update({
            'status': model_data.get('status', 'TRAINED'),
            'confidence': model_data.get('confidence', 0.0),
            'last_signal': model_data.get('last_signal', 'NONE'),
            'accuracy': model_data.get('accuracy', 0.0)
        })
        
        return {
            'status': 'success',
            'message': f'Model {model_id} loaded successfully',
            'loaded_at': model_data.get('saved_at', 'unknown')
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No saved model found for {model_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {str(e)}"
        )


@router.post("/models/reset/{model_id}")
async def reset_model(model_id: str):
    """
    Reset HebbNet model to untrained state.
    
    Args:
        model_id: Model identifier to reset
        
    Returns:
        dict: Reset operation result
    """
    if model_id not in model_states:
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_id} not found"
        )
    
    try:
        # Reset model state
        model_states[model_id] = {
            'status': 'UNTRAINED',
            'confidence': 0.0,
            'last_signal': 'NONE',
            'accuracy': 0.0
        }
        
        # Delete saved model file if it exists
        model_file = Path("models") / f"{model_id}.json"
        if model_file.exists():
            model_file.unlink()
        
        return {
            'status': 'success',
            'message': f'Model {model_id} reset to untrained state'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset model: {str(e)}"
        )


@router.post("/models/train", response_model=dict)
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Start HebbNet model training with biological neural network learning.
    
    Args:
        request: Training configuration
        background_tasks: FastAPI background task manager
        
    Returns:
        dict: Training start confirmation
    """
    if request.model not in model_states:
        raise HTTPException(
            status_code=404,
            detail=f"Model {request.model} not found"
        )
    
    if training_state['status'] == 'training':
        raise HTTPException(
            status_code=400,
            detail="Training already in progress. Stop current training first."
        )
    
    # Validate parameters
    if request.epochs < 1 or request.epochs > 1000:
        raise HTTPException(
            status_code=400,
            detail="Epochs must be between 1 and 1000"
        )
    
    if request.learning_rate <= 0 or request.learning_rate > 0.1:
        raise HTTPException(
            status_code=400,
            detail="Learning rate must be between 0.0001 and 0.1"
        )
    
    if len(request.symbols) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one symbol is required for training"
        )
    
    try:
        # Initialize training state
        training_state.update({
            'status': 'training',
            'current_epoch': 0,
            'total_epochs': request.epochs,
            'current_loss': 1.0,  # Start with high loss
            'model': request.model,
            'should_stop': False,
            'learning_rate': request.learning_rate,
            'symbols': request.symbols
        })
        
        # Update model status
        model_states[request.model]['status'] = 'TRAINING'
        
        # Start training in background
        background_tasks.add_task(run_hebbnet_training, request)
        
        return {
            'status': 'success',
            'message': f'Training started for {request.model}',
            'epochs': request.epochs,
            'symbols': len(request.symbols),
            'learning_rate': request.learning_rate
        }
        
    except Exception as e:
        training_state['status'] = 'failed'
        model_states[request.model]['status'] = 'UNTRAINED'
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start training: {str(e)}"
        )


@router.get("/models/training/status", response_model=TrainingStatusResponse)
async def get_training_status():
    """
    Get current training status and progress.
    
    Returns:
        TrainingStatusResponse: Training progress information
    """
    return TrainingStatusResponse(
        status=training_state['status'],
        current_epoch=training_state.get('current_epoch'),
        total_epochs=training_state.get('total_epochs'),
        current_loss=training_state.get('current_loss'),
        final_loss=training_state.get('final_loss'),
        error=training_state.get('error')
    )


@router.post("/models/training/stop")
async def stop_training():
    """
    Stop current training process.
    
    Returns:
        dict: Stop operation result
    """
    if training_state['status'] != 'training':
        raise HTTPException(
            status_code=400,
            detail=f"No training in progress. Status: {training_state['status']}"
        )
    
    try:
        training_state['should_stop'] = True
        training_state['status'] = 'stopping'
        
        return {
            'status': 'success',
            'message': 'Training stop requested - will complete current epoch'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop training: {str(e)}"
        )


async def run_hebbnet_training(request: TrainingRequest):
    """
    Background task to run HebbNet training with biological learning rules.
    This simulates the training process - will be replaced with actual HebbNet implementation.
    """
    import asyncio
    import random
    
    try:
        print(f"🧠 Starting {request.model} training: {request.epochs} epochs, {len(request.symbols)} symbols")
        
        # Get training data from cache
        cache = get_cache()
        training_data = []
        
        with cache._get_connection() as conn:
            for symbol in request.symbols:
                # Get recent 15-minute data for training
                query = """
                SELECT symbol, bar_timestamp, open, high, low, close, volume 
                FROM intraday_prices 
                WHERE symbol = ? AND timeframe = '15min'
                ORDER BY bar_timestamp DESC 
                LIMIT 1000
                """
                result = conn.execute(query, [symbol]).fetchall()
                training_data.extend(result)
        
        if len(training_data) == 0:
            training_state['status'] = 'failed'
            training_state['error'] = 'No training data available - download market data first'
            model_states[request.model]['status'] = 'UNTRAINED'
            return
        
        print(f"🔬 Training with {len(training_data)} market data samples")
        
        # Simulate biological neural network training
        base_loss = 1.0
        for epoch in range(1, request.epochs + 1):
            if training_state['should_stop']:
                print("🛑 Training stopped by user request")
                training_state['status'] = 'stopped'
                model_states[request.model]['status'] = 'UNTRAINED'
                return
            
            # Simulate Hebbian learning progress
            progress = epoch / request.epochs
            current_loss = base_loss * (1.0 - progress * 0.8) + random.uniform(-0.05, 0.05)
            current_loss = max(0.01, current_loss)  # Ensure loss doesn't go negative
            
            training_state.update({
                'current_epoch': epoch,
                'current_loss': current_loss
            })
            
            # Simulate epoch duration (faster for demo)
            await asyncio.sleep(0.5)
        
        # Training completed successfully
        final_loss = training_state['current_loss']
        accuracy = max(50.0, 90.0 - final_loss * 40.0)  # Convert loss to accuracy
        confidence = min(95.0, accuracy - 5.0)
        
        training_state.update({
            'status': 'completed',
            'final_loss': final_loss
        })
        
        model_states[request.model].update({
            'status': 'TRAINED',
            'confidence': confidence,
            'accuracy': accuracy,
            'last_signal': 'NONE'  # Will be set when predictions are generated
        })
        
        print(f"🎯 {request.model} training completed! Loss: {final_loss:.4f}, Accuracy: {accuracy:.1f}%")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        training_state.update({
            'status': 'failed',
            'error': str(e)
        })
        model_states[request.model]['status'] = 'UNTRAINED'


@router.post("/models/predict", response_model=PredictionResponse)
async def generate_predictions(request: PredictionRequest):
    """
    Generate trading signals using trained HebbNet model.
    
    Args:
        request: Prediction request with model and optional symbols
        
    Returns:
        PredictionResponse: Generated predictions and signals
    """
    if request.model not in model_states:
        raise HTTPException(
            status_code=404,
            detail=f"Model {request.model} not found"
        )
    
    model_state = model_states[request.model]
    if model_state['status'] != 'TRAINED':
        raise HTTPException(
            status_code=400,
            detail=f"Model {request.model} is not trained. Status: {model_state['status']}"
        )
    
    try:
        # Get symbols to predict on
        symbols = request.symbols if request.symbols else load_watchlist()
        if not symbols:
            raise HTTPException(
                status_code=400,
                detail="No symbols provided and watchlist is empty"
            )
        
        # Get recent market data for predictions
        cache = get_cache()
        predictions = []
        
        with cache._get_connection() as conn:
            for symbol in symbols:
                # Get latest price data
                query = """
                SELECT symbol, close, bar_timestamp
                FROM intraday_prices 
                WHERE symbol = ? AND timeframe = '15min'
                ORDER BY bar_timestamp DESC 
                LIMIT 1
                """
                result = conn.execute(query, [symbol]).fetchone()
                
                if result:
                    # Generate HebbNet-based prediction (simulation)
                    import random
                    confidence = random.uniform(0.6, 0.95)  # 60-95% confidence
                    signal_prob = random.random()
                    
                    if signal_prob < 0.3:
                        signal = 'BUY'
                    elif signal_prob < 0.6:
                        signal = 'SELL'
                    else:
                        signal = 'HOLD'
                    
                    predictions.append({
                        'symbol': result[0],
                        'signal': signal,
                        'confidence': confidence,
                        'price': float(result[1]),
                        'timestamp': result[2]
                    })
        
        if predictions:
            # Update model state with latest signal
            latest_signal = predictions[0]['signal']
            model_states[request.model]['last_signal'] = latest_signal
            
        return PredictionResponse(
            status='success',
            message=f'Generated {len(predictions)} predictions using {request.model}',
            predictions=predictions,
            accuracy=model_state.get('accuracy', 0.0)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction generation failed: {str(e)}"
        )


@router.get("/models/signals/recent")
async def get_recent_signals(limit: int = 50):
    """
    Get recent trading signals from all models.
    
    Args:
        limit: Maximum number of recent signals to return
        
    Returns:
        dict: Recent signals data
    """
    try:
        # This is a placeholder - in real implementation, signals would be stored in database
        # For now, generate some sample recent signals
        import random
        from datetime import datetime, timedelta
        
        symbols = load_watchlist()[:10]  # Limit for demo
        predictions = []
        
        for i in range(min(limit, len(symbols) * 3)):
            symbol = random.choice(symbols)
            age_hours = random.randint(1, 24)
            timestamp = datetime.now() - timedelta(hours=age_hours)
            
            signal_prob = random.random()
            if signal_prob < 0.3:
                signal = 'BUY'
            elif signal_prob < 0.6:
                signal = 'SELL'
            else:
                signal = 'HOLD'
                
            predictions.append({
                'symbol': symbol,
                'signal': signal,
                'confidence': random.uniform(0.6, 0.95),
                'price': random.uniform(50.0, 300.0),
                'timestamp': timestamp.isoformat()
            })
        
        # Sort by timestamp descending
        predictions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'status': 'success',
            'predictions': predictions[:limit],
            'accuracy': 78.5  # Demo accuracy
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent signals: {str(e)}"
        )