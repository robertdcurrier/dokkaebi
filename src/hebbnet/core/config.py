#!/usr/bin/env python3
"""
TradingConfig - Configuration for DOKKAEBI HebbNet Trading System
================================================================
Adapted from MaritimeConfig for financial market operations.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class TradingConfig:
    """DOKKAEBI trading configuration - tuned for financial markets"""
    
    # Temporal parameters - financial market timing
    window_size: int = 300          # 5-minute windows (300 seconds)
    step_size: int = 60             # 1-minute overlap for smoothing
    sampling_rate: int = 1          # 1Hz data collection
    
    # Network architecture - optimized for trading features
    hidden_size: int = 200          # Fewer neurons than maritime
    ensemble_size: int = 5          # Odd number for tie-breaking
    
    # Learning parameters - adapted from proven HebbNet
    eta_base: float = 0.025         # Base learning rate
    alpha: float = 0.01             # Win rate learning
    beta: float = 0.5               # Conscience mechanism strength
    gamma: float = 0.05             # Refractory period
    
    # Competition parameters
    k: int = 2                      # Top-k winner updates
    responsibilities: List[float] = None
    
    # Trading-specific thresholds
    buy_threshold: float = 0.6      # Confidence for BUY signal
    sell_threshold: float = 0.6     # Confidence for SELL signal
    hold_range: float = 0.3         # Neutral zone around 0.5
    
    # Anomaly detection
    anomaly_threshold: float = 2.5  # Z-score threshold
    baseline_samples: int = 1000    # Samples for baseline
    
    # Feature engineering
    price_features: int = 10        # OHLCV + derived features
    volume_features: int = 5        # Volume-based features
    technical_features: int = 15    # Technical indicators
    
    # Risk management
    max_position_size: float = 1.0  # Maximum position (100%)
    stop_loss: float = 0.02         # 2% stop loss
    take_profit: float = 0.04       # 4% take profit
    
    # Performance tracking
    lookback_days: int = 30         # Performance history
    min_training_samples: int = 500 # Minimum for training
    
    def __post_init__(self):
        """Initialize derived parameters"""
        if self.responsibilities is None:
            self.responsibilities = [0.7, 0.3]  # Winner takes 70%
        
        # Calculate total feature count
        self.total_features = (
            self.price_features + 
            self.volume_features + 
            self.technical_features
        )
    
    def get_signal_thresholds(self) -> Dict[str, float]:
        """Get trading signal confidence thresholds"""
        return {
            'strong_buy': self.buy_threshold + 0.2,
            'buy': self.buy_threshold,
            'hold_high': 0.5 + self.hold_range,
            'hold_low': 0.5 - self.hold_range,
            'sell': -self.sell_threshold,
            'strong_sell': -(self.sell_threshold + 0.2)
        }
    
    def validate_config(self) -> bool:
        """Validate configuration parameters"""
        assert self.window_size > 0, "Window size must be positive"
        assert self.hidden_size > 0, "Hidden size must be positive"
        assert 0 < self.eta_base < 1, "Learning rate must be (0, 1)"
        assert self.ensemble_size % 2 == 1, "Ensemble size must be odd"
        assert len(self.responsibilities) == self.k, "Responsibilities length must equal k"
        assert abs(sum(self.responsibilities) - 1.0) < 1e-6, "Responsibilities must sum to 1"
        
        return True


@dataclass
class SpecialistConfig:
    """Configuration for specialist networks"""
    
    # Network parameters
    hidden_size: int = 100          # Smaller than main network
    eta_base: float = 0.03          # Slightly higher learning rate
    
    # Specialization focus
    specialist_type: str = "general" # price, volume, momentum
    feature_subset: List[int] = None # Which features to focus on
    
    # Competition parameters
    k: int = 1                      # Single winner for specialists
    responsibilities: List[float] = None
    
    def __post_init__(self):
        """Initialize specialist parameters"""
        if self.responsibilities is None:
            self.responsibilities = [1.0]  # Single winner gets all