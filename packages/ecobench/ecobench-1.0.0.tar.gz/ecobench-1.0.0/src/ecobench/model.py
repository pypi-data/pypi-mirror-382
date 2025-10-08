
"""
Model architecture and cost calculation for LLM tracking.

This module provides the Model class for defining LLM architectures
and calculating costs, energy consumption, and environmental impact.
"""

import numpy as np
from typing import Optional, Tuple


class Model:
    """
    A model class for tracking LLM architecture and calculating costs.
    
    This class represents a transformer-based language model with support for
    various architectures including standard transformers, MoE models, and
    models with chain-of-thought reasoning.
    
    Attributes:
        name (str): Human-readable name of the model
        d_model (int): Hidden dimension size
        d_ff (int): Feedforward hidden dimension size
        layers (int): Number of transformer layers
        n_experts (int): Total number of experts (for MoE models)
        n_active_experts (int): Number of active experts per token
        num_query_heads (int): Number of query attention heads
        group_size (int): Group size for grouped attention
        weight_precision_bytes (int): Bytes per weight parameter
        activation_precision_bytes (int): Bytes per activation
        vocab_size (int): Vocabulary size
        cost_per_input_token (float): Cost per input token in dollars
        cost_per_output_token (float): Cost per output token in dollars
        cost_per_cache_token (float): Cost per cache token in dollars
        uses_chain_of_thought (bool): Whether model uses CoT reasoning
        cot_token_multiplier (float): Multiplier for output tokens due to CoT
    """
    
    def __init__(
        self,
        name: str = "None",
        d_model: int = 3 * 2**12,
        d_ff: int = 9 * 2**12,
        ff_matrix_count: Tuple[int, int] = (1, 1),
        layers: int = 120,
        n_experts: int = 1,
        n_active_experts: int = 1,
        num_query_heads: int = 128,
        group_size: int = 1,
        weight_precision_bytes: int = 2,
        activation_precision_bytes: int = 2,
        d_head: Optional[int] = None,
        vocab_size: int = 0,
        parallel_attention: bool = False,
        cost_per_input_token: float = 0.0,
        cost_per_output_token: float = 0.0,
        cost_per_cache_token: float = 0.0,
        uses_chain_of_thought: bool = False,
        cot_token_multiplier: float = 1.0,
        routing_overhead_factor: float = 1.0,
        memory_bandwidth_factor: float = 1.0,
    ):
        assert num_query_heads % group_size == 0

        # Variables directly set
        self.d_model = d_model # hidden size
        self.d_ff = d_ff # feedforward hidden size
        self.layers = layers # number of layers
        self.n_experts = n_experts # total number of experts
        self.n_active_experts = n_active_experts # number of active experts per token
        self.num_query_heads = num_query_heads # number of query attention heads
        self.group_size = group_size # group size for grouped attention
        self.weight_precision_bytes = weight_precision_bytes # bytes per weight
        self.activation_precision_bytes = activation_precision_bytes # bytes per activation
        self.vocab_size = vocab_size # vocabulary size
        self.ff_matrix_count = ff_matrix_count # tuple indicating number of feedforward matrices (e.g., (2,1) for SwiGLU) 
        self.parallel_attention = parallel_attention # whether key/value heads are parallel to query heads
        
        # Pricing
        self.cost_per_input_token = cost_per_input_token # cost in dollars per input token
        self.cost_per_output_token = cost_per_output_token # cost in dollars per output token
        self.cost_per_cache_token = cost_per_cache_token # cost in dollars per cache token
        
        # Chain of Thought reasoning parameters
        self.uses_chain_of_thought = uses_chain_of_thought # whether model uses CoT reasoning
        self.cot_token_multiplier = cot_token_multiplier # multiplier for output tokens due to CoT reasoning
        
        # MoE-specific parameters
        self.routing_overhead_factor = routing_overhead_factor # overhead from expert routing (1.0 = no overhead)
        self.memory_bandwidth_factor = memory_bandwidth_factor # memory bandwidth impact (1.0 = no impact)

        # Derived variables
        self.ff_params_per_layer_per_expert = sum(self.ff_matrix_count) * self.d_model * self.d_ff # parameters per feedforward layer per expert
        self.sparsity_factor = self.n_experts // self.n_active_experts if self.n_active_experts > 0 else 1 # sparsity factor
        self.total_ff_params = self.layers * self.n_experts * self.ff_params_per_layer_per_expert # total feedforward parameters
        self.num_kv_heads = 2 * self.num_query_heads / self.group_size # number of key/value heads
        self.d_head = d_head if d_head != None else self.d_model // self.num_query_heads # dimension per head
        self.d_all_attn_heads = (self.num_query_heads + self.num_kv_heads) * self.d_head # total dimension of all attention heads
        self.attn_params_per_layer = self.d_all_attn_heads * self.d_model + self.d_head*self.num_query_heads*self.d_model # parameters per attention layer

        self.embedding_params = self.vocab_size * self.d_model * 2 # embedding parameters (input and output embeddings)
        self.total_attn_params = self.layers * self.attn_params_per_layer # total attention parameters
        self.total_params = self.total_attn_params + self.total_ff_params + self.embedding_params # total parameters
        self.total_active_params = self.total_attn_params + self.total_ff_params//self.sparsity_factor + self.embedding_params # total active parameters

        self.kv_cache_size_per_input_bytes = self.num_kv_heads*self.d_head*self.layers*self.activation_precision_bytes # key/value cache size per input token in bytes

        self.name = name # model name

    def __repr__(self) -> str:
        """
        Return a string representation of the model.
        
        Returns:
            str: Formatted string with model details
        """
        representation = f"""Model Details:
        Name: {self.name}
        d_model: {self.d_model}
        d_ff: {self.d_ff}
        Depth: {self.layers}
        Total FF Params: {self.total_ff_params}
        Total Embedding Params: {self.embedding_params}
        Num Attention Heads: {self.num_query_heads}
        d_head: {self.d_head}
        Group size: {self.group_size}
        Total Attention Params: {self.total_attn_params}
        Total Params: {self.total_params}
        Total Active Params: {self.total_active_params}
        """
        return representation

    def arithmetic_cost_flop(
        self, 
        input_len: int, 
        batch_size: int, 
        seq_len: int = 1, 
        count_masked_flop: bool = False
    ) -> float:
        """
        Calculate the arithmetic cost in floating point operations.
        
        Args:
            input_len (int): Length of input sequence
            batch_size (int): Batch size
            seq_len (int): Sequence length for processing
            count_masked_flop (bool): Whether to count masked operations
            
        Returns:
            float: Total floating point operations
        """
        if count_masked_flop:
            mean_input_len = input_len + seq_len
        else:
            mean_input_len = (input_len + (input_len + seq_len - 1)) / 2

        # Find cost to process prefill or decoding
        # This scales quadratically with seq_len because mean_input_len is proportional to seq_len
        return (
            2 * self.total_active_params * batch_size * seq_len + 
            4 * self.d_head * self.num_query_heads * self.layers * 
            mean_input_len * batch_size * seq_len
        )

    def price(self, input_tokens, output_tokens, cache_percent=0.0, use_cot_reasoning=False):
        """
        Calculate the price for processing input and output tokens with cache percentage.
        
        Args:
            input_tokens (int): Number of input tokens
            output_tokens (int): Number of output tokens  
            cache_percent (float): Percentage of input tokens that are cached (0.0 to 1.0)
            use_cot_reasoning (bool): Whether to apply chain of thought token multiplier
        
        Returns:
            float: Total cost in dollars
        """
        effective_input_tokens = input_tokens * (1.0 - cache_percent)
        cache_tokens = input_tokens * cache_percent
        
        # Apply CoT multiplier to output tokens if using chain of thought reasoning
        if use_cot_reasoning and self.uses_chain_of_thought:
            effective_output_tokens = output_tokens * self.cot_token_multiplier
        else:
            effective_output_tokens = output_tokens
        
        input_cost = effective_input_tokens * self.cost_per_input_token
        output_cost = effective_output_tokens * self.cost_per_output_token
        cache_cost = cache_tokens * self.cost_per_cache_token if self.cost_per_cache_token is not None else 0.0

        return input_cost + output_cost + cache_cost

    def calculate_energy_cost(self, input_len, output_len, batch_size=1, use_cot_reasoning=False):
        """
        Calculate a more accurate energy cost in Wh for processing input and output tokens,
        modeling prefill as compute-bound and decoding as memory-bound.
        
        Args:
            input_len (int): Length of input sequence
            output_len (int): Length of output sequence
            batch_size (int): The batch size for the inference calculation.
            use_cot_reasoning (bool): Whether to apply chain of thought token multiplier
        """
        from utils.calculations import calculate_energy_cost_detailed
        
        model_params = self._get_model_params_dict()
        return calculate_energy_cost_detailed(
            input_len=input_len,
            output_len=output_len,
            model_params=model_params,
            batch_size=batch_size,
            use_cot_reasoning=use_cot_reasoning
        )

    def calculate_water_usage(self, input_len, output_len, use_cot_reasoning=False):
        """
        Calculate the water usage in liters for processing input and output tokens.

        Args:
            input_len (int): Length of input sequence
            output_len (int): Length of output sequence
            use_cot_reasoning (bool): Whether to apply chain of thought token multiplier
        """
        from utils.calculations import calculate_water_usage_detailed
        
        model_params = self._get_model_params_dict()
        return calculate_water_usage_detailed(
            input_len=input_len,
            output_len=output_len,
            model_params=model_params,
            use_cot_reasoning=use_cot_reasoning
        )

    def calculate_moe_inference_cost(self, input_len, output_len, batch_size=1, use_cot_reasoning=False):
        """
        Calculate MoE-specific inference costs accounting for routing overhead and memory requirements.
        
        Args:
            input_len (int): Length of input sequence
            output_len (int): Length of output sequence
            batch_size (int): Batch size for inference
            use_cot_reasoning (bool): Whether to apply chain of thought token multiplier
        
        Returns:
            dict: Dictionary containing various cost metrics
        """
        from utils.calculations import calculate_moe_inference_cost
        
        model_params = self._get_model_params_dict()
        return calculate_moe_inference_cost(
            input_len=input_len,
            output_len=output_len,
            model_params=model_params,
            batch_size=batch_size,
            use_cot_reasoning=use_cot_reasoning
        )
    
    def _get_model_params_dict(self):
        """
        Get model parameters as a dictionary for use with utility functions.
        
        Returns:
            dict: Dictionary containing all model parameters
        """
        return {
            'd_model': self.d_model,
            'd_ff': self.d_ff,
            'layers': self.layers,
            'n_experts': self.n_experts,
            'n_active_experts': self.n_active_experts,
            'num_query_heads': self.num_query_heads,
            'group_size': self.group_size,
            'weight_precision_bytes': self.weight_precision_bytes,
            'activation_precision_bytes': self.activation_precision_bytes,
            'vocab_size': self.vocab_size,
            'ff_matrix_count': self.ff_matrix_count,
            'parallel_attention': self.parallel_attention,
            'cost_per_input_token': self.cost_per_input_token,
            'cost_per_output_token': self.cost_per_output_token,
            'cost_per_cache_token': self.cost_per_cache_token,
            'uses_chain_of_thought': self.uses_chain_of_thought,
            'cot_token_multiplier': self.cot_token_multiplier,
            'routing_overhead_factor': self.routing_overhead_factor,
            'memory_bandwidth_factor': self.memory_bandwidth_factor,
            'ff_params_per_layer_per_expert': self.ff_params_per_layer_per_expert,
            'sparsity_factor': self.sparsity_factor,
            'total_ff_params': self.total_ff_params,
            'num_kv_heads': self.num_kv_heads,
            'd_head': self.d_head,
            'd_all_attn_heads': self.d_all_attn_heads,
            'attn_params_per_layer': self.attn_params_per_layer,
            'embedding_params': self.embedding_params,
            'total_attn_params': self.total_attn_params,
            'total_params': self.total_params,
            'total_active_params': self.total_active_params
        }


def scale_model(name, model: Model, scale_factor: float, depth_exponent=1/3, cost_per_input_token=0.0, cost_per_output_token=0.0, 
                 cost_per_cache_token=0.0, uses_chain_of_thought=False, cot_token_multiplier=1.0, routing_overhead_factor=None, memory_bandwidth_factor=None) -> Model:
    d_model = model.d_model * scale_factor**((1 - depth_exponent)/2)
    d_ff = model.d_ff * scale_factor**((1 - depth_exponent)/2)
    layers = int(model.layers * scale_factor**(depth_exponent))
    model.cost_per_input_token = cost_per_input_token
    model.cost_per_output_token = cost_per_output_token
    model.cost_per_cache_token = cost_per_cache_token

    

    num_query_heads = np.ceil(model.num_query_heads * scale_factor**((1 - depth_exponent)/4))
    num_groups = model.num_query_heads/model.group_size
    group_size = num_query_heads/num_groups

    return Model(name=name,
                 d_model=d_model,
                 d_ff=d_ff,
                 ff_matrix_count=model.ff_matrix_count,
                 layers=layers,
                 n_experts=model.n_experts,
                 n_active_experts=model.n_active_experts,
                 num_query_heads=num_query_heads,
                 group_size=group_size,
                 d_head=model.d_head * scale_factor**((1 - depth_exponent)/4),
                 weight_precision_bytes=model.weight_precision_bytes,
                 activation_precision_bytes=model.activation_precision_bytes,
                 vocab_size=model.vocab_size,
                 parallel_attention=model.parallel_attention,
                 cost_per_input_token=model.cost_per_input_token,
                 cost_per_output_token=model.cost_per_output_token,
                 cost_per_cache_token=model.cost_per_cache_token,
                 uses_chain_of_thought=uses_chain_of_thought,
                 cot_token_multiplier=cot_token_multiplier,
                 routing_overhead_factor=routing_overhead_factor if routing_overhead_factor is not None else model.routing_overhead_factor,
                 memory_bandwidth_factor=memory_bandwidth_factor if memory_bandwidth_factor is not None else model.memory_bandwidth_factor
                 )