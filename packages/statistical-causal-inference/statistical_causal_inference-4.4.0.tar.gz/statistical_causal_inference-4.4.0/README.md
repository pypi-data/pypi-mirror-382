# Statistical Causal Inference

Production-ready causal attribution and inference algorithms for high-performance applications.

## Overview

This package provides the core algorithms and statistical methods for causal inference, used by the CausalMMA SDK and other applications.

## Features

- **Statistical Causal Inference**: Advanced algorithms for causal effect estimation
- **Causal Discovery**: PC Algorithm, FCI, and other structure learning methods
- **Optimized Performance**: Vectorized operations with NumPy and Numba acceleration
- **Async Processing**: Efficient asynchronous computation with Dask
- **LLM Integration**: OpenAI integration for causal reasoning
- **Production Ready**: Comprehensive error handling and validation

## Installation

```bash
pip install statistical-causal-inference
```

### From source

```bash
git clone https://github.com/rdmurugan/statistical-causal-inference.git
cd statistical-causal-inference
pip install -e .
```

## Usage

```python
from causalinference.core.statistical_inference import StatisticalCausalInference, CausalMethod
from causalinference.core.statistical_methods import PCAlgorithm
import pandas as pd

# Statistical causal inference
sci = StatisticalCausalInference()
result = sci.estimate_causal_effect(
    data=df,
    treatment='treatment_column',
    outcome='outcome_column',
    method=CausalMethod.DOUBLY_ROBUST
)

# Causal discovery
pc = PCAlgorithm()
dag = pc.learn_structure(data=df)
```

## Core Modules

- `statistical_inference.py` - Causal effect estimation methods
- `statistical_methods.py` - PC Algorithm and other statistical methods
- `causal_discovery.py` - Structure learning algorithms
- `optimized_algorithms.py` - Performance-optimized implementations
- `async_processing.py` - Asynchronous computation utilities
- `llm_client.py` - LLM integration for causal reasoning

## Requirements

- Python >= 3.9
- NumPy >= 1.21.0
- Pandas >= 1.3.0
- Scikit-learn >= 1.0.0
- NetworkX >= 2.6.0
- SciPy >= 1.7.0

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black causalinference/
```

## License

Proprietary - For use in CausalMMA projects

## Contact

For questions or support, contact: durai@infinidatum.net

## Version

Current version: 4.4.0
