"""
Ecobench: A Python library for tracking LLM usage, costs, and environmental impact.

This library provides easy-to-use tools for monitoring your LLM API usage,
calculating costs, and tracking environmental impact including energy consumption
and water usage.

Main Components:
- Tracker: Main class for tracking usage
- Model: Model architecture and cost calculation
- Predefined models: GPT-4o, GPT-4o-mini, o3-mini, Mixtral-8x22B

Quick Start:
    from ecobench import Tracker
    
    # Initialize tracker
    tracker = Tracker("GPT-4o")
    
    # Track usage
    tracker.update_state(input_tokens=100, output_tokens=50, cached_tokens=20)
    
    # Get summary
    tracker.print_summary()
"""

from .tracker import Tracker, create_tracker, create_custom_tracker
from .model import Model
from .models import MODEL_REGISTRY, GPT_4o, GPT_4o_mini, o3_mini, Mixtral_8x22B
from .visualizer import Visualizer, create_visualizer, compare_trackers

__version__ = "1.0.0"
__author__ = "Ecobench Team"

__all__ = [
    "Tracker",
    "create_tracker", 
    "create_custom_tracker",
    "Model",
    "MODEL_REGISTRY",
    "GPT_4o",
    "GPT_4o_mini", 
    "o3_mini",
    "Mixtral_8x22B",
    "Visualizer",
    "create_visualizer",
    "compare_trackers"
]
