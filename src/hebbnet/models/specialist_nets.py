#!/usr/bin/env python3
"""
Specialist HebbNets - Focused networks for specific market patterns
================================================================
Specialized networks for price patterns, volume analysis, and momentum.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod

from ..core.hebbnet import HebbNet
from ..core.config import TradingConfig, SpecialistConfig


class SpecialistHebbNet(HebbNet, ABC):
    """
    Abstract base class for specialist HebbNets
    
    Each specialist focuses on specific market patterns:
    - Price patterns (support/resistance, breakouts)
    - Volume patterns (accumulation/distribution) 
    - Momentum patterns (trend changes, divergences)
    """
    
    def __init__(self, input_size: int, config: TradingConfig,
                 specialist_config: SpecialistConfig, seed: Optional[int] = None):
        """Initialize specialist network"""
        # Create reduced config for specialist
        specialist_trading_config = TradingConfig()
        specialist_trading_config.hidden_size = specialist_config.hidden_size
        specialist_trading_config.eta_base = specialist_config.eta_base
        specialist_trading_config.k = specialist_config.k
        specialist_trading_config.responsibilities = specialist_config.responsibilities
        
        super().__init__(input_size, specialist_trading_config, seed)
        
        self.specialist_type = specialist_config.specialist_type
        self.feature_subset = specialist_config.feature_subset
        self.specialist_config = specialist_config
        
        # Specialist-specific tracking
        self.pattern_detections = 0
        self.false_positives = 0
        self.confidence_history = []
    
    @abstractmethod
    def extract_specialist_features(self, market_data: np.ndarray) -> np.ndarray:
        """Extract features specific to this specialist"""
        pass
    
    @abstractmethod
    def interpret_prediction(self, prediction: int, confidence: float) -> Dict[str, Any]:
        """Interpret prediction in specialist context"""
        pass
    
    def get_specialist_signal(self, market_data: np.ndarray) -> Dict[str, Any]:
        """Generate specialist-specific signal"""
        features = self.extract_specialist_features(market_data)
        prediction = self.predict(features)
        probabilities = self.predict_proba(features)
        confidence = np.max(probabilities)
        
        signal_info = self.interpret_prediction(prediction, confidence)
        
        return {
            'specialist_type': self.specialist_type,
            'signal': prediction,
            'confidence': confidence,
            'probabilities': probabilities.tolist(),
            'pattern_info': signal_info,
            'feature_count': len(features)
        }


class PricePatternNet(SpecialistHebbNet):
    """
    Specialist for price patterns and technical levels
    
    Focus areas:
    - Support and resistance levels
    - Chart patterns (triangles, flags, etc.)
    - Breakouts and breakdowns
    - Price action signals
    """
    
    def __init__(self, input_size: int, config: TradingConfig, 
                 seed: Optional[int] = None):
        """Initialize price pattern specialist"""
        specialist_config = SpecialistConfig(
            specialist_type="price_pattern",
            hidden_size=80,
            eta_base=0.03
        )
        super().__init__(input_size, config, specialist_config, seed)
        
        # Price pattern specific
        self.support_levels = []
        self.resistance_levels = []
        self.breakout_threshold = 0.02  # 2% breakout
    
    def extract_specialist_features(self, market_data: np.ndarray) -> np.ndarray:
        """
        Extract price pattern features
        
        Args:
            market_data: OHLCV + indicators array
            
        Returns:
            Price pattern focused features
        """
        if len(market_data) < 20:
            return np.zeros(15)  # Return zeros if insufficient data
        
        # Assume market_data columns: [open, high, low, close, volume, ...]
        prices = market_data[:, :4]  # OHLC
        closes = market_data[:, 3]   # Close prices
        
        features = []
        
        # 1. Price momentum features
        price_change_1 = (closes[-1] - closes[-2]) / closes[-2] if len(closes) > 1 else 0
        price_change_5 = (closes[-1] - closes[-6]) / closes[-6] if len(closes) > 5 else 0
        price_change_20 = (closes[-1] - closes[-21]) / closes[-21] if len(closes) > 20 else 0
        
        features.extend([price_change_1, price_change_5, price_change_20])
        
        # 2. Volatility features
        returns = np.diff(closes) / closes[:-1] if len(closes) > 1 else [0]
        volatility_5 = np.std(returns[-5:]) if len(returns) >= 5 else 0
        volatility_20 = np.std(returns[-20:]) if len(returns) >= 20 else 0
        
        features.extend([volatility_5, volatility_20])
        
        # 3. Support/Resistance proximity
        recent_lows = np.min(closes[-10:]) if len(closes) >= 10 else closes[-1]
        recent_highs = np.max(closes[-10:]) if len(closes) >= 10 else closes[-1]
        
        support_distance = (closes[-1] - recent_lows) / recent_lows
        resistance_distance = (recent_highs - closes[-1]) / closes[-1]
        
        features.extend([support_distance, resistance_distance])
        
        # 4. Range analysis
        current_range = (recent_highs - recent_lows) / recent_lows
        range_position = (closes[-1] - recent_lows) / (recent_highs - recent_lows + 1e-8)
        
        features.extend([current_range, range_position])
        
        # 5. Candle patterns (simplified)
        if len(prices) >= 3:
            # Doji detection
            body_size = abs(prices[-1, 3] - prices[-1, 0]) / prices[-1, 0]  # Close-Open
            is_doji = 1.0 if body_size < 0.002 else 0.0
            
            # Hammer/Shooting star
            upper_shadow = (prices[-1, 1] - max(prices[-1, 0], prices[-1, 3])) / prices[-1, 3]
            lower_shadow = (min(prices[-1, 0], prices[-1, 3]) - prices[-1, 2]) / prices[-1, 3]
            
            features.extend([is_doji, upper_shadow, lower_shadow])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        # 6. Moving average relationships
        if len(closes) >= 20:
            ma_5 = np.mean(closes[-5:])
            ma_20 = np.mean(closes[-20:])
            
            price_vs_ma5 = (closes[-1] - ma_5) / ma_5
            price_vs_ma20 = (closes[-1] - ma_20) / ma_20
            ma_relationship = (ma_5 - ma_20) / ma_20
            
            features.extend([price_vs_ma5, price_vs_ma20, ma_relationship])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        return np.array(features, dtype=np.float32)
    
    def interpret_prediction(self, prediction: int, confidence: float) -> Dict[str, Any]:
        """Interpret prediction for price patterns"""
        pattern_strength = 'WEAK'
        if confidence > 0.8:
            pattern_strength = 'STRONG'
        elif confidence > 0.6:
            pattern_strength = 'MEDIUM'
        
        pattern_type = 'UNKNOWN'
        if prediction == 1 and confidence > 0.7:
            pattern_type = 'BULLISH_BREAKOUT'
        elif prediction == -1 and confidence > 0.7:
            pattern_type = 'BEARISH_BREAKDOWN'
        elif prediction == 0:
            pattern_type = 'RANGE_BOUND'
        
        return {
            'pattern_type': pattern_type,
            'strength': pattern_strength,
            'confidence': confidence,
            'breakout_probability': confidence if abs(prediction) == 1 else 0.0
        }


class VolumeAnalysisNet(SpecialistHebbNet):
    """
    Specialist for volume patterns and flow analysis
    
    Focus areas:
    - Volume accumulation/distribution
    - Volume breakouts
    - Price-volume divergence
    - Institutional flow detection
    """
    
    def __init__(self, input_size: int, config: TradingConfig, 
                 seed: Optional[int] = None):
        """Initialize volume analysis specialist"""
        specialist_config = SpecialistConfig(
            specialist_type="volume_analysis", 
            hidden_size=60,
            eta_base=0.035
        )
        super().__init__(input_size, config, specialist_config, seed)
        
        # Volume-specific tracking
        self.avg_volume_window = 20
        self.volume_spike_threshold = 2.0  # 2x average volume
    
    def extract_specialist_features(self, market_data: np.ndarray) -> np.ndarray:
        """Extract volume-focused features"""
        if len(market_data) < 5:
            return np.zeros(10)
        
        # Assume volume is column 4
        volumes = market_data[:, 4] if market_data.shape[1] > 4 else np.ones(len(market_data))
        prices = market_data[:, 3]  # Close prices
        
        features = []
        
        # 1. Volume trends
        volume_avg_5 = np.mean(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
        volume_avg_20 = np.mean(volumes[-20:]) if len(volumes) >= 20 else volume_avg_5
        
        volume_ratio_5 = volumes[-1] / (volume_avg_5 + 1e-8)
        volume_ratio_20 = volumes[-1] / (volume_avg_20 + 1e-8)
        
        features.extend([volume_ratio_5, volume_ratio_20])
        
        # 2. Volume momentum
        volume_change_1 = (volumes[-1] - volumes[-2]) / (volumes[-2] + 1e-8) if len(volumes) > 1 else 0
        volume_trend_5 = np.polyfit(range(5), volumes[-5:], 1)[0] if len(volumes) >= 5 else 0
        
        features.extend([volume_change_1, volume_trend_5])
        
        # 3. Price-Volume relationship
        price_change_1 = (prices[-1] - prices[-2]) / prices[-2] if len(prices) > 1 else 0
        pv_correlation = price_change_1 * volume_change_1  # Simple correlation proxy
        
        features.append(pv_correlation)
        
        # 4. Volume distribution analysis
        if len(volumes) >= 20:
            volume_percentile = np.percentile(volumes[-20:], 80)
            volume_position = (volumes[-1] - np.min(volumes[-20:])) / (np.max(volumes[-20:]) - np.min(volumes[-20:]) + 1e-8)
            features.extend([volume_percentile / (volume_avg_20 + 1e-8), volume_position])
        else:
            features.extend([1.0, 0.5])
        
        # 5. Volume spikes detection
        is_volume_spike = 1.0 if volume_ratio_20 > self.volume_spike_threshold else 0.0
        spike_with_price_up = 1.0 if (is_volume_spike and price_change_1 > 0) else 0.0
        spike_with_price_down = 1.0 if (is_volume_spike and price_change_1 < 0) else 0.0
        
        features.extend([is_volume_spike, spike_with_price_up, spike_with_price_down])
        
        return np.array(features, dtype=np.float32)
    
    def interpret_prediction(self, prediction: int, confidence: float) -> Dict[str, Any]:
        """Interpret volume analysis prediction"""
        flow_strength = 'WEAK'
        if confidence > 0.8:
            flow_strength = 'STRONG'
        elif confidence > 0.6:
            flow_strength = 'MEDIUM'
        
        flow_type = 'NEUTRAL'
        if prediction == 1:
            flow_type = 'ACCUMULATION'
        elif prediction == -1:
            flow_type = 'DISTRIBUTION'
        
        return {
            'flow_type': flow_type,
            'strength': flow_strength,
            'confidence': confidence,
            'institutional_activity': confidence > 0.75
        }


class MomentumNet(SpecialistHebbNet):
    """
    Specialist for momentum and trend analysis
    
    Focus areas:
    - Trend strength and direction
    - Momentum divergences
    - Momentum oscillator signals
    - Trend change detection
    """
    
    def __init__(self, input_size: int, config: TradingConfig, 
                 seed: Optional[int] = None):
        """Initialize momentum specialist"""
        specialist_config = SpecialistConfig(
            specialist_type="momentum",
            hidden_size=70,
            eta_base=0.028
        )
        super().__init__(input_size, config, specialist_config, seed)
        
        # Momentum-specific parameters
        self.rsi_period = 14
        self.momentum_lookback = 10
    
    def extract_specialist_features(self, market_data: np.ndarray) -> np.ndarray:
        """Extract momentum and trend features"""
        if len(market_data) < 10:
            return np.zeros(12)
        
        prices = market_data[:, 3]  # Close prices
        
        features = []
        
        # 1. Simple momentum
        momentum_1 = (prices[-1] / prices[-2] - 1) if len(prices) > 1 else 0
        momentum_5 = (prices[-1] / prices[-6] - 1) if len(prices) > 5 else 0
        momentum_10 = (prices[-1] / prices[-11] - 1) if len(prices) > 10 else 0
        
        features.extend([momentum_1, momentum_5, momentum_10])
        
        # 2. Rate of change
        roc_5 = momentum_5 * 5  # Annualized
        roc_10 = momentum_10 * 2  # Scaled
        
        features.extend([roc_5, roc_10])
        
        # 3. Trend strength (linear regression slope)
        if len(prices) >= 10:
            trend_5 = np.polyfit(range(5), prices[-5:], 1)[0] / np.mean(prices[-5:])
            trend_10 = np.polyfit(range(10), prices[-10:], 1)[0] / np.mean(prices[-10:])
            features.extend([trend_5, trend_10])
        else:
            features.extend([0.0, 0.0])
        
        # 4. Momentum acceleration
        if len(prices) >= 5:
            accel = (momentum_1 - momentum_5) * 10  # Scale for sensitivity
            features.append(accel)
        else:
            features.append(0.0)
        
        # 5. Simple RSI approximation
        if len(prices) >= 15:
            price_changes = np.diff(prices[-15:])
            gains = np.where(price_changes > 0, price_changes, 0)
            losses = np.where(price_changes < 0, -price_changes, 0)
            
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 100
                
            rsi_normalized = (rsi - 50) / 50  # Normalize to [-1, 1]
            features.append(rsi_normalized)
        else:
            features.append(0.0)
        
        # 6. Moving average convergence/divergence
        if len(prices) >= 26:
            ema_12 = self._calculate_ema(prices, 12)
            ema_26 = self._calculate_ema(prices, 26)
            
            macd_line = (ema_12[-1] - ema_26[-1]) / prices[-1]
            features.append(macd_line)
        else:
            features.append(0.0)
        
        # 7. Volatility-adjusted momentum
        if len(prices) >= 10:
            returns = np.diff(prices[-10:]) / prices[-10:-1]
            volatility = np.std(returns)
            vol_adj_momentum = momentum_10 / (volatility + 1e-8)
            features.append(vol_adj_momentum)
        else:
            features.append(0.0)
        
        return np.array(features, dtype=np.float32)
    
    def interpret_prediction(self, prediction: int, confidence: float) -> Dict[str, Any]:
        """Interpret momentum prediction"""
        momentum_strength = 'WEAK'
        if confidence > 0.8:
            momentum_strength = 'STRONG'
        elif confidence > 0.6:
            momentum_strength = 'MEDIUM'
        
        momentum_type = 'SIDEWAYS'
        if prediction == 1:
            momentum_type = 'BULLISH'
        elif prediction == -1:
            momentum_type = 'BEARISH'
        
        return {
            'momentum_type': momentum_type,
            'strength': momentum_strength,
            'confidence': confidence,
            'trend_change_probability': confidence if prediction != 0 else 0.0
        }
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate exponential moving average"""
        if len(prices) < period:
            return np.array([prices[-1]] * len(prices))
        
        alpha = 2.0 / (period + 1)
        ema = [prices[0]]
        
        for price in prices[1:]:
            ema.append(alpha * price + (1 - alpha) * ema[-1])
        
        return np.array(ema)


class SpecialistEnsemble:
    """
    Ensemble of specialist HebbNets for comprehensive market analysis
    """
    
    def __init__(self, input_size: int, config: TradingConfig):
        """Initialize specialist ensemble"""
        self.input_size = input_size
        self.config = config
        
        # Create specialists
        self.price_specialist = PricePatternNet(input_size, config)
        self.volume_specialist = VolumeAnalysisNet(input_size, config)  
        self.momentum_specialist = MomentumNet(input_size, config)
        
        self.specialists = [
            self.price_specialist,
            self.volume_specialist,
            self.momentum_specialist
        ]
        
        self.is_trained = False
    
    def train_specialists(self, X_train: np.ndarray, y_train: np.ndarray,
                         X_val: np.ndarray, y_val: np.ndarray,
                         epochs: int = 10) -> Dict[str, Any]:
        """Train all specialist networks"""
        print("🎯 Training specialist ensemble...")
        
        results = {}
        
        for specialist in self.specialists:
            print(f"  Training {specialist.specialist_type} specialist...")
            
            # Train specialist
            for epoch in range(epochs):
                indices = np.random.permutation(len(X_train))
                
                for idx in indices:
                    specialist.train_step(X_train[idx])
                
                # Periodic reseeding
                if epoch % 3 == 0:
                    specialist.reseed_dead_neurons(X_train)
            
            # Learn mapping
            specialist.learn_mapping(X_val, y_val, n_classes=3)
            
            # Evaluate
            accuracy = self._evaluate_specialist(specialist, X_val, y_val)
            results[specialist.specialist_type] = {
                'accuracy': accuracy,
                'neurons': specialist.hidden_size,
                'statistics': specialist.get_statistics()
            }
            
            print(f"    ✅ {specialist.specialist_type}: {accuracy:.1%}")
        
        self.is_trained = True
        return results
    
    def get_comprehensive_analysis(self, market_data: np.ndarray) -> Dict[str, Any]:
        """Get analysis from all specialists"""
        if not self.is_trained:
            raise ValueError("Specialists not trained!")
        
        analysis = {}
        
        for specialist in self.specialists:
            signal = specialist.get_specialist_signal(market_data)
            analysis[specialist.specialist_type] = signal
        
        # Create consensus
        signals = [analysis[s.specialist_type]['signal'] for s in self.specialists]
        confidences = [analysis[s.specialist_type]['confidence'] for s in self.specialists]
        
        consensus_signal = self._calculate_consensus(signals, confidences)
        
        analysis['consensus'] = {
            'signal': consensus_signal,
            'agreement_score': self._calculate_agreement(signals),
            'avg_confidence': np.mean(confidences),
            'specialist_count': len(self.specialists)
        }
        
        return analysis
    
    def _evaluate_specialist(self, specialist: SpecialistHebbNet,
                           X_val: np.ndarray, y_val: np.ndarray) -> float:
        """Evaluate specialist accuracy"""
        correct = 0
        for x, y in zip(X_val, y_val):
            pred = specialist.predict(x)
            if pred == y:
                correct += 1
        
        return correct / len(y_val) if len(y_val) > 0 else 0.0
    
    def _calculate_consensus(self, signals: List[int], 
                           confidences: List[float]) -> int:
        """Calculate weighted consensus signal"""
        weighted_vote = 0.0
        total_weight = 0.0
        
        for signal, confidence in zip(signals, confidences):
            weighted_vote += signal * confidence
            total_weight += confidence
        
        if total_weight > 0:
            avg_signal = weighted_vote / total_weight
            return 1 if avg_signal > 0.3 else (-1 if avg_signal < -0.3 else 0)
        else:
            return 0
    
    def _calculate_agreement(self, signals: List[int]) -> float:
        """Calculate agreement percentage"""
        from collections import Counter
        counts = Counter(signals)
        max_count = max(counts.values())
        return max_count / len(signals)