"""
LLM Usage Tracker Library

A simple library for tracking LLM usage, costs, and environmental impact.
"""

from typing import Optional, Dict, Any
from .model import Model
from .models import MODEL_REGISTRY


class Tracker:
    """
    A tracker for monitoring LLM usage, costs, and environmental impact.
    
    Usage:
        tracker = Tracker(model_name="GPT-4o")
        tracker.update_state(input_tokens=100, output_tokens=50, cached_tokens=20)
    """
    
    def __init__(self, model_name: str = "GPT-4o", custom_model: Optional[Model] = None):
        """
        Initialize the LLM tracker with a specific model.
        
        Args:
            model_name (str): Name of the model to use. Options: "GPT-4o", "GPT-4o-mini", "o3-mini", "Mixtral-8x22B"
            custom_model (Model, optional): Custom model instance to use instead of predefined models
        """
        self.model_name = model_name
        
        # Per-message tracking lists
        self.costs_per_message = []
        self.energy_per_message = []
        self.water_per_message = []
        self.input_tokens_per_message = []
        self.output_tokens_per_message = []
        self.cached_tokens_per_message = []
        
        # Keep totals for backward compatibility
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_tokens = 0
        self.total_cost = 0.0
        self.total_energy_wh = 0.0
        self.total_water_liters = 0.0
        self.usage_history = []
        
        # Initialize model
        if custom_model is not None:
            self.model = custom_model
        else:
            self.model = self._get_model_by_name(model_name)
    
    def _get_model_by_name(self, model_name: str) -> Model:
        """Get model instance by name."""
        if model_name not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {model_name}. Available models: {list(MODEL_REGISTRY.keys())}")
        
        return MODEL_REGISTRY[model_name]
    
    def update_state(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0, 
                    use_cot_reasoning: bool = False, cache_percent: float = None) -> Dict[str, Any]:
        """
        Update the tracker state with new token usage.
        
        Args:
            input_tokens (int): Number of input tokens
            output_tokens (int): Number of output tokens
            cached_tokens (int): Number of cached tokens (optional)
            use_cot_reasoning (bool): Whether to apply chain of thought token multiplier
            cache_percent (float): Percentage of input tokens that are cached (0.0 to 1.0)
        
        Returns:
            dict: Dictionary containing cost and usage information for this update
        """
        # Calculate cache percentage if not provided
        if cache_percent is None and cached_tokens > 0:
            cache_percent = cached_tokens / input_tokens if input_tokens > 0 else 0.0
        elif cache_percent is None:
            cache_percent = 0.0
        
        # Calculate costs for this update
        cost = self.model.price(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_percent=cache_percent,
            use_cot_reasoning=use_cot_reasoning
        )
        
        # Calculate energy cost
        energy_wh = self.model.calculate_energy_cost(
            input_len=input_tokens,
            output_len=output_tokens,
            use_cot_reasoning=use_cot_reasoning
        )
        
        # Calculate water usage
        energy_wh_water, water_liters = self.model.calculate_water_usage(
            input_len=input_tokens,
            output_len=output_tokens,
            use_cot_reasoning=use_cot_reasoning
        )
        
        # Store per-message values
        self.costs_per_message.append(cost)
        self.energy_per_message.append(energy_wh)
        self.water_per_message.append(water_liters)
        self.input_tokens_per_message.append(input_tokens)
        self.output_tokens_per_message.append(output_tokens)
        self.cached_tokens_per_message.append(cached_tokens)
        
        # Update totals
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cached_tokens += cached_tokens
        self.total_cost += cost
        self.total_energy_wh += energy_wh
        self.total_water_liters += water_liters
        
        # Store this update in history
        update_info = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cached_tokens': cached_tokens,
            'cost': cost,
            'energy_wh': energy_wh,
            'water_liters': water_liters,
            'use_cot_reasoning': use_cot_reasoning,
            'cache_percent': cache_percent
        }
        self.usage_history.append(update_info)
        
        return update_info
    
    def get_costs_per_message(self) -> list:
        """Get list of costs for each message."""
        return self.costs_per_message.copy()
    
    def get_energy_per_message(self) -> list:
        """Get list of energy usage for each message."""
        return self.energy_per_message.copy()
    
    def get_water_per_message(self) -> list:
        """Get list of water usage for each message."""
        return self.water_per_message.copy()
    
    def get_tokens_per_message(self) -> Dict[str, list]:
        """Get lists of token usage for each message."""
        return {
            'input_tokens': self.input_tokens_per_message.copy(),
            'output_tokens': self.output_tokens_per_message.copy(),
            'cached_tokens': self.cached_tokens_per_message.copy()
        }
    
    def get_cumulative_costs(self) -> list:
        """Get cumulative costs (running total)."""
        cumulative = []
        total = 0.0
        for cost in self.costs_per_message:
            total += cost
            cumulative.append(total)
        return cumulative
    
    def get_cumulative_energy(self) -> list:
        """Get cumulative energy usage (running total)."""
        cumulative = []
        total = 0.0
        for energy in self.energy_per_message:
            total += energy
            cumulative.append(total)
        return cumulative
    
    def get_cumulative_water(self) -> list:
        """Get cumulative water usage (running total)."""
        cumulative = []
        total = 0.0
        for water in self.water_per_message:
            total += water
            cumulative.append(total)
        return cumulative
    
    def get_total_cost(self) -> float:
        """Get total cost (last value in cumulative costs)."""
        return self.total_cost
    
    def get_total_energy(self) -> float:
        """Get total energy usage (last value in cumulative energy)."""
        return self.total_energy_wh
    
    def get_total_water(self) -> float:
        """Get total water usage (last value in cumulative water)."""
        return self.total_water_liters
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all tracked usage.
        
        Returns:
            dict: Summary of total usage, costs, and environmental impact
        """
        return {
            'model_name': self.model_name,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_cached_tokens': self.total_cached_tokens,
            'total_cost_usd': self.total_cost,
            'total_energy_wh': self.total_energy_wh,
            'total_water_liters': self.total_water_liters,
            'total_updates': len(self.usage_history),
            'average_cost_per_input_token': self.total_cost / self.total_input_tokens if self.total_input_tokens > 0 else 0,
            'average_cost_per_output_token': self.total_cost / self.total_output_tokens if self.total_output_tokens > 0 else 0
        }
    
    def reset(self):
        """Reset all tracking data."""
        # Clear per-message lists
        self.costs_per_message = []
        self.energy_per_message = []
        self.water_per_message = []
        self.input_tokens_per_message = []
        self.output_tokens_per_message = []
        self.cached_tokens_per_message = []
        
        # Reset totals
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_tokens = 0
        self.total_cost = 0.0
        self.total_energy_wh = 0.0
        self.total_water_liters = 0.0
        self.usage_history = []
    
    def print_summary(self):
        """Print a formatted summary of usage."""
        summary = self.get_summary()
        print(f"\n=== LLM Usage Summary for {summary['model_name']} ===")
        print(f"Total Input Tokens: {summary['total_input_tokens']:,}")
        print(f"Total Output Tokens: {summary['total_output_tokens']:,}")
        print(f"Total Cached Tokens: {summary['total_cached_tokens']:,}")
        print(f"Total Cost: ${summary['total_cost_usd']:.4f}")
        print(f"Total Energy: {summary['total_energy_wh']:.4f} Wh")
        print(f"Total Water Usage: {summary['total_water_liters']:.4f} liters")
        print(f"Total API Calls: {summary['total_updates']}")
        print(f"Avg Cost per Input Token: ${summary['average_cost_per_input_token']:.6f}")
        print(f"Avg Cost per Output Token: ${summary['average_cost_per_output_token']:.6f}")
        print("=" * 50)


# Convenience functions for easy initialization
def create_tracker(model_name: str = "GPT-4o") -> Tracker:
    """
    Create a new LLM tracker instance.
    
    Args:
        model_name (str): Name of the model to track
        
    Returns:
        Tracker: New tracker instance
    """
    return Tracker(model_name=model_name)


def create_custom_tracker(model: Model) -> Tracker:
    """
    Create a tracker with a custom model.
    
    Args:
        model (Model): Custom model instance
        
    Returns:
        Tracker: New tracker instance with custom model
    """
    return Tracker(custom_model=model)
