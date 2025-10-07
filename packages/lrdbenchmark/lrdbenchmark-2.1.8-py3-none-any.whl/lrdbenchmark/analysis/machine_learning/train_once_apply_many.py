#!/usr/bin/env python3
"""
Train-Once, Apply-Many Pipeline for Production ML Models.

This module implements a comprehensive pipeline for training models once and
deploying them for efficient inference in production environments.
"""

import numpy as np
import time
import logging
import json
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import warnings
from datetime import datetime

# Import our production system
from .production_ml_system import ProductionMLSystem, ProductionConfig, ProductionResult

# Import data models for training data generation
from lrdbenchmark.models.data_models.fbm.fbm_model import FractionalBrownianMotion
from lrdbenchmark.models.data_models.fgn.fgn_model import FractionalGaussianNoise
from lrdbenchmark.models.data_models.arfima.arfima_model import ARFIMAModel
from lrdbenchmark.models.data_models.mrw.mrw_model import MultifractalRandomWalk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingDataConfig:
    """Configuration for training data generation."""
    n_samples_per_model: int = 1000
    sequence_lengths: List[int] = None
    hurst_range: Tuple[float, float] = (0.1, 0.9)
    noise_levels: List[float] = None
    contamination_scenarios: List[str] = None
    
    def __post_init__(self):
        if self.sequence_lengths is None:
            self.sequence_lengths = [100, 250, 500, 1000]
        if self.noise_levels is None:
            self.noise_levels = [0.0, 0.01, 0.05, 0.1]
        if self.contamination_scenarios is None:
            self.contamination_scenarios = ['pure', 'gaussian_noise', 'outliers', 'trend']

@dataclass
class ModelTrainingConfig:
    """Configuration for model training."""
    model_types: List[str] = None
    input_length: int = 500
    hidden_dims: List[int] = None
    dropout_rate: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    
    # Framework preferences
    prefer_jax: bool = True
    prefer_torch: bool = True
    prefer_numba: bool = True
    
    def __post_init__(self):
        if self.model_types is None:
            self.model_types = ['cnn', 'transformer']
        if self.hidden_dims is None:
            self.hidden_dims = [64, 32]

@dataclass
class TrainingResult:
    """Results from training pipeline."""
    model_type: str
    framework: str
    training_time: float
    performance_metrics: Dict[str, float]
    model_path: str
    training_data_info: Dict[str, Any]
    model_config: Dict[str, Any]
    timestamp: str

class TrainingDataGenerator:
    """Generate comprehensive training data for ML models."""
    
    def __init__(self, config: TrainingDataConfig):
        self.config = config
        self.data_models = {
            'fbm': FractionalBrownianMotion,
            'fgn': FractionalGaussianNoise,
            'arfima': ARFIMAModel,
            'mrw': MultifractalRandomWalk
        }
    
    def generate_training_data(self) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Generate comprehensive training dataset."""
        logger.info("Generating training data...")
        
        X_list = []
        y_list = []
        metadata = {
            'n_samples': 0,
            'data_models': [],
            'hurst_values': [],
            'sequence_lengths': [],
            'noise_levels': [],
            'contamination_scenarios': []
        }
        
        # Generate data for each model type
        for model_name, model_class in self.data_models.items():
            logger.info(f"Generating data for {model_name}")
            
            for seq_len in self.config.sequence_lengths:
                for hurst in np.linspace(self.config.hurst_range[0], self.config.hurst_range[1], 10):
                    for noise_level in self.config.noise_levels:
                        for scenario in self.config.contamination_scenarios:
                            
                            # Generate base data
                            if model_name == 'arfima':
                                # ARFIMA uses d parameter
                                d = hurst - 0.5
                                model = model_class(d=d)
                            elif model_name == 'mrw':
                                # MRW needs H and lambda parameter
                                model = model_class(H=hurst, lambda_param=0.5)
                            else:
                                # FBM and FGN use H parameter
                                model = model_class(H=hurst)
                            
                            # Generate data
                            data = model.generate(n=seq_len)
                            
                            # Apply contamination
                            if scenario != 'pure':
                                data = self._apply_contamination(data, scenario, noise_level)
                            
                            # Ensure correct length and shape
                            data = np.asarray(data).flatten()
                            if len(data) != seq_len:
                                if len(data) > seq_len:
                                    data = data[:seq_len]
                                else:
                                    # Pad with zeros
                                    padded = np.zeros(seq_len)
                                    padded[:len(data)] = data
                                    data = padded
                            
                            X_list.append(data)
                            y_list.append(hurst)
                            
                            # Update metadata
                            metadata['n_samples'] += 1
                            metadata['data_models'].append(model_name)
                            metadata['hurst_values'].append(hurst)
                            metadata['sequence_lengths'].append(seq_len)
                            metadata['noise_levels'].append(noise_level)
                            metadata['contamination_scenarios'].append(scenario)
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        logger.info(f"Generated {len(X)} training samples")
        
        return X, y, metadata
    
    def _apply_contamination(self, data: np.ndarray, scenario: str, noise_level: float) -> np.ndarray:
        """Apply contamination to data."""
        if scenario == 'gaussian_noise':
            noise = np.random.normal(0, noise_level, len(data))
            return data + noise
        
        elif scenario == 'outliers':
            # Add random outliers
            n_outliers = max(1, int(len(data) * 0.05))
            outlier_indices = np.random.choice(len(data), n_outliers, replace=False)
            contaminated_data = data.copy()
            for idx in outlier_indices:
                contaminated_data[idx] += np.random.normal(0, 3 * noise_level)
            return contaminated_data
        
        elif scenario == 'trend':
            # Add linear trend
            trend = np.linspace(0, noise_level, len(data))
            return data + trend
        
        else:
            return data

class ModelTrainer:
    """Train multiple models with different frameworks."""
    
    def __init__(self, config: ModelTrainingConfig):
        self.config = config
        self.trained_models = {}
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> List[TrainingResult]:
        """Train all configured models."""
        logger.info("Starting model training...")
        
        results = []
        
        for model_type in self.config.model_types:
            logger.info(f"Training {model_type} model")
            
            # Try different frameworks in order of preference
            frameworks_to_try = []
            if self.config.prefer_jax:
                frameworks_to_try.append('jax')
            if self.config.prefer_torch:
                frameworks_to_try.append('torch')
            if self.config.prefer_numba:
                frameworks_to_try.append('numba')
            
            for framework in frameworks_to_try:
                try:
                    result = self._train_single_model(model_type, framework, X, y)
                    if result:
                        results.append(result)
                        self.trained_models[f"{model_type}_{framework}"] = result
                        logger.info(f"Successfully trained {model_type} with {framework}")
                        break  # Use first successful framework
                    else:
                        logger.warning(f"Failed to train {model_type} with {framework}")
                except Exception as e:
                    logger.error(f"Error training {model_type} with {framework}: {e}")
                    continue
        
        logger.info(f"Training completed. {len(results)} models trained successfully")
        return results
    
    def _train_single_model(self, model_type: str, framework: str, X: np.ndarray, y: np.ndarray) -> Optional[TrainingResult]:
        """Train a single model with specified framework."""
        try:
            # Create production config
            config = ProductionConfig(
                model_type=model_type,
                input_length=self.config.input_length,
                hidden_dims=self.config.hidden_dims,
                dropout_rate=self.config.dropout_rate,
                learning_rate=self.config.learning_rate,
                batch_size=self.config.batch_size,
                epochs=self.config.epochs,
                early_stopping_patience=self.config.early_stopping_patience,
                validation_split=self.config.validation_split,
                use_jax=framework == 'jax',
                use_torch=framework == 'torch',
                use_numba=framework == 'numba',
                framework_priority=[framework],
                model_path=f"models/{model_type}_{framework}_{int(time.time())}"
            )
            
            # Create and train model
            model = ProductionMLSystem(config)
            training_result = model.train(X, y)
            
            # Create result
            result = TrainingResult(
                model_type=model_type,
                framework=framework,
                training_time=training_result['training_time'],
                performance_metrics=training_result['performance_metrics'],
                model_path=config.model_path,
                training_data_info={
                    'n_samples': len(X),
                    'input_length': self.config.input_length,
                    'hurst_range': (np.min(y), np.max(y))
                },
                model_config=asdict(config),
                timestamp=datetime.now().isoformat()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to train {model_type} with {framework}: {e}")
            return None

class ModelRegistry:
    """Registry for managing trained models."""
    
    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load model registry from file."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {'models': {}, 'metadata': {'created': datetime.now().isoformat()}}
    
    def _save_registry(self):
        """Save model registry to file."""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self, result: TrainingResult):
        """Register a trained model."""
        model_id = f"{result.model_type}_{result.framework}_{int(time.time())}"
        
        self.registry['models'][model_id] = {
            'model_type': result.model_type,
            'framework': result.framework,
            'model_path': result.model_path,
            'performance_metrics': result.performance_metrics,
            'training_time': result.training_time,
            'timestamp': result.timestamp,
            'training_data_info': result.training_data_info,
            'model_config': result.model_config
        }
        
        self._save_registry()
        logger.info(f"Registered model: {model_id}")
    
    def get_best_model(self, model_type: str = None, framework: str = None) -> Optional[Dict[str, Any]]:
        """Get the best model based on performance metrics."""
        best_model = None
        best_score = float('inf')
        
        for model_id, model_info in self.registry['models'].items():
            # Filter by type and framework if specified
            if model_type and model_info['model_type'] != model_type:
                continue
            if framework and model_info['framework'] != framework:
                continue
            
            # Use MSE as the primary metric
            score = model_info['performance_metrics'].get('mse', float('inf'))
            if score < best_score:
                best_score = score
                best_model = model_info
        
        return best_model
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        return list(self.registry['models'].values())
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        return self.registry['models'].get(model_id)

class ProductionDeployment:
    """Deploy trained models for production use."""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.deployed_models = {}
    
    def deploy_model(self, model_id: str = None, model_type: str = None, framework: str = None) -> Optional[ProductionMLSystem]:
        """Deploy a model for production use."""
        # Get model info
        if model_id:
            model_info = self.registry.get_model_info(model_id)
        else:
            model_info = self.registry.get_best_model(model_type, framework)
        
        if not model_info:
            logger.error("No suitable model found for deployment")
            return None
        
        # Create production system
        config = ProductionConfig(**model_info['model_config'])
        model = ProductionMLSystem(config)
        
        # Load trained model
        if model.load_model(model_info['model_path']):
            self.deployed_models[model_info['model_type']] = model
            logger.info(f"Deployed model: {model_info['model_type']} ({model_info['framework']})")
            return model
        else:
            logger.error(f"Failed to load model: {model_info['model_path']}")
            return None
    
    def predict(self, data: np.ndarray, model_type: str = None) -> Optional[ProductionResult]:
        """Make prediction using deployed model."""
        if model_type and model_type in self.deployed_models:
            return self.deployed_models[model_type].predict(data)
        elif len(self.deployed_models) == 1:
            # Use the only deployed model
            model = list(self.deployed_models.values())[0]
            return model.predict(data)
        else:
            logger.error("No model deployed or multiple models available")
            return None
    
    def batch_predict(self, data_list: List[np.ndarray], model_type: str = None) -> List[ProductionResult]:
        """Make batch predictions."""
        if model_type and model_type in self.deployed_models:
            return self.deployed_models[model_type].batch_predict(data_list)
        elif len(self.deployed_models) == 1:
            model = list(self.deployed_models.values())[0]
            return model.batch_predict(data_list)
        else:
            logger.error("No model deployed or multiple models available")
            return []

class TrainOnceApplyManyPipeline:
    """Main pipeline for train-once, apply-many workflow."""
    
    def __init__(self, 
                 training_data_config: TrainingDataConfig = None,
                 model_training_config: ModelTrainingConfig = None,
                 registry_path: str = "models/registry.json"):
        
        self.training_data_config = training_data_config or TrainingDataConfig()
        self.model_training_config = model_training_config or ModelTrainingConfig()
        self.registry = ModelRegistry(registry_path)
        self.deployment = ProductionDeployment(self.registry)
        
        self.data_generator = TrainingDataGenerator(self.training_data_config)
        self.model_trainer = ModelTrainer(self.model_training_config)
    
    def run_training_pipeline(self) -> List[TrainingResult]:
        """Run the complete training pipeline."""
        logger.info("Starting train-once, apply-many pipeline")
        
        # Step 1: Generate training data
        logger.info("Step 1: Generating training data")
        X, y, metadata = self.data_generator.generate_training_data()
        
        # Step 2: Train models
        logger.info("Step 2: Training models")
        training_results = self.model_trainer.train_models(X, y)
        
        # Step 3: Register models
        logger.info("Step 3: Registering models")
        for result in training_results:
            self.registry.register_model(result)
        
        logger.info(f"Training pipeline completed. {len(training_results)} models trained and registered")
        return training_results
    
    def deploy_best_model(self, model_type: str = None, framework: str = None) -> Optional[ProductionMLSystem]:
        """Deploy the best model for production use."""
        return self.deployment.deploy_model(model_type=model_type, framework=framework)
    
    def predict(self, data: np.ndarray, model_type: str = None) -> Optional[ProductionResult]:
        """Make prediction using deployed model."""
        return self.deployment.predict(data, model_type)
    
    def batch_predict(self, data_list: List[np.ndarray], model_type: str = None) -> List[ProductionResult]:
        """Make batch predictions."""
        return self.deployment.batch_predict(data_list, model_type)
    
    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all trained models."""
        models = self.registry.list_models()
        
        summary = {
            'total_models': len(models),
            'model_types': {},
            'frameworks': {},
            'best_performers': {}
        }
        
        for model in models:
            model_type = model['model_type']
            framework = model['framework']
            mse = model['performance_metrics'].get('mse', float('inf'))
            
            # Count by type and framework
            summary['model_types'][model_type] = summary['model_types'].get(model_type, 0) + 1
            summary['frameworks'][framework] = summary['frameworks'].get(framework, 0) + 1
            
            # Track best performers
            if model_type not in summary['best_performers'] or mse < summary['best_performers'][model_type]['mse']:
                summary['best_performers'][model_type] = {
                    'framework': framework,
                    'mse': mse,
                    'model_path': model['model_path']
                }
        
        return summary

# Export main classes
__all__ = [
    'TrainOnceApplyManyPipeline',
    'TrainingDataConfig',
    'ModelTrainingConfig',
    'TrainingResult',
    'TrainingDataGenerator',
    'ModelTrainer',
    'ModelRegistry',
    'ProductionDeployment'
]
