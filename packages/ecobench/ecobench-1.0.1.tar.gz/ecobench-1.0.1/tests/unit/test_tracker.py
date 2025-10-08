"""
Unit tests for the Tracker class.
"""

import pytest
from ecobench import Tracker, Model


class TestTracker:
    """Test cases for Tracker."""
    
    def test_initialization_with_model_name(self):
        """Test tracker initialization with model name."""
        tracker = Tracker("GPT-4o")
        assert tracker.model_name == "GPT-4o"
        assert tracker.total_input_tokens == 0
        assert tracker.total_output_tokens == 0
        assert tracker.total_cost == 0.0
    
    def test_initialization_with_custom_model(self):
        """Test tracker initialization with custom model."""
        custom_model = Model(
            name="Test Model",
            d_model=1024,
            d_ff=2048,
            layers=12,
            num_query_heads=16,
            cost_per_input_token=0.001/1000,
            cost_per_output_token=0.002/1000
        )
        tracker = Tracker(custom_model=custom_model)
        assert tracker.model == custom_model
    
    def test_update_state_basic(self):
        """Test basic state update."""
        tracker = Tracker("GPT-4o")
        result = tracker.update_state(input_tokens=100, output_tokens=50)
        
        assert result['input_tokens'] == 100
        assert result['output_tokens'] == 50
        assert result['cost'] > 0
        assert result['energy_wh'] > 0
        assert tracker.total_input_tokens == 100
        assert tracker.total_output_tokens == 50
    
    def test_update_state_with_cached_tokens(self):
        """Test state update with cached tokens."""
        tracker = Tracker("GPT-4o")
        result = tracker.update_state(
            input_tokens=100, 
            output_tokens=50, 
            cached_tokens=25
        )
        
        assert result['cached_tokens'] == 25
        assert tracker.total_cached_tokens == 25
    
    def test_reset(self):
        """Test tracker reset functionality."""
        tracker = Tracker("GPT-4o")
        tracker.update_state(input_tokens=100, output_tokens=50)
        
        assert tracker.total_input_tokens > 0
        tracker.reset()
        assert tracker.total_input_tokens == 0
        assert tracker.total_output_tokens == 0
        assert tracker.total_cost == 0.0
    
    def test_get_summary(self):
        """Test getting summary."""
        tracker = Tracker("GPT-4o")
        tracker.update_state(input_tokens=100, output_tokens=50)
        
        summary = tracker.get_summary()
        assert 'total_input_tokens' in summary
        assert 'total_output_tokens' in summary
        assert 'total_cost' in summary
        assert 'total_energy_wh' in summary
