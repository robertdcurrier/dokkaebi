#!/usr/bin/env python3
"""
TradingHebbNet - Financial market adaptation of core HebbNet
==========================================================
Specialized HebbNet for trading signals with market-specific features.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import time

from ..core.hebbnet import HebbNet
from ..core.ensemble import HebbNetEnsemble
from ..core.config import TradingConfig


class TradingHebbNet(HebbNet):
    """
    Trading-specialized HebbNet with financial market adaptations
    
    Features:
    - Market regime detection
    - Volatility-adjusted learning
    - Risk-aware predictions
    - Real-time signal generation
    """
    
    def __init__(self, input_size: int, config: TradingConfig, 
                 seed: Optional[int] = None):
        """Initialize trading-specific HebbNet"""
        super().__init__(input_size, config, seed)
        
        # Trading-specific attributes
        self.market_regime = 'normal'  # normal, volatile, trending
        self.volatility_window = []
        self.price_history = []
        self.signal_history = []
        
        # Performance tracking
        self.correct_predictions = 0
        self.total_predictions = 0
        self.profitability = 0.0
        
        # Risk management
        self.position_size = 0.0
        self.last_signal_time = 0
        self.signal_cooldown = 60  # seconds between signals
    
    def detect_market_regime(self, price_data: np.ndarray) -> str:
        """
        Detect current market regime for adaptive learning
        
        Args:
            price_data: Recent price history
            
        Returns:
            Market regime: 'normal', 'volatile', 'trending'
        """
        if len(price_data) < 20:
            return 'normal'
        
        # Calculate volatility (rolling std)
        returns = np.diff(price_data) / price_data[:-1]
        volatility = np.std(returns[-20:])
        
        # Calculate trend strength
        trend = np.polyfit(range(len(price_data[-20:])), price_data[-20:], 1)[0]
        trend_strength = abs(trend) / np.mean(price_data[-20:])
        
        # Classify regime
        if volatility > 0.02:  # 2% volatility threshold
            self.market_regime = 'volatile'
        elif trend_strength > 0.001:  # 0.1% trend threshold
            self.market_regime = 'trending'
        else:
            self.market_regime = 'normal'
        
        return self.market_regime
    
    def adaptive_learning_rate(self, base_volatility: float) -> float:
        """
        Adjust learning rate based on market conditions
        
        Args:
            base_volatility: Current market volatility
            
        Returns:
            Adjusted learning rate
        """
        if self.market_regime == 'volatile':
            # Slower learning in volatile markets
            return self.config.eta_base * 0.5
        elif self.market_regime == 'trending':
            # Faster learning in trending markets
            return self.config.eta_base * 1.5
        else:
            return self.config.eta_base
    
    def train_step_adaptive(self, x: np.ndarray, 
                           volatility: float = None) -> int:
        """
        Training step with market-adaptive learning
        
        Args:
            x: Input features
            volatility: Current market volatility
            
        Returns:
            Winner neuron index
        """
        # Temporarily adjust learning rate if volatility provided
        original_eta = self.config.eta_base
        if volatility is not None:
            self.config.eta_base = self.adaptive_learning_rate(volatility)
        
        # Standard training step
        winner = self.train_step(x)
        
        # Restore original learning rate
        if volatility is not None:
            self.config.eta_base = original_eta
        
        return winner
    
    def predict_with_confidence(self, x: np.ndarray) -> Tuple[int, float, Dict]:
        """
        Prediction with confidence and market context
        
        Args:
            x: Input features
            
        Returns:
            (prediction, confidence, context_info)
        """
        # Get prediction probabilities
        probs = self.predict_proba(x)
        prediction = self.predict(x)
        confidence = np.max(probs)
        
        # Market context
        context = {
            'regime': self.market_regime,
            'probabilities': {
                'sell': probs[0],
                'hold': probs[1], 
                'buy': probs[2]
            },
            'confidence': confidence,
            'prediction': prediction
        }
        
        return prediction, confidence, context
    
    def generate_trading_signal(self, features: np.ndarray, 
                               current_price: float,
                               current_time: float = None) -> Dict[str, Any]:
        """
        Generate comprehensive trading signal
        
        Args:
            features: Market features
            current_price: Current asset price
            current_time: Unix timestamp
            
        Returns:
            Complete trading signal with risk management
        """
        if current_time is None:
            current_time = time.time()
        
        # Check signal cooldown
        if (current_time - self.last_signal_time) < self.signal_cooldown:
            return self._create_hold_signal("Cooldown period")
        
        # Get prediction with confidence
        prediction, confidence, context = self.predict_with_confidence(features)
        
        # Apply confidence thresholds
        thresholds = self.config.get_signal_thresholds()
        
        signal_strength = 'WEAK'
        if prediction == 1 and confidence >= thresholds['strong_buy']:
            signal = 'BUY'
            signal_strength = 'STRONG'
        elif prediction == 1 and confidence >= thresholds['buy']:
            signal = 'BUY'
            signal_strength = 'MEDIUM'
        elif prediction == -1 and confidence >= abs(thresholds['strong_sell']):
            signal = 'SELL'
            signal_strength = 'STRONG'
        elif prediction == -1 and confidence >= abs(thresholds['sell']):
            signal = 'SELL' 
            signal_strength = 'MEDIUM'
        else:
            signal = 'HOLD'
        
        # Risk management adjustments
        signal = self._apply_risk_management(signal, current_price, confidence)
        
        # Create signal object
        trading_signal = {
            'signal': signal,
            'strength': signal_strength,
            'confidence': confidence,
            'price': current_price,
            'timestamp': current_time,
            'market_regime': self.market_regime,
            'probabilities': context['probabilities'],
            'position_size': self._calculate_position_size(signal, confidence),
            'stop_loss': self._calculate_stop_loss(signal, current_price),
            'take_profit': self._calculate_take_profit(signal, current_price),
            'metadata': {
                'neuron_prediction': prediction,
                'raw_features_hash': hash(features.tobytes()),
                'model_stats': self.get_statistics()
            }
        }
        
        # Update history
        self.signal_history.append(trading_signal)
        self.last_signal_time = current_time
        
        return trading_signal
    
    def update_performance(self, predicted_signal: str, actual_return: float,
                          trade_executed: bool = True) -> None:
        """
        Update model performance tracking
        
        Args:
            predicted_signal: Signal that was generated
            actual_return: Realized return from the trade
            trade_executed: Whether trade was actually executed
        """
        if not trade_executed:
            return
        
        self.total_predictions += 1
        
        # Check if prediction was correct
        if ((predicted_signal == 'BUY' and actual_return > 0) or
            (predicted_signal == 'SELL' and actual_return < 0) or
            (predicted_signal == 'HOLD' and abs(actual_return) < 0.005)):
            self.correct_predictions += 1
        
        # Update profitability
        if predicted_signal != 'HOLD':
            trade_return = actual_return if predicted_signal == 'BUY' else -actual_return
            self.profitability += trade_return
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get trading performance metrics"""
        accuracy = (self.correct_predictions / max(self.total_predictions, 1))
        
        return {
            'accuracy': accuracy,
            'total_signals': self.total_predictions,
            'correct_predictions': self.correct_predictions,
            'profitability': self.profitability,
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'market_regime': self.market_regime,
            'signal_frequency': len(self.signal_history),
            'model_statistics': self.get_statistics()
        }
    
    def _create_hold_signal(self, reason: str) -> Dict[str, Any]:
        """Create a HOLD signal with reason"""
        return {
            'signal': 'HOLD',
            'strength': 'SYSTEM',
            'confidence': 0.5,
            'price': 0.0,
            'timestamp': time.time(),
            'reason': reason,
            'market_regime': self.market_regime,
            'probabilities': {'sell': 0.33, 'hold': 0.34, 'buy': 0.33},
            'position_size': 0.0,
            'stop_loss': None,
            'take_profit': None
        }
    
    def _apply_risk_management(self, signal: str, price: float, 
                             confidence: float) -> str:
        """Apply risk management rules"""
        # Don't trade if confidence too low
        if confidence < 0.6 and signal != 'HOLD':
            return 'HOLD'
        
        # Position size limits
        if abs(self.position_size) >= self.config.max_position_size:
            if ((signal == 'BUY' and self.position_size > 0) or
                (signal == 'SELL' and self.position_size < 0)):
                return 'HOLD'  # Already at max position
        
        return signal
    
    def _calculate_position_size(self, signal: str, confidence: float) -> float:
        """Calculate position size based on confidence"""
        if signal == 'HOLD':
            return 0.0
        
        # Base size on confidence
        base_size = min(confidence * self.config.max_position_size, 0.5)
        
        # Adjust for market regime
        if self.market_regime == 'volatile':
            base_size *= 0.5  # Smaller positions in volatile markets
        elif self.market_regime == 'trending':
            base_size *= 1.2  # Larger positions in trending markets
        
        return base_size if signal == 'BUY' else -base_size
    
    def _calculate_stop_loss(self, signal: str, price: float) -> Optional[float]:
        """Calculate stop loss level"""
        if signal == 'HOLD':
            return None
        
        stop_pct = self.config.stop_loss
        
        if signal == 'BUY':
            return price * (1 - stop_pct)
        else:  # SELL
            return price * (1 + stop_pct)
    
    def _calculate_take_profit(self, signal: str, price: float) -> Optional[float]:
        """Calculate take profit level"""
        if signal == 'HOLD':
            return None
        
        profit_pct = self.config.take_profit
        
        if signal == 'BUY':
            return price * (1 + profit_pct)
        else:  # SELL
            return price * (1 - profit_pct)
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio from signal history"""
        if len(self.signal_history) < 10:
            return 0.0
        
        # Simple approximation - would need actual returns in practice
        returns = [self.profitability / max(len(self.signal_history), 1)]
        if len(returns) < 2:
            return 0.0
        
        return np.mean(returns) / (np.std(returns) + 1e-8)


class TradingEnsemble(HebbNetEnsemble):
    """Trading-specific ensemble with market adaptations"""
    
    def __init__(self, input_size: int, config: TradingConfig):
        """Initialize trading ensemble"""
        super().__init__(input_size, config)
        self.market_regime = 'normal'
        self.ensemble_performance = []
    
    def initialize_ensemble(self) -> None:
        """Create ensemble of TradingHebbNets"""
        print(f"🧠 Initializing trading ensemble of {self.config.ensemble_size} networks...")
        
        self.models = []
        for i in range(self.config.ensemble_size):
            seed = 42 + i * 100
            model = TradingHebbNet(
                input_size=self.input_size,
                config=self.config,
                seed=seed
            )
            self.models.append(model)
        
        print(f"✅ Trading ensemble initialized with {len(self.models)} networks")
    
    def generate_ensemble_signal(self, features: np.ndarray,
                                current_price: float) -> Dict[str, Any]:
        """Generate ensemble trading signal with consensus"""
        if not self.ensemble_trained:
            raise ValueError("Ensemble not trained!")
        
        # Get signals from all models
        individual_signals = []
        for model in self.models:
            signal = model.generate_trading_signal(features, current_price)
            individual_signals.append(signal)
        
        # Consensus voting
        signals = [s['signal'] for s in individual_signals]
        confidences = [s['confidence'] for s in individual_signals]
        
        # Weighted consensus
        weighted_signal = self._weighted_vote(
            [self._signal_to_int(s) for s in signals],
            confidences
        )
        
        consensus_signal = self._int_to_signal(weighted_signal)
        consensus_confidence = np.mean(confidences)
        
        # Create ensemble signal
        ensemble_signal = {
            'signal': consensus_signal,
            'strength': 'STRONG' if consensus_confidence > 0.7 else 'MEDIUM',
            'confidence': consensus_confidence,
            'price': current_price,
            'timestamp': time.time(),
            'ensemble_agreement': self._calculate_agreement(signals),
            'individual_signals': individual_signals,
            'model_count': len(self.models)
        }
        
        return ensemble_signal
    
    def _signal_to_int(self, signal: str) -> int:
        """Convert signal to integer for voting"""
        return {'SELL': -1, 'HOLD': 0, 'BUY': 1}.get(signal, 0)
    
    def _int_to_signal(self, value: int) -> str:
        """Convert integer back to signal"""
        return {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}.get(value, 'HOLD')
    
    def _calculate_agreement(self, signals: List[str]) -> float:
        """Calculate ensemble agreement percentage"""
        from collections import Counter
        counts = Counter(signals)
        max_count = max(counts.values())
        return max_count / len(signals)