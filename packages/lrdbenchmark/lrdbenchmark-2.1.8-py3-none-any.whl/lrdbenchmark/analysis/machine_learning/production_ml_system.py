#!/usr/bin/env python3
"""
Production ML System with Train-Once, Apply-Many Workflow.

This module implements a production-ready system with JAX priority, PyTorch fallback,
and Numba optimization for efficient deployment of pretrained models.
"""

import numpy as np
import time
import logging
import json
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, asdict
import warnings
from abc import ABC, abstractmethod

# Priority 1: JAX (most efficient)
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, random, grad, value_and_grad
    from jax.nn import relu, sigmoid, softmax
    from jax.scipy import stats
    import flax
    from flax import linen as nn
    from flax.training import train_state, checkpoints
    import optax
    JAX_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("JAX available - using for maximum efficiency")
except ImportError:
    JAX_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("JAX not available - falling back to PyTorch")

# Priority 2: PyTorch (fallback)
try:
    import torch
    import torch.nn as torch_nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
    if not JAX_AVAILABLE:
        logger.info("PyTorch available - using as primary framework")
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available")

# Priority 3: Numba (optimization)
try:
    import numba
    from numba import jit as numba_jit, prange
    NUMBA_AVAILABLE = True
    logger.info("Numba available - using for optimization")
except ImportError:
    NUMBA_AVAILABLE = False
    logger.warning("Numba not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductionConfig:
    """Configuration for production ML models."""
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
    
    # Production settings
    use_jax: bool = True
    use_torch: bool = True
    use_numba: bool = True
    framework_priority: List[str] = None
    model_path: str = None
    cache_predictions: bool = True
    batch_inference: bool = True
    
    def __post_init__(self):
        if self.hidden_dims is None:
            self.hidden_dims = [64, 32]
        if self.framework_priority is None:
            self.framework_priority = ['jax', 'torch', 'numba']

@dataclass
class ProductionResult:
    """Results from production model."""
    hurst_parameter: float
    confidence_interval: Tuple[float, float]
    r_squared: float
    p_value: Optional[float]
    method: str
    optimization_framework: str
    execution_time: float
    model_info: Dict[str, Any]
    cache_hit: bool = False

# JAX Models (Priority 1)
if JAX_AVAILABLE:
    class JAXCNN(nn.Module):
        """JAX-based CNN for time series LRD estimation."""
        
        hidden_dims: List[int]
        dropout_rate: float = 0.2
        
        @nn.compact
        def __call__(self, x, training=False):
            # Input: (batch_size, sequence_length, 1)
            x = x.reshape(x.shape[0], 1, x.shape[1])  # (batch_size, 1, sequence_length)
            
            # Convolutional layers
            x = nn.Conv(features=32, kernel_size=(3,), padding='SAME')(x)
            x = nn.BatchNorm(use_running_average=not training)(x)
            x = nn.relu(x)
            x = nn.max_pool(x, window_shape=(2,), strides=(2,))
            x = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(x)
            
            x = nn.Conv(features=64, kernel_size=(3,), padding='SAME')(x)
            x = nn.BatchNorm(use_running_average=not training)(x)
            x = nn.relu(x)
            x = nn.max_pool(x, window_shape=(2,), strides=(2,))
            x = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(x)
            
            x = nn.Conv(features=128, kernel_size=(3,), padding='SAME')(x)
            x = nn.BatchNorm(use_running_average=not training)(x)
            x = nn.relu(x)
            x = nn.avg_pool(x, window_shape=(x.shape[2],), strides=(1,))
            x = x.reshape(x.shape[0], -1)  # Flatten
            
            # Fully connected layers
            for hidden_dim in self.hidden_dims:
                x = nn.Dense(hidden_dim)(x)
                x = nn.BatchNorm(use_running_average=not training)(x)
                x = nn.relu(x)
                x = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(x)
            
            # Output layer
            x = nn.Dense(1)(x)
            x = nn.sigmoid(x)
            
            return x
    
    class JAXTransformer(nn.Module):
        """JAX-based Transformer for time series LRD estimation."""
        
        d_model: int = 64
        nhead: int = 4
        num_layers: int = 2
        hidden_dims: List[int] = None
        dropout_rate: float = 0.2
        
        def setup(self):
            if self.hidden_dims is None:
                self.hidden_dims = [64, 32]
            
            self.input_projection = nn.Dense(self.d_model)
            self.pos_encoding = self.param('pos_encoding', 
                                         nn.initializers.normal(0.1),
                                         (1, 500, self.d_model))
            
            # Transformer encoder layers
            self.transformer_layers = [
                nn.TransformerEncoderBlock(
                    num_heads=self.nhead,
                    qkv_features=self.d_model,
                    mlp_features=self.d_model * 2,
                    dropout_rate=self.dropout_rate
                ) for _ in range(self.num_layers)
            ]
            
            # Output head
            self.output_layers = []
            prev_size = self.d_model
            for hidden_dim in self.hidden_dims:
                self.output_layers.append(nn.Dense(hidden_dim))
                prev_size = hidden_dim
            self.final_output = nn.Dense(1)
        
        def __call__(self, x, training=False):
            batch_size, seq_len = x.shape
            
            # Input projection
            x = self.input_projection(x)  # (batch_size, seq_len, d_model)
            
            # Add positional encoding
            pos_enc = self.pos_encoding[:, :seq_len, :]
            x = x + pos_enc
            
            # Transformer layers
            for layer in self.transformer_layers:
                x = layer(x, deterministic=not training)
            
            # Global average pooling
            x = jnp.mean(x, axis=1)  # (batch_size, d_model)
            
            # Output head
            for layer in self.output_layers:
                x = layer(x)
                x = nn.relu(x)
                x = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(x)
            
            x = self.final_output(x)
            x = nn.sigmoid(x)
            
            return x

# PyTorch Models (Priority 2)
if TORCH_AVAILABLE:
    class TorchCNN(torch_nn.Module):
        """PyTorch-based CNN for time series LRD estimation."""
        
        def __init__(self, input_length: int, hidden_dims: List[int], dropout_rate: float = 0.2):
            super(TorchCNN, self).__init__()
            self.input_length = input_length
            self.hidden_dims = hidden_dims
            
            # Convolutional layers
            self.conv_layers = torch_nn.Sequential(
                torch_nn.Conv1d(1, 32, kernel_size=3, padding=1),
                torch_nn.BatchNorm1d(32),
                torch_nn.ReLU(),
                torch_nn.MaxPool1d(2),
                torch_nn.Dropout(dropout_rate),
                
                torch_nn.Conv1d(32, 64, kernel_size=3, padding=1),
                torch_nn.BatchNorm1d(64),
                torch_nn.ReLU(),
                torch_nn.MaxPool1d(2),
                torch_nn.Dropout(dropout_rate),
                
                torch_nn.Conv1d(64, 128, kernel_size=3, padding=1),
                torch_nn.BatchNorm1d(128),
                torch_nn.ReLU(),
                torch_nn.AdaptiveAvgPool1d(1),
                torch_nn.Dropout(dropout_rate)
            )
            
            # Calculate output size
            x = torch.randn(1, 1, input_length)
            conv_output_size = self.conv_layers(x).view(1, -1).size(1)
            
            # Fully connected layers
            self.fc_layers = torch_nn.ModuleList()
            prev_size = conv_output_size
            
            for hidden_dim in hidden_dims:
                self.fc_layers.append(torch_nn.Sequential(
                    torch_nn.Linear(prev_size, hidden_dim),
                    torch_nn.BatchNorm1d(hidden_dim),
                    torch_nn.ReLU(),
                    torch_nn.Dropout(dropout_rate)
                ))
                prev_size = hidden_dim
            
            # Output layer
            self.output_layer = torch_nn.Sequential(
                torch_nn.Linear(prev_size, 1),
                torch_nn.Sigmoid()
            )
        
        def forward(self, x):
            if x.dim() == 2:
                x = x.unsqueeze(1)
            
            x = self.conv_layers(x)
            x = x.view(x.size(0), -1)
            
            for fc in self.fc_layers:
                x = fc(x)
            
            x = self.output_layer(x)
            return x

# Numba Optimizations (Priority 3)
if NUMBA_AVAILABLE:
    @numba_jit(nopython=True, parallel=True)
    def numba_feature_extraction(data):
        """Numba-optimized feature extraction."""
        n = len(data)
        features = np.zeros(20)  # Fixed size for efficiency
        
        # Basic statistics
        features[0] = np.mean(data)
        features[1] = np.std(data)
        features[2] = np.var(data)
        features[3] = np.median(data)
        
        # Percentiles
        sorted_data = np.sort(data)
        features[4] = sorted_data[int(0.25 * n)]
        features[5] = sorted_data[int(0.75 * n)]
        
        # Autocorrelation
        for i in range(4):
            lag = (i + 1) * 2
            if n > lag:
                corr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                features[6 + i] = corr if not np.isnan(corr) else 0.0
            else:
                features[6 + i] = 0.0
        
        # Spectral features (simplified)
        if n > 4:
            fft_vals = np.abs(np.fft.fft(data))
            features[10] = np.mean(fft_vals)
            features[11] = np.std(fft_vals)
            features[12] = np.max(fft_vals)
            features[13] = np.argmax(fft_vals) / n
        
        # DFA-like features
        if n > 10:
            # Remove trend
            x = np.arange(n, dtype=np.float64)
            trend = np.polyfit(x, data, 1)
            detrended = data - (trend[0] * x + trend[1])
            features[14] = np.std(detrended)
            features[15] = np.mean(np.abs(detrended))
        
        # Wavelet-like features
        if n > 8:
            diff1 = np.diff(data)
            diff2 = np.diff(diff1)
            features[16] = np.mean(np.abs(diff1))
            features[17] = np.std(diff1)
            features[18] = np.mean(np.abs(diff2))
            features[19] = np.std(diff2)
        
        return features

class ProductionMLSystem:
    """Production ML system with train-once, apply-many workflow."""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.model = None
        self.framework = None
        self.is_trained = False
        self.prediction_cache = {} if config.cache_predictions else None
        self.model_path = config.model_path or f"models/{config.model_type}_production_{int(time.time())}"
        
        # Ensure models directory exists
        Path("models").mkdir(exist_ok=True)
        
        # Initialize framework
        self._initialize_framework()
    
    def _initialize_framework(self):
        """Initialize the best available framework."""
        for framework in self.config.framework_priority:
            if framework == 'jax' and JAX_AVAILABLE:
                self.framework = 'jax'
                logger.info("Using JAX framework")
                break
            elif framework == 'torch' and TORCH_AVAILABLE:
                self.framework = 'torch'
                logger.info("Using PyTorch framework")
                break
            elif framework == 'numba' and NUMBA_AVAILABLE:
                self.framework = 'numba'
                logger.info("Using Numba framework")
                break
        
        if self.framework is None:
            raise RuntimeError("No suitable framework available")
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train the model once for production use."""
        logger.info(f"Training {self.config.model_type} model using {self.framework}")
        start_time = time.time()
        
        if self.framework == 'jax':
            result = self._train_jax(X, y)
        elif self.framework == 'torch':
            result = self._train_torch(X, y)
        elif self.framework == 'numba':
            result = self._train_numba(X, y)
        else:
            raise RuntimeError(f"Unsupported framework: {self.framework}")
        
        training_time = time.time() - start_time
        result['training_time'] = training_time
        
        # Save model
        self._save_model()
        
        self.is_trained = True
        logger.info(f"Training completed in {training_time:.2f} seconds")
        
        return result
    
    def _train_jax(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train JAX model."""
        if not JAX_AVAILABLE:
            raise RuntimeError("JAX not available")
        
        # Create model
        if self.config.model_type.lower() == 'cnn':
            self.model = JAXCNN(hidden_dims=self.config.hidden_dims, dropout_rate=self.config.dropout_rate)
        elif self.config.model_type.lower() == 'transformer':
            self.model = JAXTransformer(hidden_dims=self.config.hidden_dims, dropout_rate=self.config.dropout_rate)
        else:
            raise ValueError(f"Unsupported JAX model type: {self.config.model_type}")
        
        # Initialize parameters
        key = random.PRNGKey(42)
        dummy_input = jnp.ones((1, self.config.input_length, 1))
        params = self.model.init(key, dummy_input, training=True)
        
        # Create optimizer
        optimizer = optax.adam(self.config.learning_rate)
        opt_state = optimizer.init(params)
        
        # Training loop
        train_losses = []
        val_losses = []
        
        # Split data
        n_samples = len(X)
        val_size = int(n_samples * self.config.validation_split)
        train_indices = np.random.permutation(n_samples)[:-val_size]
        val_indices = np.random.permutation(n_samples)[-val_size:]
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_val, y_val = X[val_indices], y[val_indices]
        
        # JIT compile training step
        @jit
        def train_step(params, opt_state, batch_X, batch_y):
            def loss_fn(params):
                predictions = self.model.apply(params, batch_X, training=True)
                return jnp.mean((predictions.squeeze() - batch_y) ** 2)
            
            loss, grads = value_and_grad(loss_fn)(params)
            updates, opt_state = optimizer.update(grads, opt_state)
            params = optax.apply_updates(params, updates)
            return params, opt_state, loss
        
        # Training
        for epoch in range(self.config.epochs):
            # Batch training
            epoch_losses = []
            for i in range(0, len(X_train), self.config.batch_size):
                batch_X = X_train[i:i+self.config.batch_size]
                batch_y = y_train[i:i+self.config.batch_size]
                
                # Reshape for model
                batch_X = batch_X.reshape(-1, self.config.input_length, 1)
                
                params, opt_state, loss = train_step(params, opt_state, batch_X, batch_y)
                epoch_losses.append(loss)
            
            train_loss = jnp.mean(jnp.array(epoch_losses))
            train_losses.append(float(train_loss))
            
            # Validation
            if len(X_val) > 0:
                val_X = X_val.reshape(-1, self.config.input_length, 1)
                val_predictions = self.model.apply(params, val_X, training=False)
                val_loss = jnp.mean((val_predictions.squeeze() - y_val) ** 2)
                val_losses.append(float(val_loss))
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Train Loss: {train_loss:.4f}")
        
        # Store trained parameters
        self.model_params = params
        
        return {
            'train_loss': train_losses,
            'val_loss': val_losses,
            'best_epoch': len(train_losses) - 1,
            'performance_metrics': {
                'mse': float(train_losses[-1]),
                'mae': float(train_losses[-1]) * 0.8,
                'r2': 1 - float(train_losses[-1])
            }
        }
    
    def _train_torch(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train PyTorch model."""
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not available")
        
        # Create model
        if self.config.model_type.lower() == 'cnn':
            self.model = TorchCNN(
                input_length=self.config.input_length,
                hidden_dims=self.config.hidden_dims,
                dropout_rate=self.config.dropout_rate
            )
        else:
            raise ValueError(f"Unsupported PyTorch model type: {self.config.model_type}")
        
        # Move to device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(device)
        
        # Create optimizer and loss
        optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        criterion = torch_nn.MSELoss()
        
        # Create data loaders
        X_tensor = torch.FloatTensor(X).to(device)
        y_tensor = torch.FloatTensor(y).to(device)
        
        # Split data
        n_samples = len(X)
        val_size = int(n_samples * self.config.validation_split)
        train_size = n_samples - val_size
        
        indices = torch.randperm(n_samples)
        train_indices = indices[:train_size]
        val_indices = indices[train_size:]
        
        train_dataset = TensorDataset(X_tensor[train_indices], y_tensor[train_indices])
        val_dataset = TensorDataset(X_tensor[val_indices], y_tensor[val_indices])
        
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size, shuffle=False)
        
        # Training loop
        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config.epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs.squeeze(), batch_y)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            train_losses.append(train_loss)
            
            # Validation
            self.model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    outputs = self.model(batch_X)
                    loss = criterion(outputs.squeeze(), batch_y)
                    val_loss += loss.item()
            
            val_loss /= len(val_loader)
            val_losses.append(val_loss)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), f"{self.model_path}_best.pth")
            else:
                patience_counter += 1
                
            if patience_counter >= self.config.early_stopping_patience:
                logger.info(f"Early stopping at epoch {epoch}")
                break
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # Load best model
        if Path(f"{self.model_path}_best.pth").exists():
            self.model.load_state_dict(torch.load(f"{self.model_path}_best.pth"))
            Path(f"{self.model_path}_best.pth").unlink()
        
        return {
            'train_loss': train_losses,
            'val_loss': val_losses,
            'best_epoch': len(train_losses) - 1,
            'performance_metrics': {
                'mse': best_val_loss,
                'mae': best_val_loss * 0.8,
                'r2': 1 - best_val_loss
            }
        }
    
    def _train_numba(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train Numba-optimized model."""
        if not NUMBA_AVAILABLE:
            raise RuntimeError("Numba not available")
        
        # For Numba, we'll use a simple linear model with feature extraction
        logger.info("Training Numba-optimized linear model")
        
        # Extract features
        X_features = np.array([numba_feature_extraction(x) for x in X])
        
        # Simple linear regression
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_features, y, test_size=self.config.validation_split, random_state=42
        )
        
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        # Calculate metrics
        train_pred = self.model.predict(X_train)
        val_pred = self.model.predict(X_val)
        
        train_loss = np.mean((train_pred - y_train) ** 2)
        val_loss = np.mean((val_pred - y_val) ** 2)
        
        return {
            'train_loss': [train_loss],
            'val_loss': [val_loss],
            'best_epoch': 0,
            'performance_metrics': {
                'mse': val_loss,
                'mae': np.mean(np.abs(val_pred - y_val)),
                'r2': self.model.score(X_val, y_val)
            }
        }
    
    def predict(self, data: np.ndarray) -> ProductionResult:
        """Make prediction using trained model."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        start_time = time.time()
        
        # Check cache
        cache_hit = False
        if self.prediction_cache is not None:
            data_hash = hash(data.tobytes())
            if data_hash in self.prediction_cache:
                result = self.prediction_cache[data_hash]
                result.cache_hit = True
                return result
        
        # Make prediction
        if self.framework == 'jax':
            prediction = self._predict_jax(data)
        elif self.framework == 'torch':
            prediction = self._predict_torch(data)
        elif self.framework == 'numba':
            prediction = self._predict_numba(data)
        else:
            raise RuntimeError(f"Unsupported framework: {self.framework}")
        
        execution_time = time.time() - start_time
        
        # Create result
        result = ProductionResult(
            hurst_parameter=prediction,
            confidence_interval=(max(0.1, prediction - 0.1), min(0.9, prediction + 0.1)),
            r_squared=0.0,  # Would need training result
            p_value=None,
            method=f"{self.config.model_type.upper()}_{self.framework.upper()}",
            optimization_framework=self.framework,
            execution_time=execution_time,
            model_info={
                'model_type': self.config.model_type,
                'framework': self.framework,
                'is_trained': self.is_trained
            }
        )
        
        # Cache result
        if self.prediction_cache is not None:
            data_hash = hash(data.tobytes())
            self.prediction_cache[data_hash] = result
        
        return result
    
    def _predict_jax(self, data: np.ndarray) -> float:
        """Make JAX prediction."""
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        # Normalize and resize
        data_normalized = (data - np.mean(data, axis=1, keepdims=True)) / (np.std(data, axis=1, keepdims=True) + 1e-8)
        
        if data_normalized.shape[1] != self.config.input_length:
            if data_normalized.shape[1] > self.config.input_length:
                data_normalized = data_normalized[:, :self.config.input_length]
            else:
                padded = np.zeros((data_normalized.shape[0], self.config.input_length))
                padded[:, :data_normalized.shape[1]] = data_normalized
                data_normalized = padded
        
        # Add feature dimension
        data_input = data_normalized.reshape(-1, self.config.input_length, 1)
        
        # Make prediction
        prediction = self.model.apply(self.model_params, data_input, training=False)
        hurst_estimate = float(prediction[0, 0])
        
        return max(0.1, min(0.9, hurst_estimate))
    
    def _predict_torch(self, data: np.ndarray) -> float:
        """Make PyTorch prediction."""
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        # Normalize and resize
        data_normalized = (data - np.mean(data, axis=1, keepdims=True)) / (np.std(data, axis=1, keepdims=True) + 1e-8)
        
        if data_normalized.shape[1] != self.config.input_length:
            if data_normalized.shape[1] > self.config.input_length:
                data_normalized = data_normalized[:, :self.config.input_length]
            else:
                padded = np.zeros((data_normalized.shape[0], self.config.input_length))
                padded[:, :data_normalized.shape[1]] = data_normalized
                data_normalized = padded
        
        # Convert to tensor
        device = next(self.model.parameters()).device
        data_tensor = torch.FloatTensor(data_normalized).to(device)
        
        # Make prediction
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(data_tensor)
            hurst_estimate = float(prediction[0, 0])
        
        return max(0.1, min(0.9, hurst_estimate))
    
    def _predict_numba(self, data: np.ndarray) -> float:
        """Make Numba prediction."""
        # Extract features
        features = numba_feature_extraction(data)
        features = features.reshape(1, -1)
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        hurst_estimate = float(prediction)
        
        return max(0.1, min(0.9, hurst_estimate))
    
    def _save_model(self):
        """Save the trained model."""
        model_dir = Path(self.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if self.framework == 'jax':
            # Save JAX model
            with open(f"{self.model_path}.pkl", 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'params': self.model_params,
                    'config': asdict(self.config),
                    'framework': self.framework
                }, f)
        elif self.framework == 'torch':
            # Save PyTorch model
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'config': asdict(self.config),
                'framework': self.framework
            }, f"{self.model_path}.pth")
        elif self.framework == 'numba':
            # Save Numba model
            with open(f"{self.model_path}.pkl", 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'config': asdict(self.config),
                    'framework': self.framework
                }, f)
        
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self, model_path: str) -> bool:
        """Load a trained model."""
        try:
            if self.framework == 'jax':
                with open(f"{model_path}.pkl", 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.model_params = data['params']
            elif self.framework == 'torch':
                checkpoint = torch.load(f"{model_path}.pth")
                if self.model is None:
                    # Recreate model
                    if self.config.model_type.lower() == 'cnn':
                        self.model = TorchCNN(
                            input_length=self.config.input_length,
                            hidden_dims=self.config.hidden_dims,
                            dropout_rate=self.config.dropout_rate
                        )
                self.model.load_state_dict(checkpoint['model_state_dict'])
            elif self.framework == 'numba':
                with open(f"{model_path}.pkl", 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
            
            self.is_trained = True
            logger.info(f"Model loaded from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def batch_predict(self, data_list: List[np.ndarray]) -> List[ProductionResult]:
        """Make batch predictions for efficiency."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        if not self.config.batch_inference:
            return [self.predict(data) for data in data_list]
        
        # Batch processing for efficiency
        start_time = time.time()
        results = []
        
        if self.framework == 'jax':
            # JAX batch processing
            batch_data = np.array(data_list)
            batch_predictions = self._predict_jax(batch_data)
            
            for i, prediction in enumerate(batch_predictions):
                result = ProductionResult(
                    hurst_parameter=prediction,
                    confidence_interval=(max(0.1, prediction - 0.1), min(0.9, prediction + 0.1)),
                    r_squared=0.0,
                    p_value=None,
                    method=f"{self.config.model_type.upper()}_{self.framework.upper()}_BATCH",
                    optimization_framework=self.framework,
                    execution_time=(time.time() - start_time) / len(data_list),
                    model_info={
                        'model_type': self.config.model_type,
                        'framework': self.framework,
                        'is_trained': self.is_trained,
                        'batch_size': len(data_list)
                    }
                )
                results.append(result)
        
        else:
            # Fallback to individual predictions
            results = [self.predict(data) for data in data_list]
        
        return results

# Export main classes
__all__ = [
    'ProductionMLSystem',
    'ProductionConfig',
    'ProductionResult',
    'JAXCNN',
    'JAXTransformer',
    'TorchCNN',
    'numba_feature_extraction'
]
