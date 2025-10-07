# LRDBenchmark

A comprehensive, reproducible framework for Long-Range Dependence (LRD) estimation and benchmarking across Classical, Machine Learning, and Neural Network methods.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Features

**Comprehensive Estimator Suite:**
- **8 Classical Methods**: R/S, DFA, DMA, Higuchi, Periodogram, GPH, Whittle, CWT
- **3 Machine Learning Models**: Random Forest, SVR, Gradient Boosting with optimized hyperparameters  
- **4 Neural Network Architectures**: LSTM, GRU, CNN, Transformer with pre-trained models
- **Generalized Hurst Exponent (GHE)**: Advanced multifractal analysis capabilities

**🏆 Latest Performance Results:**
- **LSTM leads overall performance**: 9.68/10 (0.097 MAE) - Rank #1
- **CNN follows closely**: 9.66/10 (0.103 MAE) - Rank #2
- **R/S (Classical) excels**: 9.51/10 (0.099 MAE) - Rank #5
- **All methods achieve perfect robustness** (1.00/1.00) across contamination scenarios

**Robust Heavy-Tail Analysis:**
- α-stable distribution modeling for heavy-tailed time series
- Adaptive preprocessing: standardization, winsorization, log-winsorization, detrending
- Contamination-aware estimation with intelligent fallback mechanisms

**High-Performance Computing:**
- Intelligent optimization backend with graceful fallbacks: JAX → Numba → NumPy
- GPU acceleration support where available
- Optimized implementations for large-scale analysis

**Comprehensive Benchmarking:**
- End-to-end benchmarking scripts with statistical analysis
- Confidence intervals, significance tests, and effect size calculations
- Performance leaderboards and comparative analysis tools

## 🔧 Quick Start

### Basic Usage

```python
from lrdbenchmark.analysis.temporal.rs.rs_estimator_unified import RSEstimator
from lrdbenchmark.models.data_models.fbm.fbm_model import FractionalBrownianMotion

# Generate synthetic fractional Brownian motion
fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)
x = fbm.generate(n=1000, seed=42)

# Estimate Hurst parameter using R/S analysis
estimator = RSEstimator()
result = estimator.estimate(x)
print(f"Estimated H: {result['hurst_parameter']:.3f}")  # ~0.7
```

### Advanced Benchmarking

```python
from lrdbenchmark.analysis.benchmark import ComprehensiveBenchmark

# Run comprehensive benchmark across multiple estimators
benchmark = ComprehensiveBenchmark()
results = benchmark.run_classical_estimators(
    data_models=['fbm', 'fgn', 'arfima'],
    n_samples=1000,
    n_trials=100
)
benchmark.generate_leaderboard(results)
```

### Heavy-Tail Robustness Analysis

```python
from lrdbenchmark.models.data_models.alpha_stable.alpha_stable_model import AlphaStableModel
from lrdbenchmark.robustness.adaptive_preprocessor import AdaptivePreprocessor

# Generate heavy-tailed α-stable process
alpha_stable = AlphaStableModel(alpha=1.5, beta=0.0, scale=1.0)
x = alpha_stable.generate(n=1000, seed=42)

# Apply adaptive preprocessing for robust estimation
preprocessor = AdaptivePreprocessor()
x_processed = preprocessor.preprocess(x, method='auto')

# Estimate with robust preprocessing
estimator = RSEstimator()
result = estimator.estimate(x_processed)
```

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install lrdbenchmark
```

### Development Installation

```bash
git clone https://github.com/dave2k77/LRDBenchmark.git
cd LRDBenchmark
pip install -e .
```

### Optional Dependencies

For enhanced performance and additional features:

```bash
# GPU acceleration (JAX)
pip install "lrdbenchmark[jax]"

# Documentation building
pip install "lrdbenchmark[docs]"

# Development tools
pip install "lrdbenchmark[dev]"
```

## 📚 Documentation

- **📖 Full Documentation**: [https://lrdbenchmark.readthedocs.io/](https://lrdbenchmark.readthedocs.io/)
- **🚀 Quick Start Guide**: [`docs/quickstart.rst`](docs/quickstart.rst)
- **💡 Examples**: [`docs/examples/`](docs/examples/) and [`examples/`](examples/)
- **🔧 API Reference**: [API Documentation](https://lrdbenchmark.readthedocs.io/en/latest/api/)

## 🏗️ Project Structure

```
LRDBenchmark/
├── lrdbenchmark/           # Main package
│   ├── analysis/           # Estimator implementations
│   ├── models/            # Data generation models
│   ├── analytics/         # Performance monitoring
│   └── robustness/        # Heavy-tail robustness tools
├── scripts/               # Benchmarking and analysis scripts
├── examples/              # Usage examples
├── docs/                  # Documentation
├── tests/                 # Test suite
├── tools/                 # Development utilities
└── config/                # Configuration files
```

## 🏆 Performance Leaderboard

Our comprehensive benchmark evaluated 15 estimators across 920 test cases. Here are the top performers:

| Rank | Estimator | Category | Overall Score | MAE | Robustness |
|------|-----------|----------|---------------|-----|------------|
| 1 | **LSTM** | Neural Network | **9.68/10** | **0.097** | 1.00 |
| 2 | **CNN** | Neural Network | **9.66/10** | **0.103** | 1.00 |
| 3 | **Transformer** | Neural Network | **9.65/10** | **0.106** | 1.00 |
| 4 | **GRU** | Neural Network | **9.64/10** | **0.108** | 1.00 |
| 5 | **R/S** | Classical | **9.51/10** | **0.099** | 1.00 |
| 6 | **Higuchi** | Classical | **9.41/10** | **0.118** | 1.00 |

**Category Averages:**
- **Neural Networks**: 9.66/10 (Tier 1)
- **Machine Learning**: 9.34/10 (Tier 2)  
- **Classical**: 8.65/10 (Tiers 2-4)

## 🛠️ Available Estimators

### Classical Methods
- **R/S Analysis** - Rescaled Range analysis (9.51/10)
- **DFA** - Detrended Fluctuation Analysis (7.67/10)
- **DMA** - Detrended Moving Average (7.36/10)
- **Higuchi** - Higuchi's fractal dimension method (9.41/10)
- **Periodogram** - Periodogram-based estimation (8.97/10)
- **GPH** - Geweke and Porter-Hudak estimator (8.63/10)
- **Whittle** - Whittle maximum likelihood (9.00/10)
- **CWT** - Continuous Wavelet Transform (8.65/10)
- **GHE** - Generalized Hurst Exponent

### Machine Learning
- **Random Forest** - Ensemble tree-based estimation (9.33/10)
- **Support Vector Regression** - SVM-based estimation (9.33/10)
- **Gradient Boosting** - Boosted tree estimation (9.36/10)

### Neural Networks
- **LSTM** - Long Short-Term Memory networks (9.68/10)
- **GRU** - Gated Recurrent Units (9.64/10)
- **CNN** - Convolutional Neural Networks (9.66/10)
- **Transformer** - Attention-based architectures (9.65/10)

## 🧪 Testing

Run the test suite:

```bash
# Basic tests
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=lrdbenchmark --cov-report=html
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python scientific computing stack
- Leverages JAX for high-performance computing
- Inspired by the need for reproducible LRD analysis
- Community-driven development and validation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dave2k77/LRDBenchmark/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dave2k77/LRDBenchmark/discussions)
- **Documentation**: [ReadTheDocs](https://lrdbenchmark.readthedocs.io/)

---

**Made with ❤️ for the time series analysis community**









