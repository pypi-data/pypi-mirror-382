# Ecobench

[![PyPI version](https://badge.fury.io/py/ecobench.svg)](https://pypi.org/project/ecobench/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive Python library for tracking LLM usage, costs, and environmental impact. Monitor your AI model consumption with detailed analytics and environmental metrics.

## Features

- **Easy Integration**: Simple API for tracking LLM usage in your applications
- **Cost Tracking**: Monitor API costs with support for input, output, and cached tokens
- **Environmental Impact**: Track energy consumption and water usage
- **Multiple Models**: Built-in support for popular models (GPT-4o, GPT-4o-mini, o3-mini, Mixtral-8x22B)
- **Custom Models**: Support for custom model configurations
- **Chain of Thought**: Support for CoT reasoning with token multipliers

## Installation

### From PyPI (Recommended)

```bash
pip install ecobench
```

### From Source

```bash
git clone https://github.com/ecobench/ecobench.git
cd ecobench
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/ecobench/ecobench.git
cd ecobench
pip install -e ".[dev]"
```

## Quick Start

```python
from ecobench import Tracker

# Initialize tracker
tracker = Tracker("GPT-4o")

# Track usage
tracker.update_state(input_tokens=100, output_tokens=50, cached_tokens=20)

# Get summary
tracker.print_summary()
```

## Usage Examples

### Basic Usage

```python
from ecobench import Tracker

# Initialize tracker with GPT-4o
tracker = Tracker("GPT-4o")

# Track an API call
result = tracker.update_state(
    input_tokens=100,
    output_tokens=50,
    cached_tokens=20
)

print(f"Cost: ${result['cost']:.4f}")
print(f"Energy: {result['energy_wh']:.4f} Wh")
```

### Running Examples

The library includes several example scripts:

```bash
# Simple model comparison
python examples/simple_comparison.py

# Comprehensive visualization
python examples/visualize_model_comparison.py

# Notebook integration
python examples/notebook_integration.py
```

### Integration with Chat Applications

```python
class ChatApp:
    def __init__(self):
        self.tracker = Tracker("GPT-4o")
    
    def make_api_call(self, prompt, response, cached_tokens=0):
        # Estimate tokens (in practice, get from API response)
        input_tokens = len(prompt.split())
        output_tokens = len(response.split())
        
        # Track usage
        result = self.tracker.update_state(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens
        )
        
        return response, result
```

### Model Comparison

```python
# Compare different models
tracker_gpt4o = Tracker("GPT-4o")
tracker_mini = Tracker("GPT-4o-mini")

result_gpt4o = tracker_gpt4o.update_state(input_tokens=1000, output_tokens=500)
result_mini = tracker_mini.update_state(input_tokens=1000, output_tokens=500)

print(f"GPT-4o cost: ${result_gpt4o['cost']:.4f}")
print(f"GPT-4o-mini cost: ${result_mini['cost']:.4f}")
```

### Custom Models

```python
from ecobench import Model, Tracker

# Create custom model
custom_model = Model(
    name="Custom Model",
    d_model=4096,
    d_ff=11008,
    layers=32,
    num_query_heads=32,
    cost_per_input_token=0.001/1000,
    cost_per_output_token=0.002/1000,
    cost_per_cache_token=0.0005/1000
)

# Use with tracker
tracker = Tracker(custom_model=custom_model)
```

## Available Models

- **GPT-4o**: OpenAI's flagship model
- **GPT-4o-mini**: Smaller, faster version of GPT-4o
- **o3-mini**: OpenAI's reasoning model with CoT support
- **Mixtral-8x22B**: Open-source MoE model

## API Reference

### Tracker

#### `__init__(model_name: str = "GPT-4o", custom_model: Model = None)`
Initialize tracker with a model.

#### `update_state(input_tokens: int, output_tokens: int, cached_tokens: int = 0, use_cot_reasoning: bool = False, cache_percent: float = None) -> dict`
Update tracker with new usage data.

#### `get_summary() -> dict`
Get summary of all tracked usage.

#### `print_summary()`
Print formatted summary to console.

#### `reset()`
Reset all tracking data.

## Environmental Impact

The library tracks:
- **Energy Consumption**: In Watt-hours (Wh)
- **Water Usage**: In liters
- **Carbon Footprint**: Through energy calculations

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/ecobench.git`
3. Install in development mode: `pip install -e ".[dev]"`
4. Run tests: `pytest`
5. Run linting: `flake8 src/ tests/`
6. Format code: `black src/ tests/`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

## Support

- 📖 [Documentation](https://github.com/KnutOplandMoen/ecobench#readme)
- 🐛 [Bug Reports](https://github.com/KnutOplandMoen/ecobench/issues)
- 💬 [Discussions](https://github.com/KnutOplandMoen/ecobench/discussions)
- 📧 Email: knutomoe@stud.ntnu.no
