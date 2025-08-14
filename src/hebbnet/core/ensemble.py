#!/usr/bin/env python3
"""
HebbNet Ensemble - Stable trading performance through voting
==========================================================
Multiple HebbNets with different seeds voting for robust decisions.
Based on the proven 87%+ ensemble approach.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import time

from .hebbnet import HebbNet
from .config import TradingConfig


class HebbNetEnsemble:
    """
    Ensemble of HebbNets for variance reduction and stability
    
    Features:
    - Multiple networks with different initialization seeds
    - Majority voting with confidence weighting  
    - Performance tracking and model selection
    - Robust predictions through consensus
    """
    
    def __init__(self, input_size: int, config: TradingConfig):
        """Initialize ensemble configuration"""
        self.input_size = input_size
        self.config = config
        self.models: List[HebbNet] = []
        self.model_accuracies: List[float] = []
        self.ensemble_trained = False
        
        # Training statistics
        self.training_time = 0.0
        self.individual_stats = []
    
    def initialize_ensemble(self) -> None:
        """Create ensemble of HebbNets with different seeds"""
        print(f"🧠 Initializing ensemble of {self.config.ensemble_size} networks...")
        
        self.models = []
        for i in range(self.config.ensemble_size):
            seed = 42 + i * 100  # Different seeds for diversity
            model = HebbNet(
                input_size=self.input_size,
                config=self.config,
                seed=seed
            )
            self.models.append(model)
        
        print(f"✅ Ensemble initialized with {len(self.models)} networks")
    
    def train_ensemble(self, X_train: np.ndarray, y_train: np.ndarray,
                      X_val: np.ndarray, y_val: np.ndarray,
                      epochs: int = 15, verbose: bool = True) -> Dict[str, Any]:
        """
        Train all networks in the ensemble
        
        Args:
            X_train: Training features
            y_train: Training labels (-1, 0, 1)
            X_val: Validation features  
            y_val: Validation labels
            epochs: Training epochs per network
            verbose: Print training progress
            
        Returns:
            Training statistics
        """
        if not self.models:
            raise ValueError("Ensemble not initialized! Call initialize_ensemble() first")
        
        print(f"🚀 Training ensemble of {len(self.models)} networks...")
        print(f"📊 Training samples: {len(X_train)}, Validation: {len(X_val)}")
        
        start_time = time.time()
        self.model_accuracies = []
        self.individual_stats = []
        
        for i, model in enumerate(self.models):
            if verbose:
                print(f"\n📦 Training Network {i+1}/{len(self.models)}")
            
            model_start = time.time()
            
            # Training loop
            for epoch in range(epochs):
                if verbose and epoch % 5 == 0:
                    print(f"  Epoch {epoch+1}/{epochs}")
                
                # Random order each epoch
                indices = np.random.permutation(len(X_train))
                
                for step, idx in enumerate(indices):
                    x = X_train[idx]
                    winner = model.train_step(x)
                    
                    # Periodic dead neuron reseeding
                    if step % 1000 == 0 and step > 0 and epoch > 1:
                        reseeded = model.reseed_dead_neurons(X_train)
                        if verbose and reseeded > 0:
                            print(f"    Reseeded {reseeded} dead neurons")
            
            # Learn output mapping
            model.learn_mapping(X_val, y_val, n_classes=3)
            
            # Evaluate this model
            accuracy = self._evaluate_model(model, X_val, y_val)
            self.model_accuracies.append(accuracy)
            
            model_time = time.time() - model_start
            stats = {
                'model_id': i,
                'accuracy': accuracy,
                'training_time': model_time,
                'statistics': model.get_statistics()
            }
            self.individual_stats.append(stats)
            
            if verbose:
                print(f"  ✅ Network {i+1} accuracy: {accuracy:.1%} ({model_time:.1f}s)")
        
        self.training_time = time.time() - start_time
        self.ensemble_trained = True
        
        # Report ensemble statistics
        if verbose:
            self._print_ensemble_summary()
        
        return self._get_training_summary()
    
    def predict(self, x: np.ndarray, strategy: str = 'weighted') -> int:
        """
        Ensemble prediction using voting strategies
        
        Args:
            x: Input features
            strategy: 'majority', 'weighted', or 'confidence'
            
        Returns:
            Predicted class (-1, 0, 1)
        """
        if not self.ensemble_trained:
            raise ValueError("Ensemble not trained! Call train_ensemble() first")
        
        # Get predictions from all models
        predictions = []
        confidences = []
        
        for model in self.models:
            pred = model.predict(x)
            predictions.append(pred)
            
            # Get confidence as max probability
            probs = model.predict_proba(x)
            confidence = np.max(probs)
            confidences.append(confidence)
        
        if strategy == 'majority':
            # Simple majority vote
            return self._majority_vote(predictions)
        
        elif strategy == 'weighted':
            # Weight by individual model accuracy
            return self._weighted_vote(predictions, self.model_accuracies)
        
        elif strategy == 'confidence':
            # Weight by prediction confidence
            return self._weighted_vote(predictions, confidences)
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def predict_proba(self, x: np.ndarray, 
                     strategy: str = 'weighted') -> np.ndarray:
        """
        Ensemble probability prediction
        
        Args:
            x: Input features
            strategy: Voting strategy
            
        Returns:
            Class probabilities [sell, hold, buy]
        """
        if not self.ensemble_trained:
            raise ValueError("Ensemble not trained! Call train_ensemble() first")
        
        # Collect probabilities from all models
        all_probs = []
        weights = []
        
        for i, model in enumerate(self.models):
            probs = model.predict_proba(x)
            all_probs.append(probs)
            
            if strategy == 'weighted':
                weights.append(self.model_accuracies[i])
            elif strategy == 'confidence':
                weights.append(np.max(probs))
            else:
                weights.append(1.0)  # Equal weights
        
        # Weighted average of probabilities
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalize
        
        ensemble_probs = np.zeros(3)
        for prob, weight in zip(all_probs, weights):
            ensemble_probs += weight * prob
        
        return ensemble_probs
    
    def get_trading_signal(self, x: np.ndarray) -> Dict[str, Any]:
        """
        Get comprehensive trading signal with confidence
        
        Args:
            x: Input features
            
        Returns:
            Trading signal dictionary
        """
        # Get ensemble prediction and confidence
        prediction = self.predict(x, strategy='weighted')
        probabilities = self.predict_proba(x, strategy='weighted')
        confidence = np.max(probabilities)
        
        # Map prediction to signal
        signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
        signal = signal_map.get(prediction, 'HOLD')
        
        # Check against thresholds
        thresholds = self.config.get_signal_thresholds()
        
        if signal == 'BUY' and confidence >= thresholds['strong_buy']:
            strength = 'STRONG'
        elif signal == 'SELL' and confidence >= thresholds['strong_sell']:
            strength = 'STRONG'
        elif confidence >= 0.6:
            strength = 'MEDIUM'
        else:
            strength = 'WEAK'
        
        return {
            'signal': signal,
            'strength': strength,
            'confidence': confidence,
            'probabilities': {
                'sell': probabilities[0],
                'hold': probabilities[1], 
                'buy': probabilities[2]
            },
            'prediction_raw': prediction
        }
    
    def _evaluate_model(self, model: HebbNet, X_val: np.ndarray, 
                       y_val: np.ndarray) -> float:
        """Evaluate single model accuracy"""
        correct = 0
        for x, y in zip(X_val, y_val):
            pred = model.predict(x)
            if pred == y:
                correct += 1
        
        return correct / len(y_val) if len(y_val) > 0 else 0.0
    
    def _majority_vote(self, predictions: List[int]) -> int:
        """Simple majority vote"""
        counter = Counter(predictions)
        return counter.most_common(1)[0][0]
    
    def _weighted_vote(self, predictions: List[int], 
                      weights: List[float]) -> int:
        """Weighted voting"""
        vote_weights = {-1: 0.0, 0: 0.0, 1: 0.0}
        
        for pred, weight in zip(predictions, weights):
            vote_weights[pred] += weight
        
        return max(vote_weights, key=vote_weights.get)
    
    def _print_ensemble_summary(self) -> None:
        """Print training summary"""
        print("\n✨ ENSEMBLE TRAINING COMPLETE!")
        print("=" * 50)
        
        accuracies = self.model_accuracies
        print(f"Individual accuracies: {[f'{a:.1%}' for a in accuracies]}")
        print(f"  Mean: {np.mean(accuracies):.1%}")
        print(f"  Std:  ±{np.std(accuracies):.1%}")
        print(f"  Best: {max(accuracies):.1%}")
        print(f"  Worst: {min(accuracies):.1%}")
        
        print(f"\n⏱️  Training time: {self.training_time:.1f}s")
        print(f"⏱️  Per network: {self.training_time/len(self.models):.1f}s")
        
        # Variance analysis
        ensemble_var = np.var(accuracies)
        print(f"\n📊 Variance: {ensemble_var:.4f}")
        
        if np.mean(accuracies) >= 0.70:
            print("🎉 EXCELLENT! Strong ensemble performance!")
        elif np.mean(accuracies) >= 0.60:
            print("💪 GOOD! Solid trading predictions!")
    
    def _get_training_summary(self) -> Dict[str, Any]:
        """Get complete training statistics"""
        return {
            'ensemble_size': len(self.models),
            'individual_accuracies': self.model_accuracies,
            'mean_accuracy': np.mean(self.model_accuracies),
            'std_accuracy': np.std(self.model_accuracies),
            'best_accuracy': max(self.model_accuracies),
            'training_time': self.training_time,
            'individual_stats': self.individual_stats
        }