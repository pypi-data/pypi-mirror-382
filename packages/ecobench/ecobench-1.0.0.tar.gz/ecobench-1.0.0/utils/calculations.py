"""
Calculation utilities for energy, water, and carbon footprint calculations.
"""

from typing import Dict, Any

def calculate_energy_cost_detailed(
    input_len: int,
    output_len: int,
    model_params: Dict[str, Any],
    batch_size: int = 1,
    use_cot_reasoning: bool = False
) -> float:
    """
    Calculate a more accurate energy cost in Wh for processing input and output tokens,
    modeling prefill as compute-bound and decoding as memory-bound.
    
    Args:
        input_len: Length of input sequence
        output_len: Length of output sequence
        model_params: Model parameters dictionary
        batch_size: The batch size for the inference calculation
        use_cot_reasoning: Whether to apply chain of thought token multiplier
        
    Returns:
        Energy consumption in Wh
    """
    # --- 1. Hardware & Infrastructure Constants (NVIDIA H100 SXM) ---
    h100_tdp_watts = 700.0
    prefill_avg_power_watts = h100_tdp_watts * 0.90  # Prefill is compute-bound, runs close to TDP
    decoding_avg_power_watts = h100_tdp_watts * 0.60  # Decoding is memory-bound, running at lower power (~420W)
    
    # Performance specs (assuming FP16/BF16 precision)
    h100_peak_flops_per_second = 1e15  # ~1 PFLOP/s for dense FP16
    h100_peak_mem_bw_bytes_per_second = 3.35e12  # ~3.35 TB/s

    # PUE (Power Usage Effectiveness) for data center overhead (cooling, etc.)
    power_usage_effectiveness = 1.2 

    # --- 2. Utilization Factors ---
    # Realistic sustained utilization of peak theoretical performance
    prefill_compute_utilization = 0.6  # 60% of peak FLOP/s
    decoding_mem_bw_utilization = 0.7  # 70% of peak memory bandwidth

    # --- 3. Prefill Phase Calculation (Compute-Bound) ---
    prefill_flops = _calculate_arithmetic_cost_flop(
        input_len=0, 
        batch_size=batch_size, 
        seq_len=input_len, 
        model_params=model_params,
        count_masked_flop=True
    )
    effective_prefill_flops = h100_peak_flops_per_second * prefill_compute_utilization
    
    prefill_time_seconds = prefill_flops / effective_prefill_flops
    prefill_energy_joules = prefill_time_seconds * prefill_avg_power_watts

    # --- 4. Decoding Phase Calculation (Memory-Bound) ---
    # The bottleneck for decoding is moving the model weights from HBM to compute cores
    # for every single token generated.
    bytes_to_move_per_token = model_params['total_active_params'] * model_params['weight_precision_bytes']
    
    # Apply CoT multiplier to output length if using chain of thought reasoning
    if use_cot_reasoning and model_params.get('uses_chain_of_thought', False):
        effective_output_len = output_len * model_params.get('cot_token_multiplier', 1.0)
    else:
        effective_output_len = output_len
    
    # With batching, this memory cost is amortized across the batch.
    # We read the weights once and use them for all items in the batch.
    total_bytes_for_decoding = (bytes_to_move_per_token / batch_size) * effective_output_len
    
    effective_mem_bw = h100_peak_mem_bw_bytes_per_second * decoding_mem_bw_utilization
    decoding_time_seconds = total_bytes_for_decoding / effective_mem_bw
    decoding_energy_joules = decoding_time_seconds * decoding_avg_power_watts
    
    # --- 5. Total Energy & Conversion ---
    # Total energy consumed by the GPU itself
    total_gpu_energy_joules = prefill_energy_joules + decoding_energy_joules
    
    # Total energy including datacenter overhead
    total_facility_energy_joules = total_gpu_energy_joules * power_usage_effectiveness
    
    # Convert Joules to Watt-hours (1 Wh = 3600 J)
    joules_to_wh = 1.0 / 3600.0
    total_energy_wh = total_facility_energy_joules * joules_to_wh

    return total_energy_wh


def calculate_water_usage_detailed(
    input_len: int,
    output_len: int,
    model_params: Dict[str, Any],
    use_cot_reasoning: bool = False
) -> tuple[float, float]:
    """
    Calculate the water usage in liters for processing input and output tokens.

    Args:
        input_len: Length of input sequence
        output_len: Length of output sequence
        model_params: Model parameters dictionary
        use_cot_reasoning: Whether to apply chain of thought token multiplier
        
    Returns:
        Tuple of (energy_wh, water_liters)
    """
    prefill_cost_flop = _calculate_arithmetic_cost_flop(
        input_len=0, 
        batch_size=1, 
        seq_len=input_len, 
        model_params=model_params,
        count_masked_flop=True
    )
    
    # Apply CoT multiplier to output length if using chain of thought reasoning
    if use_cot_reasoning and model_params.get('uses_chain_of_thought', False):
        effective_output_len = output_len * model_params.get('cot_token_multiplier', 1.0)
    else:
        effective_output_len = output_len
        
    decoding_cost_flop = _calculate_arithmetic_cost_flop(
        input_len=input_len, 
        batch_size=1, 
        seq_len=effective_output_len,
        model_params=model_params
    )

    # assume 50% compute utilization during prefill. Kamath et. al. observed 70%: https://arxiv.org/pdf/2410.18038v1
    prefill_utilization = 0.5
    decoding_utilization = 0.1

    # H100 server consuming up to 1500 W per GPU.
    # Patel found ~100% TDP during prefill: https://www.microsoft.com/en-us/research/uploads/prod/2024/03/GPU_Power_ASPLOS_24.pdf
    gpu_power_draw_watts = 1500
    gpu_flop_per_second = 1e15

    gpu_joules_per_flop = gpu_power_draw_watts/gpu_flop_per_second

    # Water usage in liters per kWh
    # From https://www.epa.gov/waterdata/estimated-water-use-data-and-tools
    water_usage_liters_per_kwh = 1.8

    total_energy_wh = (1/prefill_utilization) * prefill_cost_flop*gpu_joules_per_flop/3600 + (1/decoding_utilization) * decoding_cost_flop*gpu_joules_per_flop/3600
    total_water_liters = total_energy_wh * water_usage_liters_per_kwh

    return total_energy_wh, total_water_liters


def calculate_moe_inference_cost(
    input_len: int,
    output_len: int,
    model_params: Dict[str, Any],
    batch_size: int = 1,
    use_cot_reasoning: bool = False
) -> Dict[str, Any]:
    """
    Calculate MoE-specific inference costs accounting for routing overhead and memory requirements.
    
    Args:
        input_len: Length of input sequence
        output_len: Length of output sequence
        model_params: Model parameters dictionary
        batch_size: Batch size for inference
        use_cot_reasoning: Whether to apply chain of thought token multiplier
    
    Returns:
        Dictionary containing various cost metrics
    """
    # Base computation cost (same as dense model)
    base_flops = _calculate_arithmetic_cost_flop(
        input_len=0, 
        batch_size=batch_size, 
        seq_len=input_len + output_len, 
        model_params=model_params,
        count_masked_flop=True
    )
    
    # MoE-specific overheads
    routing_overhead = base_flops * (model_params.get('routing_overhead_factor', 1.0) - 1.0)  # Additional FLOPs for routing
    memory_overhead = model_params['total_ff_params'] * model_params['weight_precision_bytes'] * model_params.get('memory_bandwidth_factor', 1.0)  # Memory bandwidth cost
    
    # Total computation with MoE overhead
    total_flops = base_flops + routing_overhead
    
    # Apply CoT multiplier if needed
    if use_cot_reasoning and model_params.get('uses_chain_of_thought', False):
        effective_output_len = output_len * model_params.get('cot_token_multiplier', 1.0)
        total_flops *= model_params.get('cot_token_multiplier', 1.0)
    
    # Memory requirements (all experts must be loaded)
    total_memory_bytes = model_params['total_params'] * model_params['weight_precision_bytes']
    
    # Active memory (only active experts during computation)
    active_memory_bytes = model_params['total_active_params'] * model_params['weight_precision_bytes']
    
    return {
        'total_flops': total_flops,
        'routing_overhead': routing_overhead,
        'memory_overhead': memory_overhead,
        'total_memory_bytes': total_memory_bytes,
        'active_memory_bytes': active_memory_bytes,
        'sparsity_efficiency': model_params.get('sparsity_factor', 1.0),
        'is_moe': model_params.get('n_experts', 1) > 1
    }


def _calculate_arithmetic_cost_flop(
    input_len: int,
    batch_size: int,
    seq_len: int,
    model_params: Dict[str, Any],
    count_masked_flop: bool = False
) -> float:
    """
    Calculate arithmetic cost in FLOPs for a given sequence length and batch size.
    
    Args:
        input_len: Input sequence length
        batch_size: Batch size
        seq_len: Sequence length
        model_params: Model parameters dictionary
        count_masked_flop: Whether to count masked FLOPs
        
    Returns:
        Arithmetic cost in FLOPs
    """
    if count_masked_flop:
        mean_input_len = input_len + seq_len
    else:
        mean_input_len = (input_len + (input_len + seq_len - 1))/2

    # find cost to process prefill or decoding
    # this scales quadratically with seq_len because mean_input_len is proportion to seq_len
    return (2*model_params['total_active_params']*batch_size*seq_len + 
            4*model_params['d_head']*model_params['num_query_heads']*model_params['layers']*mean_input_len*batch_size*seq_len)


