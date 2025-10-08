# Ecobench Project Structure

This document describes the professional open source project structure for Ecobench.

## Directory Structure

```
ecobench/
├── src/                          # Source code directory
│   └── ecobench/                # Main package
│       ├── __init__.py          # Package initialization
│       ├── model.py             # Model architecture and calculations
│       ├── models.py            # Predefined model configurations
│       ├── tracker.py           # LLM usage tracking
│       └── visualizer.py        # Visualization utilities
├── utils/                       # Utility functions
│   ├── __init__.py              # Utils package initialization
│   ├── calculations.py          # Energy, water, carbon calculations
│   ├── formatters.py            # Display formatting utilities
│   └── validators.py            # Input validation utilities
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   │   ├── test_tracker.py      # Tracker unit tests
│   │   └── test_model.py        # Model unit tests
│   ├── integration/            # Integration tests
│   │   └── test_integration.py  # End-to-end tests
│   └── __init__.py              # Test package initialization
├── examples/                    # Usage examples
│   ├── example_usage.py         # Basic usage examples
│   ├── simple_comparison.py     # Model comparison examples
│   └── visualization_example.py # Visualization examples
├── docs/                        # Documentation
│   ├── PROJECT_STRUCTURE.md     # This file
│   ├── Chain_of_Thought_Considerations.md
│   └── Energy_calculation.md
├── notebooks/                   # Jupyter notebooks
│   └── single_model_analysis.ipynb
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup configuration
├── README.md                    # Project documentation
└── .gitignore                   # Git ignore rules
```

## Package Organization

### Core Package (`src/ecobench/`)
- **`__init__.py`**: Main package exports and version information
- **`model.py`**: Core Model class for architecture and calculations
- **`models.py`**: Predefined model configurations (GPT-4o, etc.)
- **`tracker.py`**: Tracker class for usage monitoring
- **`visualizer.py`**: Visualization and plotting utilities

### Utilities (`utils/`)
- **`calculations.py`**: Energy, water, and carbon footprint calculations
- **`formatters.py`**: Display formatting for costs, energy, water
- **`validators.py`**: Input validation and error checking

### Testing (`tests/`)
- **`unit/`**: Unit tests for individual components
- **`integration/`**: End-to-end integration tests
- Follows pytest conventions

### Examples (`examples/`)
- **`example_usage.py`**: Comprehensive usage examples
- **`simple_comparison.py`**: Model comparison examples
- **`visualization_example.py`**: Visualization examples

## Benefits of This Structure

1. **Professional Organization**: Follows Python packaging best practices
2. **Separation of Concerns**: Core logic, utilities, and tests are clearly separated
3. **Scalability**: Easy to add new features and modules
4. **Maintainability**: Clear structure makes code easier to maintain
5. **Testing**: Comprehensive test structure with unit and integration tests
6. **Documentation**: Dedicated docs directory with structured documentation

## Installation and Usage

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Run examples
python examples/example_usage.py
```

## Import Structure

```python
# Main package imports
from ecobench import Tracker, Model, Visualizer

# Utility imports (if needed)
from utils.calculations import calculate_energy_consumption
from utils.formatters import format_currency
from utils.validators import validate_tokens
```

This structure provides a solid foundation for a professional open source project that can grow and be maintained effectively.
