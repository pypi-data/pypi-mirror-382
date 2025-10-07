#!/usr/bin/env python3
"""
Enhanced Machine Learning Estimators using the ML Model Factory.

This module provides production-ready ML estimators with advanced features.
"""

import numpy as np
import torch
import warnings
from typing import Dict, Any, Optional, Union, List
import time
import logging
from pathlib import Path

from .ml_model_factory import (
    MLModelFactory, ModelConfig, TrainingResult, 
    CNNModel, TransformerModel, TimeSeriesFeatureExtractor
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMLEstimator:
    """Base class for enhanced ML estimators."""
    
    def __init__(self, model_type: str, use_optimization: str = "auto", **kwargs):
        self.model_type = model_type
        self.use_optimization = use_optimization
        self.kwargs = kwargs
        self.factory = MLModelFactory()
        self.model = None
        self.is_trained = False
        self.training_result = None
        
        # Default configuration
        self.config = ModelConfig(
            model_type=model_type,
            input_length=kwargs.get('input_length', 500),
            hidden_dims=kwargs.get('hidden_dims', [64, 32]),
            dropout_rate=kwargs.get('dropout_rate', 0.2),
            learning_rate=kwargs.get('learning_rate', 0.001),
            batch_size=kwargs.get('batch_size', 32),
            epochs=kwargs.get('epochs', 100),
            early_stopping_patience=kwargs.get('early_stopping_patience', 10),
            validation_split=kwargs.get('validation_split', 0.2),
            use_attention=kwargs.get('use_attention', False),
            use_residual=kwargs.get('use_residual', False),
            optimization_framework=use_optimization
        )
    
    def train(self, X: np.ndarray, y: np.ndarray, optimize_hyperparams: bool = True, **kwargs) -> TrainingResult:
        """Train the model with optional hyperparameter optimization."""
        logger.info(f"Training {self.model_type} model...")
        
        if optimize_hyperparams and len(X) > 100:
            logger.info("Optimizing hyperparameters...")
            self.model = self.factory.create_optimized_model(self.model_type, X, y)
        else:
            logger.info("Using default hyperparameters...")
            self.model = self.factory.create_model(self.model_type, self.config)
        
        # Train the model
        self.training_result = self.model.train(X, y, **kwargs)
        self.is_trained = True
        
        logger.info(f"Training completed. Best validation loss: {min(self.training_result.val_loss):.4f}")
        return self.training_result
    
    def train_or_load(self, X: np.ndarray, y: np.ndarray, model_path: Optional[str] = None, **kwargs) -> TrainingResult:
        """Train the model or load existing if available."""
        if model_path and Path(model_path).exists():
            logger.info(f"Loading existing model from {model_path}")
            if self.model is None:
                self.model = self.factory.create_model(self.model_type, self.config)
            
            if self.model.load_model(model_path):
                self.is_trained = True
                return TrainingResult(
                    model=self.model,
                    train_loss=[],
                    val_loss=[],
                    best_epoch=0,
                    training_time=0.0,
                    hyperparameters=asdict(self.config),
                    performance_metrics={'mse': 0.0, 'mae': 0.0, 'r2': 0.0},
                    model_path=model_path
                )
            else:
                logger.warning("Failed to load model, training new one...")
        
        return self.train(X, y, **kwargs)
    
    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """Estimate Hurst parameter using the trained model."""
        if not self.is_trained:
            logger.warning("Model not trained, using fallback estimation")
            return self._fallback_estimation(data)
        
        try:
            start_time = time.time()
            
            # Make prediction
            prediction = self.model.predict(data)
            hurst_estimate = float(prediction[0] if len(prediction) == 1 else np.mean(prediction))
            
            # Ensure valid range
            hurst_estimate = max(0.1, min(0.9, hurst_estimate))
            
            execution_time = time.time() - start_time
            
            # Calculate confidence interval (simplified)
            confidence_interval = (
                max(0.1, hurst_estimate - 0.1),
                min(0.9, hurst_estimate + 0.1)
            )
            
            return {
                "hurst_parameter": hurst_estimate,
                "confidence_interval": confidence_interval,
                "r_squared": self.training_result.performance_metrics.get('r2', 0.0) if self.training_result else 0.0,
                "p_value": None,
                "method": f"{self.model_type.upper()} (Enhanced ML)",
                "optimization_framework": self.use_optimization,
                "execution_time": execution_time,
                "model_info": {
                    "model_type": self.model_type,
                    "is_trained": self.is_trained,
                    "training_metrics": self.training_result.performance_metrics if self.training_result else {}
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return self._fallback_estimation(data)
    
    def _fallback_estimation(self, data: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation when model fails."""
        try:
            from lrdbenchmark.analysis.temporal.rs.rs_estimator_unified import RSEstimator
            rs_estimator = RSEstimator(use_optimization='numpy')
            rs_result = rs_estimator.estimate(data)
            
            return {
                "hurst_parameter": rs_result.get("hurst_parameter", 0.5),
                "confidence_interval": [0.4, 0.6],
                "r_squared": rs_result.get("r_squared", 0.0),
                "p_value": rs_result.get("p_value", None),
                "method": f"{self.model_type.upper()}_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
        except Exception:
            return {
                "hurst_parameter": 0.5,
                "confidence_interval": [0.4, 0.6],
                "r_squared": 0.0,
                "p_value": None,
                "method": f"{self.model_type.upper()}_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            "model_type": self.model_type,
            "is_trained": self.is_trained,
            "config": asdict(self.config) if hasattr(self.config, '__dataclass_fields__') else str(self.config),
            "training_result": asdict(self.training_result) if self.training_result else None,
            "optimization_framework": self.use_optimization
        }
    
    def get_model_path(self) -> str:
        """Get the path where the model should be saved."""
        model_dir = Path("models/ml_models")
        model_dir.mkdir(parents=True, exist_ok=True)
        return str(model_dir / f"{self.model_type}_enhanced_{int(time.time())}.pth")
    
    def save_model(self, path: Optional[str] = None) -> str:
        """Save the trained model."""
        if not self.is_trained or self.model is None:
            raise RuntimeError("No trained model to save")
        
        model_path = path or self.get_model_path()
        self.model._save_model()
        logger.info(f"Model saved to {model_path}")
        return model_path
    
    def load_model(self, path: str) -> bool:
        """Load a trained model."""
        if self.model is None:
            self.model = self.factory.create_model(self.model_type, self.config)
        
        success = self.model.load_model(path)
        if success:
            self.is_trained = True
            logger.info(f"Model loaded from {path}")
        else:
            logger.error(f"Failed to load model from {path}")
        
        return success

class EnhancedCNNEstimator(EnhancedMLEstimator):
    """Enhanced CNN estimator for LRD estimation."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        super().__init__("cnn", use_optimization, **kwargs)
        
        # CNN-specific defaults
        self.config.use_attention = kwargs.get('use_attention', True)
        self.config.input_length = kwargs.get('input_length', 500)

class EnhancedLSTMEstimator(EnhancedMLEstimator):
    """Enhanced LSTM estimator for LRD estimation."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        super().__init__("lstm", use_optimization, **kwargs)
        
        # LSTM-specific defaults
        self.config.use_attention = kwargs.get('use_attention', True)
        self.config.input_length = kwargs.get('input_length', 500)

class EnhancedGRUEstimator(EnhancedMLEstimator):
    """Enhanced GRU estimator for LRD estimation."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        super().__init__("gru", use_optimization, **kwargs)
        
        # GRU-specific defaults
        self.config.use_attention = kwargs.get('use_attention', True)
        self.config.input_length = kwargs.get('input_length', 500)

class EnhancedTransformerEstimator(EnhancedMLEstimator):
    """Enhanced Transformer estimator for LRD estimation."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        super().__init__("transformer", use_optimization, **kwargs)
        
        # Transformer-specific defaults
        self.config.use_attention = True  # Always use attention for transformer
        self.config.use_residual = kwargs.get('use_residual', True)
        self.config.input_length = kwargs.get('input_length', 500)

class EnhancedRandomForestEstimator:
    """Enhanced Random Forest estimator using scikit-learn with advanced features."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        self.use_optimization = use_optimization
        self.kwargs = kwargs
        self.model = None
        self.feature_extractor = TimeSeriesFeatureExtractor()
        self.is_trained = False
        
        # Random Forest parameters
        self.n_estimators = kwargs.get('n_estimators', 100)
        self.max_depth = kwargs.get('max_depth', 10)
        self.min_samples_split = kwargs.get('min_samples_split', 5)
        self.min_samples_leaf = kwargs.get('min_samples_leaf', 2)
        self.random_state = kwargs.get('random_state', 42)
    
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Train the Random Forest model."""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import cross_val_score
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            logger.info("Training Enhanced Random Forest model...")
            
            # Extract features
            X_features = []
            for i in range(len(X)):
                features = self.feature_extractor.extract_comprehensive_features(X[i])
                X_features.append(features)
            
            X_features = np.array(X_features)
            
            # Create and train model
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.random_state,
                n_jobs=-1
            )
            
            start_time = time.time()
            self.model.fit(X_features, y)
            training_time = time.time() - start_time
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_features, y, cv=5, scoring='neg_mean_squared_error')
            
            # Predictions for metrics
            y_pred = self.model.predict(X_features)
            
            performance_metrics = {
                'mse': mean_squared_error(y, y_pred),
                'mae': mean_absolute_error(y, y_pred),
                'r2': r2_score(y, y_pred),
                'cv_mse_mean': -np.mean(cv_scores),
                'cv_mse_std': np.std(cv_scores)
            }
            
            self.is_trained = True
            
            return {
                'model': self.model,
                'training_time': training_time,
                'performance_metrics': performance_metrics,
                'feature_importance': self.model.feature_importances_.tolist()
            }
            
        except Exception as e:
            logger.error(f"Random Forest training failed: {e}")
            raise
    
    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """Estimate Hurst parameter using the trained Random Forest."""
        if not self.is_trained:
            logger.warning("Random Forest not trained, using fallback estimation")
            return self._fallback_estimation(data)
        
        try:
            start_time = time.time()
            
            # Extract features
            features = self.feature_extractor.extract_comprehensive_features(data)
            features = features.reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            hurst_estimate = max(0.1, min(0.9, float(prediction)))
            
            execution_time = time.time() - start_time
            
            return {
                "hurst_parameter": hurst_estimate,
                "confidence_interval": [max(0.1, hurst_estimate - 0.1), min(0.9, hurst_estimate + 0.1)],
                "r_squared": 0.0,  # Would need training result
                "p_value": None,
                "method": "Random_Forest_Enhanced",
                "optimization_framework": self.use_optimization,
                "execution_time": execution_time,
                "model_info": {
                    "model_type": "random_forest",
                    "is_trained": self.is_trained,
                    "n_estimators": self.n_estimators
                }
            }
            
        except Exception as e:
            logger.error(f"Random Forest prediction failed: {e}")
            return self._fallback_estimation(data)
    
    def _fallback_estimation(self, data: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation."""
        try:
            from lrdbenchmark.analysis.temporal.rs.rs_estimator_unified import RSEstimator
            rs_estimator = RSEstimator(use_optimization='numpy')
            rs_result = rs_estimator.estimate(data)
            
            return {
                "hurst_parameter": rs_result.get("hurst_parameter", 0.5),
                "confidence_interval": [0.4, 0.6],
                "r_squared": rs_result.get("r_squared", 0.0),
                "p_value": rs_result.get("p_value", None),
                "method": "Random_Forest_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
        except Exception:
            return {
                "hurst_parameter": 0.5,
                "confidence_interval": [0.4, 0.6],
                "r_squared": 0.0,
                "p_value": None,
                "method": "Random_Forest_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_type": "random_forest",
            "is_trained": self.is_trained,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "optimization_framework": self.use_optimization
        }

class EnhancedSVREstimator:
    """Enhanced SVR estimator using scikit-learn with advanced features."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        self.use_optimization = use_optimization
        self.kwargs = kwargs
        self.model = None
        self.feature_extractor = TimeSeriesFeatureExtractor()
        self.is_trained = False
        
        # SVR parameters
        self.C = kwargs.get('C', 1.0)
        self.epsilon = kwargs.get('epsilon', 0.1)
        self.kernel = kwargs.get('kernel', 'rbf')
        self.gamma = kwargs.get('gamma', 'scale')
    
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Train the SVR model."""
        try:
            from sklearn.svm import SVR
            from sklearn.model_selection import cross_val_score
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            from sklearn.preprocessing import StandardScaler
            
            logger.info("Training Enhanced SVR model...")
            
            # Extract features
            X_features = []
            for i in range(len(X)):
                features = self.feature_extractor.extract_comprehensive_features(X[i])
                X_features.append(features)
            
            X_features = np.array(X_features)
            
            # Scale features
            self.scaler = StandardScaler()
            X_features_scaled = self.scaler.fit_transform(X_features)
            
            # Create and train model
            self.model = SVR(
                C=self.C,
                epsilon=self.epsilon,
                kernel=self.kernel,
                gamma=self.gamma
            )
            
            start_time = time.time()
            self.model.fit(X_features_scaled, y)
            training_time = time.time() - start_time
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_features_scaled, y, cv=5, scoring='neg_mean_squared_error')
            
            # Predictions for metrics
            y_pred = self.model.predict(X_features_scaled)
            
            performance_metrics = {
                'mse': mean_squared_error(y, y_pred),
                'mae': mean_absolute_error(y, y_pred),
                'r2': r2_score(y, y_pred),
                'cv_mse_mean': -np.mean(cv_scores),
                'cv_mse_std': np.std(cv_scores)
            }
            
            self.is_trained = True
            
            return {
                'model': self.model,
                'training_time': training_time,
                'performance_metrics': performance_metrics
            }
            
        except Exception as e:
            logger.error(f"SVR training failed: {e}")
            raise
    
    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """Estimate Hurst parameter using the trained SVR."""
        if not self.is_trained:
            logger.warning("SVR not trained, using fallback estimation")
            return self._fallback_estimation(data)
        
        try:
            start_time = time.time()
            
            # Extract features
            features = self.feature_extractor.extract_comprehensive_features(data)
            features = features.reshape(1, -1)
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            hurst_estimate = max(0.1, min(0.9, float(prediction)))
            
            execution_time = time.time() - start_time
            
            return {
                "hurst_parameter": hurst_estimate,
                "confidence_interval": [max(0.1, hurst_estimate - 0.1), min(0.9, hurst_estimate + 0.1)],
                "r_squared": 0.0,
                "p_value": None,
                "method": "SVR_Enhanced",
                "optimization_framework": self.use_optimization,
                "execution_time": execution_time,
                "model_info": {
                    "model_type": "svr",
                    "is_trained": self.is_trained,
                    "kernel": self.kernel
                }
            }
            
        except Exception as e:
            logger.error(f"SVR prediction failed: {e}")
            return self._fallback_estimation(data)
    
    def _fallback_estimation(self, data: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation."""
        try:
            from lrdbenchmark.analysis.temporal.rs.rs_estimator_unified import RSEstimator
            rs_estimator = RSEstimator(use_optimization='numpy')
            rs_result = rs_estimator.estimate(data)
            
            return {
                "hurst_parameter": rs_result.get("hurst_parameter", 0.5),
                "confidence_interval": [0.4, 0.6],
                "r_squared": rs_result.get("r_squared", 0.0),
                "p_value": rs_result.get("p_value", None),
                "method": "SVR_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
        except Exception:
            return {
                "hurst_parameter": 0.5,
                "confidence_interval": [0.4, 0.6],
                "r_squared": 0.0,
                "p_value": None,
                "method": "SVR_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_type": "svr",
            "is_trained": self.is_trained,
            "kernel": self.kernel,
            "C": self.C,
            "optimization_framework": self.use_optimization
        }

class EnhancedGradientBoostingEstimator:
    """Enhanced Gradient Boosting estimator using scikit-learn with advanced features."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        self.use_optimization = use_optimization
        self.kwargs = kwargs
        self.model = None
        self.feature_extractor = TimeSeriesFeatureExtractor()
        self.is_trained = False
        
        # Gradient Boosting parameters
        self.n_estimators = kwargs.get('n_estimators', 100)
        self.learning_rate = kwargs.get('learning_rate', 0.1)
        self.max_depth = kwargs.get('max_depth', 3)
        self.min_samples_split = kwargs.get('min_samples_split', 2)
        self.min_samples_leaf = kwargs.get('min_samples_leaf', 1)
        self.random_state = kwargs.get('random_state', 42)
    
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Train the Gradient Boosting model."""
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.model_selection import cross_val_score
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            logger.info("Training Enhanced Gradient Boosting model...")
            
            # Extract features
            X_features = []
            for i in range(len(X)):
                features = self.feature_extractor.extract_comprehensive_features(X[i])
                X_features.append(features)
            
            X_features = np.array(X_features)
            
            # Create and train model
            self.model = GradientBoostingRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.random_state
            )
            
            start_time = time.time()
            self.model.fit(X_features, y)
            training_time = time.time() - start_time
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_features, y, cv=5, scoring='neg_mean_squared_error')
            
            # Predictions for metrics
            y_pred = self.model.predict(X_features)
            
            performance_metrics = {
                'mse': mean_squared_error(y, y_pred),
                'mae': mean_absolute_error(y, y_pred),
                'r2': r2_score(y, y_pred),
                'cv_mse_mean': -np.mean(cv_scores),
                'cv_mse_std': np.std(cv_scores)
            }
            
            self.is_trained = True
            
            return {
                'model': self.model,
                'training_time': training_time,
                'performance_metrics': performance_metrics,
                'feature_importance': self.model.feature_importances_.tolist()
            }
            
        except Exception as e:
            logger.error(f"Gradient Boosting training failed: {e}")
            raise
    
    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """Estimate Hurst parameter using the trained Gradient Boosting."""
        if not self.is_trained:
            logger.warning("Gradient Boosting not trained, using fallback estimation")
            return self._fallback_estimation(data)
        
        try:
            start_time = time.time()
            
            # Extract features
            features = self.feature_extractor.extract_comprehensive_features(data)
            features = features.reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            hurst_estimate = max(0.1, min(0.9, float(prediction)))
            
            execution_time = time.time() - start_time
            
            return {
                "hurst_parameter": hurst_estimate,
                "confidence_interval": [max(0.1, hurst_estimate - 0.1), min(0.9, hurst_estimate + 0.1)],
                "r_squared": 0.0,
                "p_value": None,
                "method": "Gradient_Boosting_Enhanced",
                "optimization_framework": self.use_optimization,
                "execution_time": execution_time,
                "model_info": {
                    "model_type": "gradient_boosting",
                    "is_trained": self.is_trained,
                    "n_estimators": self.n_estimators
                }
            }
            
        except Exception as e:
            logger.error(f"Gradient Boosting prediction failed: {e}")
            return self._fallback_estimation(data)
    
    def _fallback_estimation(self, data: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation."""
        try:
            from lrdbenchmark.analysis.temporal.rs.rs_estimator_unified import RSEstimator
            rs_estimator = RSEstimator(use_optimization='numpy')
            rs_result = rs_estimator.estimate(data)
            
            return {
                "hurst_parameter": rs_result.get("hurst_parameter", 0.5),
                "confidence_interval": [0.4, 0.6],
                "r_squared": rs_result.get("r_squared", 0.0),
                "p_value": rs_result.get("p_value", None),
                "method": "Gradient_Boosting_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
        except Exception:
            return {
                "hurst_parameter": 0.5,
                "confidence_interval": [0.4, 0.6],
                "r_squared": 0.0,
                "p_value": None,
                "method": "Gradient_Boosting_fallback",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_type": "gradient_boosting",
            "is_trained": self.is_trained,
            "n_estimators": self.n_estimators,
            "learning_rate": self.learning_rate,
            "optimization_framework": self.use_optimization
        }

# Export all enhanced estimators
__all__ = [
    'EnhancedMLEstimator',
    'EnhancedCNNEstimator',
    'EnhancedLSTMEstimator', 
    'EnhancedGRUEstimator',
    'EnhancedTransformerEstimator',
    'EnhancedRandomForestEstimator',
    'EnhancedSVREstimator',
    'EnhancedGradientBoostingEstimator'
]
