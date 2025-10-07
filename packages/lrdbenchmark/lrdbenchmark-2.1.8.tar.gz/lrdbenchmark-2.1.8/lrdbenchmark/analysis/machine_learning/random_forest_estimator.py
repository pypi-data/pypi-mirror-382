#!/usr/bin/env python3
"""
Random Forest Estimator for Long-Range Dependence Analysis.

This module implements a proper Random Forest-based approach for estimating Hurst parameters
from time series data using scikit-learn's RandomForestRegressor with feature engineering.
"""

import numpy as np
import logging
from typing import Dict, Any, Union, List, Optional
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from pathlib import Path
from scipy import stats
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

class RandomForestEstimator(BaseEstimator):
    """
    Random Forest estimator for Hurst parameter estimation.
    
    This estimator uses Random Forest with engineered features from time series data
    to predict Hurst parameters. It includes feature extraction, model training,
    and prediction capabilities.
    """
    
    def __init__(self, 
                 n_estimators: int = 100,
                 max_depth: Optional[int] = None,
                 min_samples_split: int = 2,
                 min_samples_leaf: int = 1,
                 max_features: str = 'sqrt',
                 bootstrap: bool = True,
                 random_state: int = 42,
                 use_optimization: str = 'auto',
                 **kwargs):
        """
        Initialize Random Forest estimator.
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples to split a node
            min_samples_leaf: Minimum samples in a leaf
            max_features: Number of features to consider for splits
            bootstrap: Whether to use bootstrap sampling
            random_state: Random state for reproducibility
            use_optimization: Optimization framework (not used for RF)
            **kwargs: Additional parameters
        """
        super().__init__()
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.bootstrap = bootstrap
        self.random_state = random_state
        self.parameters = kwargs
        
        # Initialize components
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.feature_importance = None
        
        # Model path for saving/loading - try to find any available model first
        pretrained_path = get_pretrained_model_path("random_forest_estimator", "joblib")
        if pretrained_path:
            self.model_path = Path(pretrained_path)
            logger.info(f"Using pretrained Random Forest model from package: {self.model_path}")
        else:
            # Try to find any available model (joblib or pkl)
            available_model = find_available_model("random_forest_estimator", "models")
            if available_model:
                self.model_path = available_model
                logger.info(f"Found existing Random Forest model: {self.model_path}")
            else:
                # Default to joblib format for new models
                self.model_path = Path("models/random_forest_estimator.joblib")
                self.model_path.parent.mkdir(exist_ok=True)
                logger.info(f"Using local Random Forest model path: {self.model_path}")
        
        # Validate parameters
        self._validate_parameters()
    
    def _validate_parameters(self) -> None:
        """Validate Random Forest estimator parameters."""
        if self.n_estimators <= 0:
            raise ValueError("n_estimators must be positive")
        if self.max_depth is not None and self.max_depth <= 0:
            raise ValueError("max_depth must be positive or None")
        if self.min_samples_split < 2:
            raise ValueError("min_samples_split must be at least 2")
        if self.min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be at least 1")
        if self.max_features not in ['sqrt', 'log2', 'auto'] and not isinstance(self.max_features, (int, float)):
            raise ValueError("max_features must be 'sqrt', 'log2', 'auto', or a number")
        
    def _extract_features(self, data: np.ndarray) -> np.ndarray:
        """
        Extract features from time series data for Random Forest.
        
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
            stats.skew(data),
            stats.kurtosis(data)
        ])
        
        # Time series specific features
        # 1. Autocorrelation at different lags
        for lag in [1, 2, 5, 10, 20, 50, 100]:
            if len(data) > lag:
                autocorr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                features.append(autocorr if not np.isnan(autocorr) else 0.0)
            else:
                features.append(0.0)
        
        # 2. Variance of increments at different scales
        scales = [1, 2, 4, 8, 16]
        for scale in scales:
            if len(data) > scale:
                increments = data[scale:] - data[:-scale]
                features.extend([
                    np.var(increments),
                    np.mean(np.abs(increments)),
                    np.std(increments),
                    np.max(increments) - np.min(increments)  # Range
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
        
        # 3. Spectral features
        try:
            fft = np.fft.fft(data)
            power_spectrum = np.abs(fft) ** 2
            n = len(power_spectrum)
            
            # Frequency band power ratios
            bands = [(0, n//16), (n//16, n//8), (n//8, n//4), (n//4, n//2)]
            for low, high in bands:
                band_power = np.sum(power_spectrum[low:high])
                total_power = np.sum(power_spectrum)
                features.append(band_power / total_power if total_power > 0 else 0.0)
            
            # Spectral slope and intercept
            freqs = np.fft.fftfreq(n)[:n//2]
            log_freqs = np.log(freqs[1:])
            log_power = np.log(power_spectrum[1:n//2])
            if len(log_freqs) > 1 and len(log_power) > 1:
                slope, intercept = np.polyfit(log_freqs, log_power, 1)
                features.extend([slope, intercept])
            else:
                features.extend([0.0, 0.0])
            
            # Spectral centroid
            if np.sum(power_spectrum) > 0:
                spectral_centroid = np.sum(freqs * power_spectrum[:len(freqs)]) / np.sum(power_spectrum[:len(freqs)])
                features.append(spectral_centroid)
            else:
                features.append(0.0)
        except:
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        # 4. Detrended fluctuation analysis features
        try:
            n = len(data)
            scales = [10, 20, 50, 100, 200, 500]
            dfa_features = []
            
            for scale in scales:
                if n >= scale * 2:
                    n_segments = n // scale
                    segments = data[:n_segments * scale].reshape(n_segments, scale)
                    
                    detrended_segments = []
                    for segment in segments:
                        x = np.arange(len(segment))
                        p = np.polyfit(x, segment, 1)
                        trend = np.polyval(p, x)
                        detrended = segment - trend
                        detrended_segments.append(detrended)
                    
                    fluctuations = [np.sqrt(np.mean(seg**2)) for seg in detrended_segments]
                    dfa_features.append(np.mean(fluctuations))
                else:
                    dfa_features.append(0.0)
            
            features.extend(dfa_features)
            
            # DFA slope and intercept
            if len([f for f in dfa_features if f > 0]) >= 3:
                valid_scales = [scales[i] for i, f in enumerate(dfa_features) if f > 0]
                valid_fluctuations = [f for f in dfa_features if f > 0]
                if len(valid_scales) > 1:
                    log_scales = np.log(valid_scales)
                    log_fluctuations = np.log(valid_fluctuations)
                    slope, intercept = np.polyfit(log_scales, log_fluctuations, 1)
                    features.extend([slope, intercept])
                else:
                    features.extend([0.0, 0.0])
            else:
                features.extend([0.0, 0.0])
        except:
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        # 5. Wavelet-like features
        try:
            scales = [2, 4, 8, 16, 32, 64]
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
            
            # Wavelet slope and intercept
            if len([f for f in wavelet_features if f > 0]) >= 3:
                valid_scales = [scales[i] for i, f in enumerate(wavelet_features) if f > 0]
                valid_vars = [f for f in wavelet_features if f > 0]
                if len(valid_scales) > 1:
                    log_scales = np.log(valid_scales)
                    log_vars = np.log(valid_vars)
                    slope, intercept = np.polyfit(log_scales, log_vars, 1)
                    features.extend([slope, intercept])
                else:
                    features.extend([0.0, 0.0])
            else:
                features.extend([0.0, 0.0])
        except:
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        # 6. Hurst-related features
        try:
            # R/S analysis features
            n = len(data)
            rs_values = []
            scales = [10, 20, 50, 100, 200, 500]
            
            for scale in scales:
                if n >= scale * 2:
                    n_segments = n // scale
                    segments = data[:n_segments * scale].reshape(n_segments, scale)
                    
                    rs_segment = []
                    for segment in segments:
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
            
            # R/S slope and intercept
            if len([f for f in rs_values if f > 0]) >= 3:
                valid_scales = [scales[i] for i, f in enumerate(rs_values) if f > 0]
                valid_rs = [f for f in rs_values if f > 0]
                if len(valid_scales) > 1:
                    log_scales = np.log(valid_scales)
                    log_rs = np.log(valid_rs)
                    slope, intercept = np.polyfit(log_scales, log_rs, 1)
                    features.extend([slope, intercept])
                else:
                    features.extend([0.0, 0.0])
            else:
                features.extend([0.0, 0.0])
        except:
            features.extend([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
        
        # 7. Additional time series features
        try:
            # Trend features
            x = np.arange(len(data))
            trend_slope, trend_intercept = np.polyfit(x, data, 1)
            features.extend([trend_slope, trend_intercept])
            
            # Seasonality features
            if len(data) >= 20:
                periods = [5, 10, 20, 50]
                for period in periods:
                    if len(data) >= period * 2:
                        autocorr = np.corrcoef(data[:-period], data[period:])[0, 1]
                        features.append(autocorr if not np.isnan(autocorr) else 0.0)
                    else:
                        features.append(0.0)
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
            
            # Entropy-like features
            # Approximate entropy (simplified)
            if len(data) >= 20:
                # Calculate approximate entropy
                m = 2  # pattern length
                r = 0.2 * np.std(data)  # tolerance
                
                def _maxdist(xi, xj, N):
                    return max([abs(ua - va) for ua, va in zip(xi, xj)])
                
                def _approximate_entropy(U, m, r):
                    N = len(U)
                    def _phi(m):
                        C = np.zeros(N - m + 1)
                        for i in range(N - m + 1):
                            template_i = U[i:i + m]
                            for j in range(N - m + 1):
                                template_j = U[j:j + m]
                                if _maxdist(template_i, template_j, m) <= r:
                                    C[i] += 1.0
                        phi = np.mean(np.log(C / float(N - m + 1.0)))
                        return phi
                    return _phi(m) - _phi(m + 1)
                
                try:
                    approx_entropy = _approximate_entropy(data, m, r)
                    features.append(approx_entropy)
                except:
                    features.append(0.0)
            else:
                features.append(0.0)
        except:
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        # 8. Fractal dimension features
        try:
            # Box-counting dimension (simplified)
            if len(data) >= 20:
                # Resample data to different resolutions
                resolutions = [1, 2, 4, 8]
                box_counts = []
                
                for resolution in resolutions:
                    if len(data) >= resolution:
                        # Downsample data
                        downsampled = data[::resolution]
                        # Count boxes (simplified)
                        min_val, max_val = np.min(downsampled), np.max(downsampled)
                        if max_val > min_val:
                            n_boxes = int((max_val - min_val) / (resolution * 0.1)) + 1
                            box_counts.append(n_boxes)
                        else:
                            box_counts.append(1)
                    else:
                        box_counts.append(1)
                
                # Calculate fractal dimension
                if len(box_counts) > 1:
                    log_resolutions = np.log(resolutions)
                    log_counts = np.log(box_counts)
                    fractal_dim = -np.polyfit(log_resolutions, log_counts, 1)[0]
                    features.append(fractal_dim)
                else:
                    features.append(1.0)
            else:
                features.append(1.0)
        except:
            features.append(1.0)
        
        return np.array(features)
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train the Random Forest model.
        
        Args:
            X: Training data (time series)
            y: Target Hurst parameters
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training results
        """
        logger.info("Training Random Forest model...")
        
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
        
        # Initialize and train Random Forest model
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            max_features=self.max_features,
            bootstrap=self.bootstrap,
            random_state=self.random_state,
            n_jobs=-1  # Use all available cores
        )
        
        logger.info("Training Random Forest model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate on validation set
        y_pred = self.model.predict(X_val_scaled)
        mse = mean_squared_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)
        
        # Get feature importance
        self.feature_importance = self.model.feature_importances_
        
        self.is_trained = True
        
        # Save model
        self.save_model()
        
        results = {
            'mse': mse,
            'r2': r2,
            'n_features': X_features.shape[1],
            'n_train': len(X_train),
            'n_val': len(X_val),
            'feature_importance': self.feature_importance.tolist()
        }
        
        logger.info(f"Random Forest training completed: MSE={mse:.4f}, R²={r2:.4f}")
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
        Estimate Hurst parameter using Random Forest.
        
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
                    logger.info("Loaded pretrained Random Forest model")
                else:
                    logger.warning("No trained Random Forest model available, using fallback")
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
                "method": "random_forest",
                "optimization_framework": "sklearn",
                "model_info": f"Random Forest (n_estimators={self.n_estimators}, max_depth={self.max_depth})",
                "feature_count": len(self.feature_names),
                "feature_importance_available": self.feature_importance is not None
            }
            
        except Exception as e:
            logger.error(f"Random Forest estimation failed: {e}")
            return self._fallback_estimation(data)
    
    def _fallback_estimation(self, data: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation when Random Forest model is not available."""
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
                    "method": "random_forest_fallback_rs",
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
                "method": "random_forest_fallback_rs",
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
                "method": "random_forest_fallback_default",
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
                'feature_importance': self.feature_importance,
                'parameters': {
                    'n_estimators': self.n_estimators,
                    'max_depth': self.max_depth,
                    'min_samples_split': self.min_samples_split,
                    'min_samples_leaf': self.min_samples_leaf,
                    'max_features': self.max_features,
                    'bootstrap': self.bootstrap,
                    'random_state': self.random_state
                }
            }
            save_model_flexible(model_data, self.model_path, prefer_joblib=True)
            logger.info(f"Random Forest model saved to {self.model_path}")
    
    def load_model(self) -> bool:
        """Load a pretrained model."""
        try:
            if self.model_path.exists():
                model_data = load_model_flexible(self.model_path, suppress_warnings=True)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                self.feature_importance = model_data.get('feature_importance', None)
                self.is_trained = True
                logger.info(f"Random Forest model loaded from {self.model_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to load Random Forest model: {e}")
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model."""
        if not self.is_trained:
            return {"status": "not_trained"}
        
        return {
            "status": "trained",
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "n_features": len(self.feature_names),
            "feature_names": self.feature_names[:10],  # First 10 features
            "feature_importance_available": self.feature_importance is not None,
            "model_path": str(self.model_path)
        }
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance from the trained model."""
        return self.feature_importance
