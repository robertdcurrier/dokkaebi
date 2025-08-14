#!/usr/bin/env python3
"""
DOKKAEBI HebbNet - Biological Learning for Trading
================================================
Biologically-inspired neural networks for financial market analysis.
"""

from .core.hebbnet import HebbNet
from .core.ensemble import HebbNetEnsemble
from .core.config import TradingConfig, SpecialistConfig

from .models.trading_hebbnet import TradingHebbNet, TradingEnsemble
from .models.specialist_nets import (
    PricePatternNet, VolumeAnalysisNet, MomentumNet, 
    SpecialistEnsemble
)

from .utils.feature_engineering import (
    extract_price_features,
    extract_volume_features, 
    extract_technical_indicators,
    normalize_features,
    create_feature_vector
)

from .utils.persistence import (
    save_model,
    load_model,
    list_saved_models,
    ModelPersistence
)

# Version info
__version__ = "1.0.0"
__author__ = "VIPER - The BIOLOGICAL REBELLION"
__description__ = "Hebbian learning networks for trading - NO BACKPROP!"

# Main exports
__all__ = [
    # Core components
    'HebbNet',
    'HebbNetEnsemble', 
    'TradingConfig',
    'SpecialistConfig',
    
    # Trading models
    'TradingHebbNet',
    'TradingEnsemble',
    
    # Specialists
    'PricePatternNet',
    'VolumeAnalysisNet', 
    'MomentumNet',
    'SpecialistEnsemble',
    
    # Feature engineering
    'extract_price_features',
    'extract_volume_features',
    'extract_technical_indicators',
    'normalize_features',
    'create_feature_vector',
    
    # Persistence
    'save_model',
    'load_model', 
    'list_saved_models',
    'ModelPersistence'
]