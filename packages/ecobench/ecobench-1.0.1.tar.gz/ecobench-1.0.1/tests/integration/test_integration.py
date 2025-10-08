"""
Integration tests for the Ecobench library.
"""

import pytest
from ecobench import Tracker, Model, Visualizer


class TestIntegration:
    """Integration test cases."""
    
    def test_full_workflow(self):
        """Test complete workflow from initialization to visualization."""
        # Initialize tracker
        tracker = Tracker("GPT-4o")
        
        # Simulate multiple API calls
        for i in range(5):
            tracker.update_state(
                input_tokens=100 + i*10,
                output_tokens=50 + i*5,
                cached_tokens=i*2
            )
        
        # Get summary
        summary = tracker.get_summary()
        assert summary['total_input_tokens'] > 0
        assert summary['total_output_tokens'] > 0
        assert summary['total_cost'] > 0
        
        # Test visualization
        visualizer = Visualizer()
        # This would test visualization functionality if implemented
        assert visualizer is not None
    
    def test_model_comparison(self):
        """Test comparing different models."""
        tracker1 = Tracker("GPT-4o")
        tracker2 = Tracker("GPT-4o-mini")
        
        # Same usage for both
        result1 = tracker1.update_state(input_tokens=1000, output_tokens=500)
        result2 = tracker2.update_state(input_tokens=1000, output_tokens=500)
        
        # GPT-4o should be more expensive
        assert result1['cost'] > result2['cost']
    
    def test_custom_model_workflow(self):
        """Test workflow with custom model."""
        custom_model = Model(
            name="Custom Test Model",
            d_model=2048,
            d_ff=4096,
            layers=24,
            num_query_heads=32,
            cost_per_input_token=0.0005/1000,
            cost_per_output_token=0.001/1000
        )
        
        tracker = Tracker(custom_model=custom_model)
        result = tracker.update_state(input_tokens=500, output_tokens=250)
        
        assert result['cost'] > 0
        assert tracker.model == custom_model
