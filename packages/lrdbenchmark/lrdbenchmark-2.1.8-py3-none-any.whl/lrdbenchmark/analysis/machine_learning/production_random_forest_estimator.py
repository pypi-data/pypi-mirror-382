#!/usr/bin/env python3
"""
Production Random Forest Estimator with Train-Once, Apply-Many Workflow.

This module provides a production-ready Random Forest estimator that uses
the train-once, apply-many pipeline for efficient deployment.
"""

import numpy as np
import warnings
from typing import Dict, Any, Optional, Union
import time
import logging

# Try to import the production system
try:
    from .train_once_apply_many import TrainOnceApplyManyPipeline, TrainingDataConfig, ModelTrainingConfig
    from .production_ml_system import ProductionMLSystem, ProductionConfig
    PRODUCTION_AVAILABLE = True
except ImportError:
    PRODUCTION_AVAILABLE = False

# Try to import the enhanced implementation
try:
    from .enhanced_ml_estimators import EnhancedRandomForestEstimator
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Fallback to R/S if enhanced version not available
if not ENHANCED_AVAILABLE:
    try:
        from lrdbenchmark.analysis.temporal.rs.rs_estimator_unified import RSEstimator
        FALLBACK_AVAILABLE = True
    except ImportError:
        FALLBACK_AVAILABLE = False

logger = logging.getLogger(__name__)

class ProductionRandomForestEstimator:
    """Production Random Forest estimator with train-once, apply-many workflow."""
    
    def __init__(self, use_optimization: str = "auto", **kwargs):
        self.use_optimization = use_optimization
        self.kwargs = kwargs
        self.estimator = None
        self.framework_used = None
        self.production_model = None
        self.is_production_ready = False
        
        # Initialize the best available estimator
        self._initialize_estimator()
    
    def _initialize_estimator(self):
        """Initialize the best available estimator."""
        # Try production system first
        if PRODUCTION_AVAILABLE:
            try:
                # Check if we have a trained model available
                from .train_once_apply_many import ModelRegistry
                registry = ModelRegistry("models/registry.json")
                best_model = registry.get_best_model(model_type="random_forest")
                
                if best_model:
                    # Deploy the trained model
                    config = ProductionConfig(**best_model['model_config'])
                    self.production_model = ProductionMLSystem(config)
                    if self.production_model.load_model(best_model['model_path']):
                        self.framework_used = "production"
                        self.is_production_ready = True
                        logger.info("Using production-trained Random Forest model")
                        return
                
            except Exception as e:
                logger.warning(f"Production system not available: {e}")
        
        # Try enhanced implementation
        if ENHANCED_AVAILABLE:
            try:
                self.estimator = EnhancedRandomForestEstimator(
                    use_optimization=self.use_optimization,
                    **self.kwargs
                )
                self.framework_used = "enhanced"
                return
            except Exception as e:
                warnings.warn(f"Enhanced Random Forest not available: {e}")
        
        # Fallback to R/S
        if FALLBACK_AVAILABLE:
            try:
                self.estimator = RSEstimator(use_optimization=self.use_optimization)
                self.framework_used = "fallback"
                warnings.warn("Using R/S fallback estimation")
                return
            except Exception as e:
                warnings.warn(f"R/S fallback not available: {e}")
        
        raise RuntimeError("No Random Forest estimator available")
    
    def train_production_model(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train a production-ready model."""
        if not PRODUCTION_AVAILABLE:
            logger.warning("Production system not available for training")
            return False
        
        try:
            # Create training configuration
            training_data_config = TrainingDataConfig(
                n_samples_per_model=len(X),
                sequence_lengths=[X.shape[1]] if X.ndim > 1 else [500],
                hurst_range=(np.min(y), np.max(y))
            )
            
            model_training_config = ModelTrainingConfig(
                model_types=['random_forest'],
                input_length=X.shape[1] if X.ndim > 1 else 500,
                prefer_jax=True,
                prefer_torch=True,
                prefer_numba=True
            )
            
            # Create and run pipeline
            pipeline = TrainOnceApplyManyPipeline(
                training_data_config=training_data_config,
                model_training_config=model_training_config
            )
            
            # Train models
            results = pipeline.run_training_pipeline()
            
            if results:
                # Deploy the best model
                self.production_model = pipeline.deploy_best_model(model_type="random_forest")
                if self.production_model:
                    self.framework_used = "production"
                    self.is_production_ready = True
                    logger.info("Production Random Forest model trained and deployed")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to train production model: {e}")
            return False
    
    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """Estimate Hurst parameter using Random Forest."""
        if self.is_production_ready and self.production_model:
            # Use production model
            try:
                result = self.production_model.predict(data)
                return {
                    "hurst_parameter": result.hurst_parameter,
                    "confidence_interval": result.confidence_interval,
                    "r_squared": result.r_squared,
                    "p_value": result.p_value,
                    "method": result.method,
                    "optimization_framework": result.optimization_framework,
                    "execution_time": result.execution_time,
                    "framework_used": self.framework_used,
                    "model_info": result.model_info
                }
            except Exception as e:
                logger.warning(f"Production model prediction failed: {e}")
        
        # Fallback to other estimators
        if self.estimator is None:
            raise RuntimeError("Estimator not initialized")
        
        try:
            start_time = time.time()
            result = self.estimator.estimate(data)
            execution_time = time.time() - start_time
            
            # Add execution time and framework info
            result["execution_time"] = execution_time
            result["framework_used"] = self.framework_used
            
            return result
            
        except Exception as e:
            warnings.warn(f"Random Forest estimation failed: {e}")
            # Return a default result
            return {
                "hurst_parameter": 0.5,
                "confidence_interval": [0.4, 0.6],
                "r_squared": 0.0,
                "p_value": None,
                "method": "Random_Forest_failed",
                "optimization_framework": self.use_optimization,
                "execution_time": 0.0,
                "framework_used": self.framework_used,
                "error": str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        if self.is_production_ready and self.production_model:
            info = self.production_model.get_model_info()
        elif hasattr(self.estimator, 'get_model_info'):
            info = self.estimator.get_model_info()
        else:
            info = {}
        
        info.update({
            "estimator_type": "RandomForest",
            "framework_used": self.framework_used,
            "optimization_framework": self.use_optimization,
            "is_production_ready": self.is_production_ready
        })
        
        return info

# Backward compatibility alias
RandomForestEstimator = ProductionRandomForestEstimator
