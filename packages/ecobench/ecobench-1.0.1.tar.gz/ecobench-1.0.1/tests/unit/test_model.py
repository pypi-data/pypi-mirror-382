"""
Unit tests for the Model class.
"""

import pytest
from ecobench import Model


class TestModel:
    """Test cases for Model class."""
    
    def test_model_initialization(self):
        """Test basic model initialization."""
        model = Model(
            name="Test Model",
            d_model=1024,
            d_ff=2048,
            layers=12,
            num_query_heads=16
        )
        
        assert model.name == "Test Model"
        assert model.d_model == 1024
        assert model.d_ff == 2048
        assert model.layers == 12
        assert model.num_query_heads == 16
    
    def test_model_parameter_calculation(self):
        """Test that model parameters are calculated correctly."""
        model = Model(
            d_model=1024,
            d_ff=2048,
            layers=12,
            num_query_heads=16
        )
        
        assert model.total_params > 0
        assert model.total_attn_params > 0
        assert model.total_ff_params > 0
    
    def test_cost_calculation(self):
        """Test cost calculation methods."""
        model = Model(
            cost_per_input_token=0.001/1000,
            cost_per_output_token=0.002/1000,
            cost_per_cache_token=0.0005/1000
        )
        
        input_cost = model.calculate_input_cost(1000)
        output_cost = model.calculate_output_cost(500)
        cache_cost = model.calculate_cache_cost(200)
        
        assert input_cost > 0
        assert output_cost > 0
        assert cache_cost > 0
    
    def test_energy_calculation(self):
        """Test energy calculation methods."""
        model = Model(
            d_model=1024,
            d_ff=2048,
            layers=12
        )
        
        energy = model.calculate_energy_consumption(1000, 500, 200)
        assert energy > 0
