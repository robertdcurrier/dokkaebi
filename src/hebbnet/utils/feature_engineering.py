#!/usr/bin/env python3
"""
Feature Engineering for HebbNet Trading
======================================
Extract and normalize market features for biological learning.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from scipy import signal


def extract_price_features(prices: np.ndarray, window_size: int = 20) -> np.ndarray:
    """
    Extract price-based features for HebbNet consumption
    
    Args:
        prices: Array of price data [open, high, low, close]
        window_size: Lookback window for feature calculation
        
    Returns:
        Normalized price features
    """
    if len(prices) < window_size:
        # Return zeros if insufficient data
        return np.zeros(10)
    
    # Assume prices is OHLC format
    if prices.ndim == 1:
        # Single price series
        closes = prices
        opens = closes
        highs = closes
        lows = closes
    else:
        # OHLC format
        opens = prices[:, 0] if prices.shape[1] > 0 else prices[:, -1]
        highs = prices[:, 1] if prices.shape[1] > 1 else prices[:, -1]
        lows = prices[:, 2] if prices.shape[1] > 2 else prices[:, -1]
        closes = prices[:, 3] if prices.shape[1] > 3 else prices[:, -1]
    
    features = []
    
    # 1. Price momentum (returns)
    returns_1 = (closes[-1] - closes[-2]) / closes[-2] if len(closes) > 1 else 0
    returns_5 = (closes[-1] - closes[-6]) / closes[-6] if len(closes) > 5 else 0
    returns_20 = (closes[-1] - closes[-21]) / closes[-21] if len(closes) > 20 else 0
    
    features.extend([returns_1, returns_5, returns_20])
    
    # 2. Volatility measures
    if len(closes) >= 5:
        recent_returns = np.diff(closes[-5:]) / closes[-5:-1]
        volatility_5 = np.std(recent_returns)
    else:
        volatility_5 = 0.0
    
    if len(closes) >= window_size:
        window_returns = np.diff(closes[-window_size:]) / closes[-window_size:-1]
        volatility_window = np.std(window_returns)
    else:
        volatility_window = volatility_5
    
    features.extend([volatility_5, volatility_window])
    
    # 3. Price position in range
    if len(closes) >= 10:
        recent_high = np.max(highs[-10:])
        recent_low = np.min(lows[-10:])
        
        if recent_high != recent_low:
            price_position = (closes[-1] - recent_low) / (recent_high - recent_low)
        else:
            price_position = 0.5
    else:
        price_position = 0.5
    
    features.append(price_position)
    
    # 4. Moving average relationships
    if len(closes) >= 20:
        ma_5 = np.mean(closes[-5:])
        ma_10 = np.mean(closes[-10:])
        ma_20 = np.mean(closes[-20:])
        
        price_vs_ma5 = (closes[-1] - ma_5) / ma_5
        price_vs_ma20 = (closes[-1] - ma_20) / ma_20
        
        features.extend([price_vs_ma5, price_vs_ma20])
    else:
        features.extend([0.0, 0.0])
    
    # 5. Gap analysis
    if len(opens) > 1 and len(closes) > 1:
        gap = (opens[-1] - closes[-2]) / closes[-2]
        features.append(gap)
    else:
        features.append(0.0)
    
    return np.array(features, dtype=np.float32)


def extract_volume_features(volumes: np.ndarray, prices: np.ndarray = None,
                          window_size: int = 20) -> np.ndarray:
    """
    Extract volume-based features
    
    Args:
        volumes: Volume data
        prices: Optional price data for volume-price analysis
        window_size: Lookback window
        
    Returns:
        Volume features
    """
    if len(volumes) < 2:
        return np.zeros(5)
    
    features = []
    
    # 1. Volume momentum
    volume_change_1 = (volumes[-1] - volumes[-2]) / (volumes[-2] + 1e-8)
    
    if len(volumes) >= 5:
        volume_avg_5 = np.mean(volumes[-5:])
        volume_ratio_5 = volumes[-1] / (volume_avg_5 + 1e-8)
    else:
        volume_ratio_5 = 1.0
    
    if len(volumes) >= window_size:
        volume_avg_window = np.mean(volumes[-window_size:])
        volume_ratio_window = volumes[-1] / (volume_avg_window + 1e-8)
    else:
        volume_ratio_window = volume_ratio_5
    
    features.extend([volume_change_1, volume_ratio_5, volume_ratio_window])
    
    # 2. Volume trend
    if len(volumes) >= 5:
        volume_trend = np.polyfit(range(5), volumes[-5:], 1)[0]
        volume_trend_normalized = volume_trend / (np.mean(volumes[-5:]) + 1e-8)
        features.append(volume_trend_normalized)
    else:
        features.append(0.0)
    
    # 3. Volume-price correlation
    if prices is not None and len(prices) >= 5 and len(volumes) >= 5:
        if prices.ndim == 1:
            price_series = prices[-5:]
        else:
            price_series = prices[-5:, 3]  # Use close prices
        
        price_changes = np.diff(price_series) / price_series[:-1]
        volume_changes = np.diff(volumes[-5:]) / volumes[-5:-1]
        
        if len(price_changes) == len(volume_changes) and len(price_changes) > 0:
            pv_correlation = np.corrcoef(price_changes, volume_changes)[0, 1]
            if np.isnan(pv_correlation):
                pv_correlation = 0.0
        else:
            pv_correlation = 0.0
        
        features.append(pv_correlation)
    else:
        features.append(0.0)
    
    return np.array(features, dtype=np.float32)


def extract_technical_indicators(ohlcv_data: np.ndarray, 
                                window_size: int = 20) -> np.ndarray:
    """
    Extract technical indicator features
    
    Args:
        ohlcv_data: OHLCV price data [open, high, low, close, volume]
        window_size: Lookback window for indicators
        
    Returns:
        Technical indicator features
    """
    if len(ohlcv_data) < 10:
        return np.zeros(15)
    
    # Extract OHLCV
    if ohlcv_data.ndim == 1:
        # Single price series
        closes = ohlcv_data
        opens = closes
        highs = closes
        lows = closes
        volumes = np.ones_like(closes)
    else:
        opens = ohlcv_data[:, 0]
        highs = ohlcv_data[:, 1] if ohlcv_data.shape[1] > 1 else opens
        lows = ohlcv_data[:, 2] if ohlcv_data.shape[1] > 2 else opens
        closes = ohlcv_data[:, 3] if ohlcv_data.shape[1] > 3 else opens
        volumes = ohlcv_data[:, 4] if ohlcv_data.shape[1] > 4 else np.ones_like(closes)
    
    features = []
    
    # 1. RSI (Relative Strength Index)
    rsi = calculate_rsi(closes, period=14)
    rsi_normalized = (rsi - 50) / 50  # Normalize to [-1, 1]
    features.append(rsi_normalized)
    
    # 2. MACD
    macd_line, signal_line = calculate_macd(closes)
    macd_histogram = macd_line - signal_line
    features.extend([macd_line, signal_line, macd_histogram])
    
    # 3. Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(closes, window_size)
    bb_position = (closes[-1] - bb_lower) / (bb_upper - bb_lower + 1e-8)
    bb_width = (bb_upper - bb_lower) / bb_middle
    
    features.extend([bb_position, bb_width])
    
    # 4. Stochastic Oscillator
    stoch_k, stoch_d = calculate_stochastic(highs, lows, closes)
    features.extend([stoch_k / 100, stoch_d / 100])  # Normalize to [0, 1]
    
    # 5. ATR (Average True Range)
    atr = calculate_atr(highs, lows, closes)
    atr_normalized = atr / closes[-1]  # Normalize by current price
    features.append(atr_normalized)
    
    # 6. Williams %R
    williams_r = calculate_williams_r(highs, lows, closes)
    williams_r_normalized = williams_r / 100  # Normalize to [-1, 0]
    features.append(williams_r_normalized)
    
    # 7. Commodity Channel Index (CCI)
    cci = calculate_cci(highs, lows, closes)
    cci_normalized = np.tanh(cci / 200)  # Squash to [-1, 1]
    features.append(cci_normalized)
    
    # 8. Rate of Change (ROC)
    roc = calculate_roc(closes, period=10)
    features.append(roc)
    
    # 9. Money Flow Index (requires volume)
    mfi = calculate_mfi(highs, lows, closes, volumes)
    mfi_normalized = (mfi - 50) / 50  # Normalize to [-1, 1]
    features.append(mfi_normalized)
    
    # 10. Momentum
    momentum = calculate_momentum(closes, period=10)
    features.append(momentum)
    
    return np.array(features, dtype=np.float32)


def normalize_features(features: np.ndarray, 
                      method: str = 'zscore') -> np.ndarray:
    """
    Normalize features for HebbNet consumption
    
    Args:
        features: Raw features
        method: Normalization method ('zscore', 'minmax', 'robust')
        
    Returns:
        Normalized features
    """
    if features.ndim == 1:
        features = features.reshape(1, -1)
    
    if method == 'zscore':
        # Z-score normalization
        mean = np.mean(features, axis=0)
        std = np.std(features, axis=0) + 1e-8
        normalized = (features - mean) / std
        
    elif method == 'minmax':
        # Min-max scaling to [0, 1]
        min_vals = np.min(features, axis=0)
        max_vals = np.max(features, axis=0)
        range_vals = max_vals - min_vals + 1e-8
        normalized = (features - min_vals) / range_vals
        
    elif method == 'robust':
        # Robust scaling using median and IQR
        median = np.median(features, axis=0)
        q75 = np.percentile(features, 75, axis=0)
        q25 = np.percentile(features, 25, axis=0)
        iqr = q75 - q25 + 1e-8
        normalized = (features - median) / iqr
        
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    # Clip extreme values
    normalized = np.clip(normalized, -5, 5)
    
    return normalized


def create_feature_vector(ohlcv_data: np.ndarray, 
                         config: 'TradingConfig' = None) -> np.ndarray:
    """
    Create complete feature vector for HebbNet
    
    Args:
        ohlcv_data: OHLCV market data
        config: Trading configuration
        
    Returns:
        Complete normalized feature vector
    """
    if config is None:
        window_size = 20
    else:
        window_size = min(config.window_size // 5, 50)  # Reasonable window
    
    # Extract different feature types
    if ohlcv_data.ndim == 1:
        # Single price series
        price_features = extract_price_features(ohlcv_data, window_size)
        volume_features = np.zeros(5)  # No volume data
        technical_features = extract_technical_indicators(ohlcv_data, window_size)
    else:
        # Full OHLCV data
        price_features = extract_price_features(ohlcv_data[:, :4], window_size)
        
        if ohlcv_data.shape[1] >= 5:
            volume_features = extract_volume_features(
                ohlcv_data[:, 4], 
                ohlcv_data[:, :4], 
                window_size
            )
        else:
            volume_features = np.zeros(5)
        
        technical_features = extract_technical_indicators(ohlcv_data, window_size)
    
    # Combine all features
    all_features = np.concatenate([
        price_features,
        volume_features,
        technical_features
    ])
    
    # Normalize
    normalized_features = normalize_features(all_features.reshape(1, -1))[0]
    
    return normalized_features


# Technical Indicator Calculations
def calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
    """Calculate RSI"""
    if len(prices) < period + 1:
        return 50.0  # Neutral RSI
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices: np.ndarray, fast: int = 12, slow: int = 26, 
                  signal_period: int = 9) -> Tuple[float, float]:
    """Calculate MACD"""
    if len(prices) < slow:
        return 0.0, 0.0
    
    # Simple approximation using moving averages
    ema_fast = np.mean(prices[-fast:])
    ema_slow = np.mean(prices[-slow:])
    
    macd_line = (ema_fast - ema_slow) / prices[-1]
    
    # Simple signal line approximation
    signal_line = macd_line * 0.9  # Simplified
    
    return macd_line, signal_line


def calculate_bollinger_bands(prices: np.ndarray, period: int = 20, 
                            std_dev: float = 2.0) -> Tuple[float, float, float]:
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        price = prices[-1]
        return price * 1.02, price, price * 0.98
    
    middle = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    return upper, middle, lower


def calculate_stochastic(highs: np.ndarray, lows: np.ndarray, 
                        closes: np.ndarray, k_period: int = 14) -> Tuple[float, float]:
    """Calculate Stochastic Oscillator"""
    if len(closes) < k_period:
        return 50.0, 50.0
    
    highest_high = np.max(highs[-k_period:])
    lowest_low = np.min(lows[-k_period:])
    
    if highest_high == lowest_low:
        k_percent = 50.0
    else:
        k_percent = 100 * (closes[-1] - lowest_low) / (highest_high - lowest_low)
    
    # Simple %D calculation (3-period SMA of %K)
    d_percent = k_percent * 0.8 + 20  # Simplified
    
    return k_percent, d_percent


def calculate_atr(highs: np.ndarray, lows: np.ndarray, 
                 closes: np.ndarray, period: int = 14) -> float:
    """Calculate Average True Range"""
    if len(closes) < 2:
        return 0.01
    
    # True Range calculations
    high_low = highs[-period:] - lows[-period:]
    high_close = np.abs(highs[-period:] - closes[-period-1:-1])
    low_close = np.abs(lows[-period:] - closes[-period-1:-1])
    
    true_ranges = np.maximum(high_low, np.maximum(high_close, low_close))
    atr = np.mean(true_ranges)
    
    return atr


def calculate_williams_r(highs: np.ndarray, lows: np.ndarray, 
                        closes: np.ndarray, period: int = 14) -> float:
    """Calculate Williams %R"""
    if len(closes) < period:
        return -50.0
    
    highest_high = np.max(highs[-period:])
    lowest_low = np.min(lows[-period:])
    
    if highest_high == lowest_low:
        return -50.0
    
    williams_r = -100 * (highest_high - closes[-1]) / (highest_high - lowest_low)
    
    return williams_r


def calculate_cci(highs: np.ndarray, lows: np.ndarray, 
                 closes: np.ndarray, period: int = 20) -> float:
    """Calculate Commodity Channel Index"""
    if len(closes) < period:
        return 0.0
    
    typical_prices = (highs[-period:] + lows[-period:] + closes[-period:]) / 3
    sma = np.mean(typical_prices)
    mad = np.mean(np.abs(typical_prices - sma))
    
    if mad == 0:
        return 0.0
    
    cci = (typical_prices[-1] - sma) / (0.015 * mad)
    
    return cci


def calculate_roc(prices: np.ndarray, period: int = 10) -> float:
    """Calculate Rate of Change"""
    if len(prices) < period + 1:
        return 0.0
    
    roc = (prices[-1] - prices[-period-1]) / prices[-period-1]
    
    return roc


def calculate_mfi(highs: np.ndarray, lows: np.ndarray, 
                 closes: np.ndarray, volumes: np.ndarray, period: int = 14) -> float:
    """Calculate Money Flow Index"""
    if len(closes) < period + 1:
        return 50.0
    
    typical_prices = (highs[-period-1:] + lows[-period-1:] + closes[-period-1:]) / 3
    raw_money_flow = typical_prices * volumes[-period-1:]
    
    positive_flow = 0
    negative_flow = 0
    
    for i in range(1, len(typical_prices)):
        if typical_prices[i] > typical_prices[i-1]:
            positive_flow += raw_money_flow[i]
        elif typical_prices[i] < typical_prices[i-1]:
            negative_flow += raw_money_flow[i]
    
    if negative_flow == 0:
        return 100.0
    
    money_ratio = positive_flow / negative_flow
    mfi = 100 - (100 / (1 + money_ratio))
    
    return mfi


def calculate_momentum(prices: np.ndarray, period: int = 10) -> float:
    """Calculate Momentum"""
    if len(prices) < period + 1:
        return 0.0
    
    momentum = (prices[-1] - prices[-period-1]) / prices[-period-1]
    
    return momentum