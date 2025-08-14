#!/usr/bin/env python3
"""
HebbNet Model Persistence - Save and load trained biological brains
==================================================================
Save/load HebbNet models with full state preservation.
"""

import pickle
import json
import numpy as np
import os
import time
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

from ..core.hebbnet import HebbNet
from ..core.ensemble import HebbNetEnsemble
from ..core.config import TradingConfig, SpecialistConfig
from ..models.trading_hebbnet import TradingHebbNet, TradingEnsemble
from ..models.specialist_nets import (
    SpecialistHebbNet, PricePatternNet, 
    VolumeAnalysisNet, MomentumNet, SpecialistEnsemble
)


class ModelPersistence:
    """
    Handle saving and loading of HebbNet models
    
    Features:
    - Full model state preservation
    - Metadata tracking
    - Version compatibility
    - Compression support
    """
    
    def __init__(self, base_path: str = "models/hebbnet/"):
        """Initialize persistence manager"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.version = "1.0"
        self.compression_level = 9
    
    def save_model(self, model: Union[HebbNet, HebbNetEnsemble], 
                   filename: str, metadata: Optional[Dict] = None) -> str:
        """
        Save HebbNet model with full state
        
        Args:
            model: HebbNet or ensemble to save
            filename: Output filename (without extension)
            metadata: Additional metadata
            
        Returns:
            Full path to saved file
        """
        # Create filename with timestamp if not provided
        if not filename.endswith('.hebbnet'):
            timestamp = int(time.time())
            filename = f"{filename}_{timestamp}.hebbnet"
        
        filepath = self.base_path / filename
        
        # Prepare model data
        model_data = self._extract_model_data(model)
        
        # Add metadata
        model_data['metadata'] = {
            'saved_at': time.time(),
            'saved_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': type(model).__name__,
            'version': self.version,
            'numpy_version': np.__version__,
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            **(metadata or {})
        }
        
        # Save with pickle
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            print(f"✅ Model saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            raise
    
    def load_model(self, filepath: str, 
                   validate_integrity: bool = True) -> Union[HebbNet, HebbNetEnsemble]:
        """
        Load HebbNet model from file
        
        Args:
            filepath: Path to saved model
            validate_integrity: Check model integrity after loading
            
        Returns:
            Loaded HebbNet model
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            # Validate version compatibility
            self._validate_compatibility(model_data)
            
            # Reconstruct model
            model = self._reconstruct_model(model_data)
            
            # Validate integrity if requested
            if validate_integrity:
                self._validate_model_integrity(model, model_data)
            
            print(f"✅ Model loaded from {filepath}")
            print(f"📊 Model type: {model_data['metadata'].get('model_type', 'Unknown')}")
            print(f"💾 Saved: {model_data['metadata'].get('saved_date', 'Unknown')}")
            
            return model
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def save_ensemble(self, ensemble: HebbNetEnsemble, name: str,
                     include_training_data: bool = False) -> str:
        """
        Save ensemble with all individual models
        
        Args:
            ensemble: Ensemble to save
            name: Base name for files
            include_training_data: Include training statistics
            
        Returns:
            Path to ensemble file
        """
        # Save main ensemble file
        ensemble_metadata = {
            'ensemble_size': len(ensemble.models) if ensemble.models else 0,
            'ensemble_trained': ensemble.ensemble_trained,
            'training_time': getattr(ensemble, 'training_time', 0),
            'individual_accuracies': getattr(ensemble, 'model_accuracies', [])
        }
        
        if include_training_data:
            ensemble_metadata['individual_stats'] = getattr(ensemble, 'individual_stats', [])
        
        ensemble_path = self.save_model(ensemble, f"ensemble_{name}", ensemble_metadata)
        
        print(f"💼 Ensemble saved with {len(ensemble.models)} models")
        return ensemble_path
    
    def load_ensemble(self, filepath: str) -> HebbNetEnsemble:
        """Load ensemble model"""
        return self.load_model(filepath)
    
    def list_models(self, pattern: str = "*.hebbnet") -> List[Dict[str, Any]]:
        """
        List available saved models
        
        Args:
            pattern: Filename pattern to match
            
        Returns:
            List of model info dictionaries
        """
        model_files = list(self.base_path.glob(pattern))
        model_info = []
        
        for model_file in sorted(model_files, key=os.path.getmtime, reverse=True):
            try:
                with open(model_file, 'rb') as f:
                    data = pickle.load(f)
                
                metadata = data.get('metadata', {})
                
                info = {
                    'filename': model_file.name,
                    'path': str(model_file),
                    'size_mb': model_file.stat().st_size / (1024 * 1024),
                    'model_type': metadata.get('model_type', 'Unknown'),
                    'saved_date': metadata.get('saved_date', 'Unknown'),
                    'version': metadata.get('version', 'Unknown')
                }
                
                # Add model-specific info
                if 'config' in data:
                    config = data['config']
                    info.update({
                        'hidden_size': getattr(config, 'hidden_size', 'Unknown'),
                        'input_size': data.get('input_size', 'Unknown')
                    })
                
                model_info.append(info)
                
            except Exception as e:
                print(f"⚠️  Error reading {model_file.name}: {e}")
        
        return model_info
    
    def cleanup_old_models(self, keep_latest: int = 5, 
                          days_old: int = 30) -> int:
        """
        Clean up old model files
        
        Args:
            keep_latest: Number of latest models to keep per type
            days_old: Remove models older than this many days
            
        Returns:
            Number of files removed
        """
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        # Get all model files
        model_files = list(self.base_path.glob("*.hebbnet"))
        model_files.sort(key=os.path.getmtime, reverse=True)
        
        # Group by model type
        models_by_type = {}
        for model_file in model_files:
            try:
                with open(model_file, 'rb') as f:
                    data = pickle.load(f)
                model_type = data.get('metadata', {}).get('model_type', 'unknown')
                
                if model_type not in models_by_type:
                    models_by_type[model_type] = []
                
                models_by_type[model_type].append({
                    'file': model_file,
                    'mtime': model_file.stat().st_mtime
                })
            except:
                continue
        
        removed_count = 0
        
        for model_type, files in models_by_type.items():
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['mtime'], reverse=True)
            
            # Remove old files (keep latest N)
            for i, file_info in enumerate(files):
                should_remove = False
                
                # Remove if beyond keep_latest limit
                if i >= keep_latest:
                    should_remove = True
                
                # Remove if older than cutoff
                if file_info['mtime'] < cutoff_time:
                    should_remove = True
                
                if should_remove:
                    try:
                        file_info['file'].unlink()
                        removed_count += 1
                        print(f"🗑️  Removed old model: {file_info['file'].name}")
                    except Exception as e:
                        print(f"⚠️  Error removing {file_info['file'].name}: {e}")
        
        return removed_count
    
    def _extract_model_data(self, model: Union[HebbNet, HebbNetEnsemble]) -> Dict[str, Any]:
        """Extract model data for saving"""
        data = {
            'model_class': type(model).__name__,
            'input_size': model.input_size,
        }
        
        if isinstance(model, HebbNetEnsemble):
            # Ensemble model
            data.update({
                'config': model.config,
                'models': [],
                'model_accuracies': getattr(model, 'model_accuracies', []),
                'ensemble_trained': model.ensemble_trained,
                'training_time': getattr(model, 'training_time', 0),
                'individual_stats': getattr(model, 'individual_stats', [])
            })
            
            # Save individual models
            for individual_model in model.models:
                individual_data = self._extract_single_model_data(individual_model)
                data['models'].append(individual_data)
        
        else:
            # Single model
            data.update(self._extract_single_model_data(model))
        
        return data
    
    def _extract_single_model_data(self, model: HebbNet) -> Dict[str, Any]:
        """Extract data from single HebbNet"""
        return {
            'model_class': type(model).__name__,
            'input_size': model.input_size,
            'hidden_size': model.hidden_size,
            'config': model.config,
            
            # Network weights and state
            'W': model.W,
            'p': model.p,
            'bias': model.bias,
            'refractory': model.refractory,
            
            # Mappings and statistics
            'neuron_to_class': model.neuron_to_class,
            'training_steps': getattr(model, 'training_steps', 0),
            'last_winner': getattr(model, 'last_winner', -1),
            
            # Trading-specific attributes (if present)
            'market_regime': getattr(model, 'market_regime', None),
            'position_size': getattr(model, 'position_size', 0.0),
            'correct_predictions': getattr(model, 'correct_predictions', 0),
            'total_predictions': getattr(model, 'total_predictions', 0),
            'profitability': getattr(model, 'profitability', 0.0),
        }
    
    def _reconstruct_model(self, model_data: Dict[str, Any]) -> Union[HebbNet, HebbNetEnsemble]:
        """Reconstruct model from saved data"""
        model_class = model_data['model_class']
        
        if 'Ensemble' in model_class:
            return self._reconstruct_ensemble(model_data)
        else:
            return self._reconstruct_single_model(model_data)
    
    def _reconstruct_single_model(self, data: Dict[str, Any]) -> HebbNet:
        """Reconstruct single HebbNet model"""
        model_class = data['model_class']
        input_size = data['input_size']
        config = data['config']
        
        # Create appropriate model type
        if model_class == 'TradingHebbNet':
            model = TradingHebbNet(input_size, config)
        elif model_class == 'PricePatternNet':
            model = PricePatternNet(input_size, config)
        elif model_class == 'VolumeAnalysisNet':
            model = VolumeAnalysisNet(input_size, config)
        elif model_class == 'MomentumNet':
            model = MomentumNet(input_size, config)
        else:
            model = HebbNet(input_size, config)
        
        # Restore network state
        model.W = data['W']
        model.p = data['p'] 
        model.bias = data['bias']
        model.refractory = data['refractory']
        model.neuron_to_class = data['neuron_to_class']
        
        # Restore training statistics
        model.training_steps = data.get('training_steps', 0)
        model.last_winner = data.get('last_winner', -1)
        
        # Restore trading-specific attributes
        if hasattr(model, 'market_regime'):
            model.market_regime = data.get('market_regime', 'normal')
        if hasattr(model, 'position_size'):
            model.position_size = data.get('position_size', 0.0)
        if hasattr(model, 'correct_predictions'):
            model.correct_predictions = data.get('correct_predictions', 0)
            model.total_predictions = data.get('total_predictions', 0)
            model.profitability = data.get('profitability', 0.0)
        
        return model
    
    def _reconstruct_ensemble(self, data: Dict[str, Any]) -> HebbNetEnsemble:
        """Reconstruct ensemble model"""
        model_class = data['model_class']
        input_size = data['input_size']
        config = data['config']
        
        # Create appropriate ensemble type
        if model_class == 'TradingEnsemble':
            ensemble = TradingEnsemble(input_size, config)
        elif model_class == 'SpecialistEnsemble':
            ensemble = SpecialistEnsemble(input_size, config)
        else:
            ensemble = HebbNetEnsemble(input_size, config)
        
        # Reconstruct individual models
        ensemble.models = []
        for model_data in data['models']:
            individual_model = self._reconstruct_single_model(model_data)
            ensemble.models.append(individual_model)
        
        # Restore ensemble state
        ensemble.model_accuracies = data.get('model_accuracies', [])
        ensemble.ensemble_trained = data.get('ensemble_trained', False)
        ensemble.training_time = data.get('training_time', 0)
        ensemble.individual_stats = data.get('individual_stats', [])
        
        return ensemble
    
    def _validate_compatibility(self, model_data: Dict[str, Any]) -> None:
        """Validate model version compatibility"""
        saved_version = model_data.get('metadata', {}).get('version', '0.0')
        
        # Version compatibility checks
        if saved_version != self.version:
            print(f"⚠️  Version mismatch: saved={saved_version}, current={self.version}")
            print("   Model may still load but compatibility is not guaranteed")
    
    def _validate_model_integrity(self, model: Union[HebbNet, HebbNetEnsemble], 
                                 original_data: Dict[str, Any]) -> None:
        """Validate loaded model integrity"""
        # Basic checks
        assert model.input_size == original_data['input_size']
        
        if isinstance(model, HebbNetEnsemble):
            assert len(model.models) == len(original_data['models'])
        else:
            # Check critical arrays
            np.testing.assert_array_equal(model.W, original_data['W'])
            np.testing.assert_array_equal(model.p, original_data['p'])
            assert len(model.neuron_to_class) == len(original_data['neuron_to_class'])
        
        print("✅ Model integrity validated")


# Convenience functions
def save_model(model: Union[HebbNet, HebbNetEnsemble], 
               filename: str, base_path: str = "models/hebbnet/",
               metadata: Optional[Dict] = None) -> str:
    """
    Quick save function
    
    Args:
        model: Model to save
        filename: Output filename
        base_path: Directory for saved models
        metadata: Additional metadata
        
    Returns:
        Path to saved file
    """
    persistence = ModelPersistence(base_path)
    return persistence.save_model(model, filename, metadata)


def load_model(filepath: str) -> Union[HebbNet, HebbNetEnsemble]:
    """
    Quick load function
    
    Args:
        filepath: Path to model file
        
    Returns:
        Loaded model
    """
    # Infer base path from filepath
    file_path = Path(filepath)
    base_path = file_path.parent if file_path.is_absolute() else "models/hebbnet/"
    
    persistence = ModelPersistence(base_path)
    return persistence.load_model(filepath)


def list_saved_models(base_path: str = "models/hebbnet/") -> List[Dict[str, Any]]:
    """
    List all saved models
    
    Args:
        base_path: Directory to search
        
    Returns:
        List of model information
    """
    persistence = ModelPersistence(base_path)
    return persistence.list_models()