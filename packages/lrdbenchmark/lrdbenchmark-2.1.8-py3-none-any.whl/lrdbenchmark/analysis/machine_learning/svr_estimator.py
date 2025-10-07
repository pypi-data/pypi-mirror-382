#!/usr/bin/env python3
"""
Support Vector Regression (SVR) Estimator for Long-Range Dependence Analysis.

This module implements a proper SVR-based approach for estimating Hurst parameters
from time series data using scikit-learn's SVR with feature engineering.
"""

import numpy as np
import logging
from typing import Dict, Any, Union, List, Optional
import warnings
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from pathlib import Path
from ...utils import load_model_flexible, save_model_flexible, find_available_model

from lrdbenchmark.models.estimators.base_estimator import BaseEstimator

# Import utility function for package data paths
try:
    from ...utils import get_pretrained_model_path
except ImportError:
    # Fallback for development
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from utils import get_pretrained_model_path

logger = logging.getLogger(__name__)

class SVREstimator(BaseEstimator):
    """
    Support Vector Regression estimator for Hurst parameter estimation.
    
    This estimator uses SVR with engineered features from time series data
    to predict Hurst parameters. It includes feature extraction, model training,
    and prediction capabilities.
    """
    
    def __init__(self, 
                 kernel: str = 'rbf',
                 C: float = 1.0,
                 gamma: str = 'scale',
                 epsilon: float = 0.1,
                 use_optimization: str = 'auto',
                 **kwargs):
        """
        Initialize SVR estimator.
        
        Args:
            kernel: SVR kernel type ('rbf', 'linear', 'poly', 'sigmoid')
            C: Regularization parameter
            gamma: Kernel coefficient
            epsilon: Epsilon-tube parameter
            use_optimization: Optimization framework (not used for SVR)
            **kwargs: Additional parameters
        """
        super().__init__()
        self.kernel = kernel
        self.C = C
        self.gamma = gamma
        self.epsilon = epsilon
        self.parameters = kwargs
        
        # Initialize components
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        
        # Model path for saving/loading - try to find any available model first
        pretrained_path = get_pretrained_model_path("svr_estimator", "joblib")
        if pretrained_path:
            self.model_path = Path(pretrained_path)
            logger.info(f"Using pretrained SVR model from package: {self.model_path}")
        else:
            # Try to find any available model (joblib or pkl)
            available_model = find_available_model("svr_estimator", "models")
            if available_model:
                self.model_path = available_model
                logger.info(f"Found existing SVR model: {self.model_path}")
            else:
                # Default to joblib format for new models
                self.model_path = Path("models/svr_estimator.joblib")
                self.model_path.parent.mkdir(exist_ok=True)
                logger.info(f"Using local SVR model path: {self.model_path}")
        
        # Validate parameters
        self._validate_parameters()
    
    def _validate_parameters(self) -> None:
        """Validate SVR estimator parameters."""
        if self.C <= 0:
            raise ValueError("C parameter must be positive")
        if self.epsilon < 0:
            raise ValueError("epsilon parameter must be non-negative")
        if self.kernel not in ['rbf', 'linear', 'poly', 'sigmoid']:
            raise ValueError(f"Unsupported kernel: {self.kernel}")
        
    def _extract_features(self, data: np.ndarray) -> np.ndarray:
        """
        Extract features from time series data for SVR.
        
        Args:
            data: Input time series data
            
        Returns:
            Feature vector
        """
        features = []
        
        # Basic statistical features
        features.extend([
            np.mean(data),
            np.std(data),
            np.var(data),
            np.min(data),
            np.max(data),
            np.median(data),
            np.percentile(data, 25),
            np.percentile(data, 75),
        ])
        
        # Time series specific features
        # 1. Autocorrelation at different lags
        for lag in [1, 2, 5, 10, 20]:
            if len(data) > lag:
                autocorr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                features.append(autocorr if not np.isnan(autocorr) else 0.0)
            else:
                features.append(0.0)
        
        # 2. Variance of increments
        if len(data) > 1:
            increments = np.diff(data)
            features.extend([
                np.var(increments),
                np.mean(np.abs(increments)),
                np.std(increments)
            ])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        # 3. Spectral features (simplified)
        try:
            fft = np.fft.fft(data)
            power_spectrum = np.abs(fft) ** 2
            # Low frequency power ratio
            n = len(power_spectrum)
            low_freq_power = np.sum(power_spectrum[:n//4])
            total_power = np.sum(power_spectrum)
            features.append(low_freq_power / total_power if total_power > 0 else 0.0)
        except:
            features.append(0.0)
        
        # 4. Detrended fluctuation analysis features (simplified)
        try:
            # Simple DFA-like features
            n = len(data)
            scales = [10, 20, 50, 100]
            dfa_features = []
            
            for scale in scales:
                if n >= scale * 2:
                    # Divide into segments
                    n_segments = n // scale
                    segments = data[:n_segments * scale].reshape(n_segments, scale)
                    
                    # Detrend each segment
                    detrended_segments = []
                    for segment in segments:
                        x = np.arange(len(segment))
                        p = np.polyfit(x, segment, 1)
                        trend = np.polyval(p, x)
                        detrended = segment - trend
                        detrended_segments.append(detrended)
                    
                    # Calculate fluctuation
                    fluctuations = [np.sqrt(np.mean(seg**2)) for seg in detrended_segments]
                    dfa_features.append(np.mean(fluctuations))
                else:
                    dfa_features.append(0.0)
            
            features.extend(dfa_features)
        except:
            features.extend([0.0, 0.0, 0.0, 0.0])
        
        # 5. Wavelet-like features (simplified)
        try:
            # Simple wavelet variance at different scales
            scales = [2, 4, 8, 16]
            wavelet_features = []
            
            for scale in scales:
                if len(data) >= scale * 2:
                    # Simple averaging at different scales
                    downsampled = []
                    for i in range(0, len(data) - scale + 1, scale):
                        downsampled.append(np.mean(data[i:i+scale]))
                    wavelet_features.append(np.var(downsampled))
                else:
                    wavelet_features.append(0.0)
            
            features.extend(wavelet_features)
        except:
            features.extend([0.0, 0.0, 0.0, 0.0])
        
        # 6. Hurst-related features
        try:
            # R/S analysis features
            n = len(data)
            rs_values = []
            scales = [10, 20, 50, 100]
            
            for scale in scales:
                if n >= scale * 2:
                    n_segments = n // scale
                    segments = data[:n_segments * scale].reshape(n_segments, scale)
                    
                    rs_segment = []
                    for segment in segments:
                        # Calculate R/S for this segment
                        mean_val = np.mean(segment)
                        deviations = segment - mean_val
                        cumulative_deviations = np.cumsum(deviations)
                        
                        R = np.max(cumulative_deviations) - np.min(cumulative_deviations)
                        S = np.std(segment)
                        
                        if S > 0:
                            rs_segment.append(R / S)
                        else:
                            rs_segment.append(1.0)
                    
                    rs_values.append(np.mean(rs_segment))
                else:
                    rs_values.append(1.0)
            
            features.extend(rs_values)
        except:
            features.extend([1.0, 1.0, 1.0, 1.0])
        
        return np.array(features)
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train the SVR model.
        
        Args:
            X: Training data (time series)
            y: Target Hurst parameters
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training results
        """
        logger.info("Training SVR model...")
        
        # Extract features from all training samples
        logger.info("Extracting features from training data...")
        X_features = []
        for i, sample in enumerate(X):
            if i % 100 == 0:
                logger.info(f"  Processing sample {i}/{len(X)}")
            features = self._extract_features(sample)
            X_features.append(features)
        
        X_features = np.array(X_features)
        
        # Store feature names for reference
        self.feature_names = [f"feature_{i}" for i in range(X_features.shape[1])]
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_features, y, test_size=validation_split, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Initialize and train SVR model
        self.model = SVR(
            kernel=self.kernel,
            C=self.C,
            gamma=self.gamma,
            epsilon=self.epsilon
        )
        
        logger.info("Training SVR model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate on validation set
        y_pred = self.model.predict(X_val_scaled)
        mse = mean_squared_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)
        
        self.is_trained = True
        
        # Save model
        self.save_model()
        
        results = {
            'mse': mse,
            'r2': r2,
            'n_features': X_features.shape[1],
            'n_train': len(X_train),
            'n_val': len(X_val)
        }
        
        logger.info(f"SVR training completed: MSE={mse:.4f}, R²={r2:.4f}")
        return results
    
    def predict(self, data: np.ndarray) -> float:
        """
        Predict Hurst parameter for a single time series.
        
        Args:
            data: Input time series data
            
        Returns:
            Predicted Hurst parameter
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Extract features
        features = self._extract_features(data)
        features = features.reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        
        # Ensure prediction is in valid range
        prediction = np.clip(prediction, 0.0, 1.0)
        
        return prediction
    
    def estimate(self, data: Union[np.ndarray, list]) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using SVR.
        
        Args:
            data: Input time series data
            
        Returns:
            Estimation results
        """
        data = np.asarray(data)
        
        try:
            if not self.is_trained:
                # Try to load pretrained model
                if self.load_model():
                    logger.info("Loaded pretrained SVR model")
                else:
                    logger.warning("No trained SVR model available, using fallback")
                    return self._fallback_estimation(data)
            
            # Make prediction
            hurst_estimate = self.predict(data)
            
            # Calculate confidence interval (simplified)
            confidence_interval = [
                max(0.0, hurst_estimate - 0.1),
                min(1.0, hurst_estimate + 0.1)
            ]
            
            return {
                "hurst_parameter": hurst_estimate,
                "confidence_interval": confidence_interval,
                "r_squared": 0.0,  # Would need validation data
                "p_value": None,
                "method": "svr",
                "optimization_framework": "sklearn",
                "model_info": f"SVR (kernel={self.kernel}, C={self.C})",
                "feature_count": len(self.feature_names)
            }
            
        except Exception as e:
            logger.error(f"SVR estimation failed: {e}")
            return self._fallback_estimation(data)
    
    def _fallback_estimation(self, data: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation when SVR model is not available."""
        # Simple statistical estimation as fallback
        try:
            # Use R/S analysis as fallback
            n = len(data)
            if n < 10:
                return {
                    "hurst_parameter": 0.5,
                    "confidence_interval": [0.4, 0.6],
                    "r_squared": 0.0,
                    "p_value": None,
                    "method": "svr_fallback_rs",
                    "optimization_framework": "numpy",
                    "fallback_used": True
                }
            
            # Simple R/S calculation
            mean_val = np.mean(data)
            deviations = data - mean_val
            cumulative_deviations = np.cumsum(deviations)
            
            R = np.max(cumulative_deviations) - np.min(cumulative_deviations)
            S = np.std(data)
            
            if S > 0:
                rs_ratio = R / S
                # Convert R/S to Hurst parameter (simplified)
                hurst_estimate = 0.5 + 0.1 * np.log(rs_ratio)
                hurst_estimate = np.clip(hurst_estimate, 0.0, 1.0)
            else:
                hurst_estimate = 0.5
            
            return {
                "hurst_parameter": hurst_estimate,
                "confidence_interval": [0.4, 0.6],
                "r_squared": 0.0,
                "p_value": None,
                "method": "svr_fallback_rs",
                "optimization_framework": "numpy",
                "fallback_used": True
            }
            
        except Exception as e:
            logger.error(f"Fallback estimation failed: {e}")
            return {
                "hurst_parameter": 0.5,
                "confidence_interval": [0.4, 0.6],
                "r_squared": 0.0,
                "p_value": None,
                "method": "svr_fallback_default",
                "optimization_framework": "numpy",
                "fallback_used": True,
                "error": str(e)
            }
    
    def save_model(self):
        """Save the trained model."""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'parameters': {
                    'kernel': self.kernel,
                    'C': self.C,
                    'gamma': self.gamma,
                    'epsilon': self.epsilon
                }
            }
            save_model_flexible(model_data, self.model_path, prefer_joblib=True)
            logger.info(f"SVR model saved to {self.model_path}")
    
    def load_model(self) -> bool:
        """Load a pretrained model."""
        try:
            if self.model_path.exists():
                model_data = load_model_flexible(self.model_path, suppress_warnings=True)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                self.is_trained = True
                logger.info(f"SVR model loaded from {self.model_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to load SVR model: {e}")
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model."""
        if not self.is_trained:
            return {"status": "not_trained"}
        
        return {
            "status": "trained",
            "kernel": self.kernel,
            "C": self.C,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "n_features": len(self.feature_names),
            "feature_names": self.feature_names[:10],  # First 10 features
            "model_path": str(self.model_path)
        }
