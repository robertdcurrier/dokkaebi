#!/usr/bin/env python3
"""
HebbNet Core - Biologically-inspired competitive learning
========================================================
Pure Hebbian learning with spherical k-means, NO backpropagation!
Adapted from the PROVEN 85.6% accurate HebbNet implementation.
"""

import numpy as np
from typing import Optional, Dict, List, Any
from .config import TradingConfig


class HebbNet:
    """
    Core HebbNet implementation - BIOLOGICAL LEARNING ONLY!
    
    Features:
    - Spherical k-means with cosine similarity
    - Winner-take-all competition with conscience mechanism
    - Refractory periods to prevent over-activation
    - Top-k updates with weighted responsibilities
    - Dead neuron resurrection via intelligent reseeding
    """
    
    def __init__(self, input_size: int, config: TradingConfig, 
                 seed: Optional[int] = None):
        """Initialize HebbNet with trading configuration"""
        if seed is not None:
            np.random.seed(seed)
        
        self.input_size = input_size
        self.hidden_size = config.hidden_size
        self.config = config
        
        # Initialize weights on unit sphere (CRITICAL for cosine similarity)
        self.W = np.random.randn(input_size, config.hidden_size)
        self.W = self.W.astype(np.float32)
        self._normalize_weights()
        
        # Competition tracking
        self.p = np.ones(config.hidden_size, dtype=np.float32)
        self.p = self.p / config.hidden_size  # Equal initial probability
        self.bias = np.zeros(config.hidden_size, dtype=np.float32)
        self.refractory = np.zeros(config.hidden_size, dtype=np.float32)
        
        # Mapping from neurons to output classes/signals
        self.neuron_to_class = {}
        
        # Training statistics
        self.training_steps = 0
        self.last_winner = -1
    
    def _normalize_weights(self):
        """Normalize all weight vectors to unit sphere"""
        for i in range(self.hidden_size):
            norm = np.linalg.norm(self.W[:, i])
            if norm > 1e-8:
                self.W[:, i] /= norm
    
    def compete(self, x: np.ndarray, training: bool = False) -> np.ndarray:
        """
        Winner-take-all competition using cosine similarity
        
        Args:
            x: Input vector
            training: Apply bias and refractory if training
            
        Returns:
            Competition scores for all neurons
        """
        # Normalize input for cosine similarity
        x_norm = x / (np.linalg.norm(x) + 1e-8)
        
        # Compute cosine similarities
        scores = np.dot(x_norm, self.W)
        
        # Apply competitive mechanisms during training
        if training:
            scores += self.bias - self.refractory
        
        return scores
    
    def train_step(self, x: np.ndarray) -> int:
        """
        Single training step with spherical k-means
        
        Args:
            x: Training sample
            
        Returns:
            Index of winning neuron
        """
        # Normalize input
        x_norm = x / (np.linalg.norm(x) + 1e-8)
        
        # Competition phase
        scores = self.compete(x, training=True)
        topk_indices = np.argsort(scores)[-self.config.k:][::-1]
        winner = topk_indices[0]
        
        # Update win rate statistics
        one_hot = np.zeros(self.hidden_size, dtype=np.float32)
        one_hot[winner] = 1.0
        self.p = (1 - self.config.alpha) * self.p
        self.p += self.config.alpha * one_hot
        
        # Update conscience bias (prevents monopolization)
        target_prob = 1.0 / self.hidden_size
        self.bias += self.config.beta * (target_prob - self.p)
        
        # Update refractory periods
        self.refractory *= 0.98  # Decay
        self.refractory[winner] = self.config.gamma
        
        # Top-k weight updates with responsibilities
        for rank, neuron_idx in enumerate(topk_indices):
            if rank < len(self.config.responsibilities):
                # Adaptive learning rate based on win frequency
                eta = self.config.eta_base * min(5.0, 
                    target_prob / (self.p[neuron_idx] + 1e-3))
                eta *= self.config.responsibilities[rank]
                
                # Spherical k-means update
                old_weight = self.W[:, neuron_idx]
                new_weight = (1 - eta) * old_weight + eta * x_norm
                
                # Re-normalize to unit sphere
                norm = np.linalg.norm(new_weight)
                if norm > 1e-8:
                    self.W[:, neuron_idx] = new_weight / norm
        
        self.training_steps += 1
        self.last_winner = winner
        return winner
    
    def reseed_dead_neurons(self, X_train: np.ndarray, 
                           threshold: float = 0.0005) -> int:
        """
        Resurrect dead neurons using intelligent reseeding
        
        Args:
            X_train: Training data for reseeding
            threshold: Probability threshold for "dead" neurons
            
        Returns:
            Number of neurons reseeded
        """
        dead_neurons = np.where(self.p < threshold)[0]
        
        if len(dead_neurons) == 0:
            return 0
        
        # Sample candidates from training data
        n_candidates = min(500, len(X_train))
        indices = np.random.choice(len(X_train), size=n_candidates, 
                                 replace=False)
        candidates = X_train[indices]
        
        # Normalize candidates
        candidates_norm = candidates / (np.linalg.norm(candidates, 
                                                     axis=1, keepdims=True) + 1e-8)
        
        # Find candidates most dissimilar from existing neurons
        similarities = candidates_norm @ self.W
        max_similarities = similarities.max(axis=1)
        dissimilarity_order = np.argsort(max_similarities)
        
        # Reseed up to 10 dead neurons
        reseeded = 0
        for i, neuron_idx in enumerate(dead_neurons[:10]):
            if i < len(dissimilarity_order):
                # Use most dissimilar candidate
                self.W[:, neuron_idx] = candidates_norm[dissimilarity_order[i]]
                
                # Reset neuron statistics
                self.p[neuron_idx] = 1.0 / self.hidden_size
                self.bias[neuron_idx] = 0.0
                self.refractory[neuron_idx] = 0.0
                
                reseeded += 1
        
        return reseeded
    
    def learn_mapping(self, X_val: np.ndarray, y_val: np.ndarray, 
                     n_classes: int = 3) -> np.ndarray:
        """
        Learn neuron-to-class mapping using validation data
        
        Args:
            X_val: Validation inputs
            y_val: Validation labels (e.g., -1, 0, 1 for sell/hold/buy)
            n_classes: Number of output classes
            
        Returns:
            Vote counts matrix [neurons x classes]
        """
        # Count votes for each neuron-class combination
        vote_counts = np.zeros((self.hidden_size, n_classes), dtype=np.int32)
        
        for x, y in zip(X_val, y_val):
            scores = self.compete(x, training=False)
            winner = np.argmax(scores)
            
            # Convert y to class index (assumes -1, 0, 1 -> 0, 1, 2)
            class_idx = int(y + 1) if y >= -1 else 1  # Default to hold
            class_idx = min(max(class_idx, 0), n_classes - 1)
            
            vote_counts[winner, class_idx] += 1
        
        # Assign each neuron to its most frequent class
        self.neuron_to_class = {}
        for neuron in range(self.hidden_size):
            neuron_votes = vote_counts[neuron, :]
            if neuron_votes.sum() > 0:
                best_class = np.argmax(neuron_votes)
                # Convert back to -1, 0, 1 format
                self.neuron_to_class[neuron] = best_class - 1
        
        return vote_counts
    
    def predict(self, x: np.ndarray) -> int:
        """
        Predict class for single input
        
        Args:
            x: Input vector
            
        Returns:
            Predicted class (-1, 0, 1)
        """
        scores = self.compete(x, training=False)
        winner = np.argmax(scores)
        
        if winner in self.neuron_to_class:
            return self.neuron_to_class[winner]
        
        return 0  # Default to hold
    
    def predict_proba(self, x: np.ndarray, n_classes: int = 3) -> np.ndarray:
        """
        Get prediction probabilities using top-k voting
        
        Args:
            x: Input vector
            n_classes: Number of classes
            
        Returns:
            Class probabilities
        """
        scores = self.compete(x, training=False)
        top5_indices = np.argsort(scores)[-5:][::-1]
        
        votes = np.zeros(n_classes)
        weights = [0.4, 0.25, 0.15, 0.1, 0.1]  # Weighted voting
        
        for i, neuron in enumerate(top5_indices):
            if neuron in self.neuron_to_class:
                class_idx = self.neuron_to_class[neuron] + 1  # Convert to 0,1,2
                class_idx = min(max(class_idx, 0), n_classes - 1)
                votes[class_idx] += weights[i]
        
        # Normalize to probabilities
        if votes.sum() > 0:
            return votes / votes.sum()
        else:
            return np.ones(n_classes) / n_classes
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get training and competition statistics"""
        return {
            'training_steps': self.training_steps,
            'win_rates': self.p.copy(),
            'dead_neurons': np.sum(self.p < 0.001),
            'active_neurons': np.sum(self.p > 0.01),
            'conscience_bias_range': (self.bias.min(), self.bias.max()),
            'last_winner': self.last_winner,
            'neuron_assignments': len(self.neuron_to_class)
        }