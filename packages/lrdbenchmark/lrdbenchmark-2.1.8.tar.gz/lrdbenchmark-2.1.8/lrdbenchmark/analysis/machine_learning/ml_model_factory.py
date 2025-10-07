#!/usr/bin/env python3
"""
Advanced Machine Learning Model Factory for LRD Estimation.

This module provides an intelligent factory system for creating, training, and optimizing
machine learning models for long-range dependence estimation with adaptive mechanisms.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import joblib
import optuna
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
import warnings
from pathlib import Path
import json
import time
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import logging

# Advanced libraries
try:
    import numpyro
    import numpyro.distributions as dist
    from numpyro.infer import MCMC, NUTS, Predictive
    from numpyro.contrib.control_flow import scan
    NUMPYRO_AVAILABLE = True
except ImportError:
    NUMPYRO_AVAILABLE = False

try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, random
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

try:
    import numba
    from numba import jit as numba_jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for ML models."""
    model_type: str
    input_length: int
    output_dim: int = 1
    hidden_dims: List[int] = None
    dropout_rate: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    use_bayesian: bool = False
    use_attention: bool = False
    use_residual: bool = False
    optimization_framework: str = "auto"
    
    def __post_init__(self):
        if self.hidden_dims is None:
            self.hidden_dims = [64, 32]

@dataclass
class TrainingResult:
    """Results from model training."""
    model: Any
    train_loss: List[float]
    val_loss: List[float]
    best_epoch: int
    training_time: float
    hyperparameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    model_path: str

class BaseMLModel(ABC):
    """Base class for all ML models."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.device = self._get_device()
        self.is_trained = False
        
    def _get_device(self) -> torch.device:
        """Get the best available device."""
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return torch.device("mps")
        else:
            return torch.device("cpu")
    
    @abstractmethod
    def _create_model(self) -> nn.Module:
        """Create the model architecture."""
        pass
    
    @abstractmethod
    def _extract_features(self, data: np.ndarray) -> np.ndarray:
        """Extract features from time series data."""
        pass
    
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> TrainingResult:
        """Train the model with adaptive mechanisms."""
        start_time = time.time()
        
        # Extract features
        X_features = self._extract_features(X)
        
        # Create model if not exists
        if self.model is None:
            self.model = self._create_model().to(self.device)
        
        # Prepare data
        X_tensor = torch.FloatTensor(X_features).to(self.device)
        y_tensor = torch.FloatTensor(y).to(self.device)
        
        # Create data loaders
        train_loader, val_loader = self._create_data_loaders(X_tensor, y_tensor)
        
        # Train with adaptive learning
        train_losses, val_losses, best_epoch = self._adaptive_train(train_loader, val_loader)
        
        training_time = time.time() - start_time
        
        # Calculate performance metrics
        performance_metrics = self._calculate_metrics(val_loader)
        
        # Save model
        model_path = self._save_model()
        
        self.is_trained = True
        
        return TrainingResult(
            model=self.model,
            train_loss=train_losses,
            val_loss=val_losses,
            best_epoch=best_epoch,
            training_time=training_time,
            hyperparameters=asdict(self.config),
            performance_metrics=performance_metrics,
            model_path=model_path
        )
    
    def _create_data_loaders(self, X: torch.Tensor, y: torch.Tensor) -> Tuple[DataLoader, DataLoader]:
        """Create train and validation data loaders."""
        # Split data
        n_samples = len(X)
        val_size = int(n_samples * self.config.validation_split)
        train_size = n_samples - val_size
        
        indices = torch.randperm(n_samples)
        train_indices = indices[:train_size]
        val_indices = indices[train_size:]
        
        train_dataset = TensorDataset(X[train_indices], y[train_indices])
        val_dataset = TensorDataset(X[val_indices], y[val_indices])
        
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size, shuffle=False)
        
        return train_loader, val_loader
    
    def _adaptive_train(self, train_loader: DataLoader, val_loader: DataLoader) -> Tuple[List[float], List[float], int]:
        """Train with adaptive learning rate and early stopping."""
        optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
        criterion = nn.MSELoss()
        
        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        best_epoch = 0
        patience_counter = 0
        
        for epoch in range(self.config.epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs.squeeze(), batch_y)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            # Validation phase
            self.model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    outputs = self.model(batch_X)
                    loss = criterion(outputs.squeeze(), batch_y)
                    val_loss += loss.item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_epoch = epoch
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), 'best_model_temp.pth')
            else:
                patience_counter += 1
                
            if patience_counter >= self.config.early_stopping_patience:
                logger.info(f"Early stopping at epoch {epoch}")
                break
                
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # Load best model
        if Path('best_model_temp.pth').exists():
            self.model.load_state_dict(torch.load('best_model_temp.pth'))
            Path('best_model_temp.pth').unlink()
        
        return train_losses, val_losses, best_epoch
    
    def _calculate_metrics(self, val_loader: DataLoader) -> Dict[str, float]:
        """Calculate performance metrics."""
        self.model.eval()
        predictions = []
        targets = []
        
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                outputs = self.model(batch_X)
                predictions.extend(outputs.squeeze().cpu().numpy())
                targets.extend(batch_y.cpu().numpy())
        
        predictions = np.array(predictions)
        targets = np.array(targets)
        
        mse = np.mean((predictions - targets) ** 2)
        mae = np.mean(np.abs(predictions - targets))
        r2 = 1 - (np.sum((targets - predictions) ** 2) / np.sum((targets - np.mean(targets)) ** 2))
        
        return {
            'mse': float(mse),
            'mae': float(mae),
            'r2': float(r2)
        }
    
    def _save_model(self) -> str:
        """Save the trained model."""
        model_dir = Path("models/ml_models")
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = model_dir / f"{self.config.model_type}_{int(time.time())}.pth"
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': asdict(self.config),
            'is_trained': self.is_trained
        }, model_path)
        
        return str(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load a trained model."""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.config = ModelConfig(**checkpoint['config'])
            self.model = self._create_model().to(self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.is_trained = checkpoint['is_trained']
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        self.model.eval()
        X_features = self._extract_features(X)
        X_tensor = torch.FloatTensor(X_features).to(self.device)
        
        with torch.no_grad():
            predictions = self.model(X_tensor)
        
        return predictions.cpu().numpy().flatten()

class TimeSeriesFeatureExtractor:
    """Advanced feature extractor for time series data."""
    
    @staticmethod
    def extract_comprehensive_features(data: np.ndarray) -> np.ndarray:
        """Extract comprehensive features from time series."""
        features = []
        
        # Basic statistical features
        features.extend([
            np.mean(data),
            np.std(data),
            np.var(data),
            np.median(data),
            np.percentile(data, 25),
            np.percentile(data, 75),
            np.skew(data),
            np.kurtosis(data)
        ])
        
        # Autocorrelation features
        if len(data) > 1:
            for lag in [1, 2, 5, 10]:
                if len(data) > lag:
                    autocorr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                    features.append(autocorr if not np.isnan(autocorr) else 0.0)
                else:
                    features.append(0.0)
        
        # Spectral features
        if len(data) > 4:
            fft_vals = np.abs(np.fft.fft(data))
            freqs = np.fft.fftfreq(len(data))
            positive_freqs = freqs > 0
            
            if np.sum(positive_freqs) > 1:
                # Spectral slope
                log_freqs = np.log(freqs[positive_freqs] + 1e-8)
                log_fft = np.log(fft_vals[positive_freqs] + 1e-8)
                if len(log_freqs) > 1:
                    spectral_slope = np.polyfit(log_freqs, log_fft, 1)[0]
                    features.append(spectral_slope)
                else:
                    features.append(-1.0)
                
                # Spectral centroid
                spectral_centroid = np.sum(freqs[positive_freqs] * fft_vals[positive_freqs]) / np.sum(fft_vals[positive_freqs])
                features.append(spectral_centroid)
            else:
                features.extend([-1.0, 0.0])
        
        # Detrended fluctuation analysis (simplified)
        if len(data) > 10:
            # Remove trend
            x = np.arange(len(data))
            trend = np.polyval(np.polyfit(x, data, 1), x)
            detrended = data - trend
            
            # Calculate fluctuation
            segment_size = max(10, len(data) // 4)
            segments = [detrended[i:i+segment_size] for i in range(0, len(detrended), segment_size) if len(detrended[i:i+segment_size]) == segment_size]
            
            if segments:
                fluctuations = [np.std(seg) for seg in segments]
                dfa_alpha = np.polyfit(np.log(range(1, len(fluctuations)+1)), np.log(fluctuations + 1e-8), 1)[0]
                features.append(dfa_alpha)
            else:
                features.append(0.5)
        else:
            features.append(0.5)
        
        # Wavelet features (simplified)
        if len(data) > 8:
            # Simple wavelet-like features using differences
            diff1 = np.diff(data)
            diff2 = np.diff(diff1)
            
            features.extend([
                np.mean(np.abs(diff1)),
                np.std(diff1),
                np.mean(np.abs(diff2)),
                np.std(diff2)
            ])
        else:
            features.extend([0.0, 0.0, 0.0, 0.0])
        
        return np.array(features)

class AdaptiveCNN(nn.Module):
    """Adaptive CNN for time series LRD estimation."""
    
    def __init__(self, input_length: int, hidden_dims: List[int], dropout_rate: float = 0.2, use_attention: bool = False):
        super(AdaptiveCNN, self).__init__()
        
        self.input_length = input_length
        self.use_attention = use_attention
        
        # Adaptive convolution layers
        self.conv_layers = nn.ModuleList()
        in_channels = 1
        
        for i, out_channels in enumerate([32, 64, 128]):
            self.conv_layers.append(nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=3, padding=1),
                nn.BatchNorm1d(out_channels),
                nn.ReLU(),
                nn.MaxPool1d(2),
                nn.Dropout(dropout_rate)
            ))
            in_channels = out_channels
        
        # Calculate output size
        x = torch.randn(1, 1, input_length)
        for conv in self.conv_layers:
            x = conv(x)
        conv_output_size = x.view(1, -1).size(1)
        
        # Attention mechanism
        if use_attention:
            self.attention = nn.MultiheadAttention(conv_output_size, num_heads=4, batch_first=True)
        
        # Adaptive fully connected layers
        self.fc_layers = nn.ModuleList()
        prev_size = conv_output_size
        
        for hidden_dim in hidden_dims:
            self.fc_layers.append(nn.Sequential(
                nn.Linear(prev_size, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ))
            prev_size = hidden_dim
        
        # Output layer
        self.output_layer = nn.Sequential(
            nn.Linear(prev_size, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Ensure correct input shape
        if x.dim() == 2:
            x = x.unsqueeze(1)
        
        # Convolutional layers
        for conv in self.conv_layers:
            x = conv(x)
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Attention mechanism
        if self.use_attention:
            x_att = x.unsqueeze(1)  # Add sequence dimension
            x_att, _ = self.attention(x_att, x_att, x_att)
            x = x_att.squeeze(1)
        
        # Fully connected layers
        for fc in self.fc_layers:
            x = fc(x)
        
        # Output
        x = self.output_layer(x)
        
        return x

class AdaptiveTransformer(nn.Module):
    """Adaptive Transformer for time series LRD estimation."""
    
    def __init__(self, input_length: int, d_model: int = 64, nhead: int = 4, num_layers: int = 2, 
                 hidden_dims: List[int] = None, dropout_rate: float = 0.2, use_residual: bool = False):
        super(AdaptiveTransformer, self).__init__()
        
        self.input_length = input_length
        self.d_model = d_model
        self.use_residual = use_residual
        
        if hidden_dims is None:
            hidden_dims = [64, 32]
        
        # Input projection
        self.input_projection = nn.Linear(1, d_model)
        
        # Positional encoding
        self.pos_encoding = nn.Parameter(torch.randn(input_length, d_model))
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            dropout=dropout_rate,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Adaptive output head
        self.output_head = nn.ModuleList()
        prev_size = d_model
        
        for hidden_dim in hidden_dims:
            self.output_head.append(nn.Sequential(
                nn.Linear(prev_size, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ))
            prev_size = hidden_dim
        
        # Final output
        self.final_output = nn.Sequential(
            nn.Linear(prev_size, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        batch_size = x.size(0)
        
        # Input projection
        x = self.input_projection(x)  # (batch_size, seq_len, d_model)
        
        # Add positional encoding
        x = x + self.pos_encoding.unsqueeze(0)
        
        # Transformer encoding
        x = self.transformer(x)  # (batch_size, seq_len, d_model)
        
        # Global average pooling
        x = x.mean(dim=1)  # (batch_size, d_model)
        
        # Output head
        for layer in self.output_head:
            x = layer(x)
        
        # Final output
        x = self.final_output(x)
        
        return x

class CNNModel(BaseMLModel):
    """CNN model for LRD estimation."""
    
    def _create_model(self) -> nn.Module:
        return AdaptiveCNN(
            input_length=self.config.input_length,
            hidden_dims=self.config.hidden_dims,
            dropout_rate=self.config.dropout_rate,
            use_attention=self.config.use_attention
        )
    
    def _extract_features(self, data: np.ndarray) -> np.ndarray:
        """Extract features for CNN (raw time series)."""
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        # Normalize data
        data_normalized = (data - np.mean(data, axis=1, keepdims=True)) / (np.std(data, axis=1, keepdims=True) + 1e-8)
        
        # Resize to input length
        if data_normalized.shape[1] != self.config.input_length:
            if data_normalized.shape[1] > self.config.input_length:
                data_normalized = data_normalized[:, :self.config.input_length]
            else:
                padded = np.zeros((data_normalized.shape[0], self.config.input_length))
                padded[:, :data_normalized.shape[1]] = data_normalized
                data_normalized = padded
        
        return data_normalized

class TransformerModel(BaseMLModel):
    """Transformer model for LRD estimation."""
    
    def _create_model(self) -> nn.Module:
        return AdaptiveTransformer(
            input_length=self.config.input_length,
            d_model=64,
            nhead=4,
            num_layers=2,
            hidden_dims=self.config.hidden_dims,
            dropout_rate=self.config.dropout_rate,
            use_residual=self.config.use_residual
        )
    
    def _extract_features(self, data: np.ndarray) -> np.ndarray:
        """Extract features for Transformer (raw time series)."""
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        # Normalize data
        data_normalized = (data - np.mean(data, axis=1, keepdims=True)) / (np.std(data, axis=1, keepdims=True) + 1e-8)
        
        # Resize to input length
        if data_normalized.shape[1] != self.config.input_length:
            if data_normalized.shape[1] > self.config.input_length:
                data_normalized = data_normalized[:, :self.config.input_length]
            else:
                padded = np.zeros((data_normalized.shape[0], self.config.input_length))
                padded[:, :data_normalized.shape[1]] = data_normalized
                data_normalized = padded
        
        # Add feature dimension for transformer
        return data_normalized.reshape(data_normalized.shape[0], data_normalized.shape[1], 1)

class MLModelFactory:
    """Intelligent factory for creating and optimizing ML models."""
    
    def __init__(self):
        self.models = {}
        self.optimization_results = {}
    
    def create_model(self, model_type: str, config: ModelConfig) -> BaseMLModel:
        """Create a model instance."""
        if model_type.lower() == "cnn":
            return CNNModel(config)
        elif model_type.lower() == "transformer":
            return TransformerModel(config)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def optimize_hyperparameters(self, model_type: str, X: np.ndarray, y: np.ndarray, 
                                n_trials: int = 50) -> Dict[str, Any]:
        """Optimize hyperparameters using Optuna."""
        
        def objective(trial):
            # Suggest hyperparameters
            config = ModelConfig(
                model_type=model_type,
                input_length=X.shape[1] if X.ndim > 1 else 500,
                hidden_dims=[trial.suggest_int('hidden_dim_1', 32, 128),
                           trial.suggest_int('hidden_dim_2', 16, 64)],
                dropout_rate=trial.suggest_float('dropout_rate', 0.1, 0.5),
                learning_rate=trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True),
                batch_size=trial.suggest_categorical('batch_size', [16, 32, 64]),
                epochs=50,  # Reduced for optimization
                early_stopping_patience=5,
                use_attention=trial.suggest_categorical('use_attention', [True, False]),
                use_residual=trial.suggest_categorical('use_residual', [True, False])
            )
            
            # Create and train model
            model = self.create_model(model_type, config)
            result = model.train(X, y)
            
            # Return validation loss (to minimize)
            return result.performance_metrics['mse']
        
        # Create study
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials)
        
        # Store results
        self.optimization_results[model_type] = {
            'best_params': study.best_params,
            'best_value': study.best_value,
            'study': study
        }
        
        return self.optimization_results[model_type]
    
    def create_optimized_model(self, model_type: str, X: np.ndarray, y: np.ndarray) -> BaseMLModel:
        """Create a model with optimized hyperparameters."""
        if model_type not in self.optimization_results:
            self.optimize_hyperparameters(model_type, X, y)
        
        best_params = self.optimization_results[model_type]['best_params']
        
        config = ModelConfig(
            model_type=model_type,
            input_length=X.shape[1] if X.ndim > 1 else 500,
            hidden_dims=[best_params['hidden_dim_1'], best_params['hidden_dim_2']],
            dropout_rate=best_params['dropout_rate'],
            learning_rate=best_params['learning_rate'],
            batch_size=best_params['batch_size'],
            use_attention=best_params['use_attention'],
            use_residual=best_params['use_residual']
        )
        
        return self.create_model(model_type, config)
    
    def ensemble_predict(self, models: List[BaseMLModel], X: np.ndarray) -> np.ndarray:
        """Make ensemble predictions."""
        predictions = []
        for model in models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Average predictions
        return np.mean(predictions, axis=0)
    
    def get_model_recommendation(self, data_size: int, data_complexity: str = "medium") -> str:
        """Get model recommendation based on data characteristics."""
        if data_size < 1000:
            return "cnn"  # CNN is more efficient for small datasets
        elif data_complexity == "high":
            return "transformer"  # Transformer for complex patterns
        else:
            return "cnn"  # Default to CNN

# Bayesian optimization using NumPyro (if available)
if NUMPYRO_AVAILABLE:
    class BayesianOptimizer:
        """Bayesian optimization for hyperparameter tuning."""
        
        def __init__(self, model_type: str):
            self.model_type = model_type
        
        def model(self, X: np.ndarray, y: np.ndarray = None):
            """Bayesian model for hyperparameter optimization."""
            # Prior distributions for hyperparameters
            dropout_rate = numpyro.sample("dropout_rate", dist.Beta(2, 8))
            learning_rate = numpyro.sample("learning_rate", dist.LogNormal(0, 1))
            hidden_dim_1 = numpyro.sample("hidden_dim_1", dist.DiscreteUniform(32, 128))
            hidden_dim_2 = numpyro.sample("hidden_dim_2", dist.DiscreteUniform(16, 64))
            
            # Model performance (simplified)
            performance = numpyro.sample("performance", dist.Normal(0.5, 0.1))
            
            if y is not None:
                numpyro.sample("obs", dist.Normal(performance, 0.05), obs=y)
            
            return performance
        
        def optimize(self, X: np.ndarray, y: np.ndarray, n_samples: int = 1000) -> Dict[str, Any]:
            """Run Bayesian optimization."""
            # This is a simplified example - in practice, you'd integrate with actual model training
            kernel = NUTS(self.model)
            mcmc = MCMC(kernel, num_warmup=500, num_samples=n_samples)
            mcmc.run(random.PRNGKey(0), X, y)
            
            samples = mcmc.get_samples()
            
            return {
                'best_dropout_rate': float(np.mean(samples['dropout_rate'])),
                'best_learning_rate': float(np.exp(np.mean(samples['learning_rate']))),
                'best_hidden_dim_1': int(np.mean(samples['hidden_dim_1'])),
                'best_hidden_dim_2': int(np.mean(samples['hidden_dim_2'])),
                'samples': samples
            }

# Export main classes
__all__ = [
    'MLModelFactory',
    'ModelConfig', 
    'TrainingResult',
    'CNNModel',
    'TransformerModel',
    'TimeSeriesFeatureExtractor',
    'BayesianOptimizer'
]
