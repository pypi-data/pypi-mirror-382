# Energy Cost Calculation for Large Language Models

This document explains how energy consumption is calculated for Large Language Model (LLM) inference in the LLM-BENCH framework.

## Overview

The energy cost calculation estimates the power consumption in Watt-hours (Wh) for processing input and output tokens during LLM inference. The calculation considers two distinct phases of inference:

1. **Prefill Phase**: Processing the initial input prompt
2. **Decoding Phase**: Generating output tokens one by one

## Calculation Methodology

### 1. FLOP Computation

The energy calculation starts by computing the number of Floating Point Operations (FLOPs) required for each phase using the `arithmetic_cost_flop()` method:

```python
prefill_cost_flop = self.arithmetic_cost_flop(input_len=0, batch_size=1, seq_len=input_len, count_masked_flop=True)
decoding_cost_flop = self.arithmetic_cost_flop(input_len=input_len, batch_size=1, seq_len=output_len)
```

#### FLOP Formula

The arithmetic cost function calculates FLOPs based on:

```
FLOPs = 2 × total_active_params × batch_size × seq_len + 
        4 × d_head × num_query_heads × layers × mean_input_len × batch_size × seq_len
```

Where:
- `total_active_params`: Number of active parameters in the model
- `d_head`: Dimension per attention head
- `num_query_heads`: Number of query attention heads
- `layers`: Number of transformer layers
- `mean_input_len`: Average input length (differs between prefill and decoding)

### 2. Hardware Specifications

The calculation assumes NVIDIA H100 GPU specifications:

| Parameter | Value | Description |
|-----------|-------|-------------|
| GPU Power Draw | 1500 W | Maximum power consumption per GPU |
| GPU FLOP/s | 1×10¹⁵ | Floating point operations per second |
| GPU Joules per FLOP | 1.5×10⁻¹² J | Energy per floating point operation |

### 3. Utilization Factors

Different utilization rates are applied for each phase based on empirical research:

#### Prefill Phase
- **Utilization**: 50%
- **Reasoning**: During prefill, the model processes the entire input sequence in parallel, achieving higher compute utilization
- **Reference**: Kamath et al. observed 70% utilization ([arXiv:2410.18038](https://arxiv.org/pdf/2410.18038v1))

#### Decoding Phase
- **Utilization**: 10%
- **Reasoning**: During autoregressive decoding, only one token is generated at a time, leading to lower compute utilization due to memory bandwidth limitations

### 4. Energy Conversion

The energy consumption in Watt-hours is calculated as:

```
Energy (Wh) = (1 / utilization_factor) × FLOPs × gpu_joules_per_flop / 3600
```

The division by 3600 converts from Joules to Watt-hours (1 Wh = 3600 J).

## Example Calculation

For an input length of 1000 tokens and output length of 500 tokens:

1. **Prefill FLOPs**: Calculate based on processing 1000 input tokens
2. **Decoding FLOPs**: Calculate based on generating 500 output tokens with 1000 tokens in context
3. **Prefill Energy**: `prefill_FLOPs × (1/0.5) × 1.5e-12 / 3600` Wh
4. **Decoding Energy**: `decoding_FLOPs × (1/0.1) × 1.5e-12 / 3600` Wh

## Key Assumptions and Limitations

### Assumptions
- Single GPU inference (H100)
- Batch size of 1
- 100% TDP (Thermal Design Power) during computation
- Linear scaling of energy with FLOPs

### Limitations
- Does not account for memory access energy
- Assumes constant power draw during computation
- Does not consider cooling or infrastructure overhead
- Utilization factors are approximations based on limited studies

## Research References

1. **GPU Power Consumption**: Patel et al. found ~100% TDP during prefill phase
   - [Microsoft Research Paper](https://www.microsoft.com/en-us/research/uploads/prod/2024/03/GPU_Power_ASPLOS_24.pdf)

2. **Compute Utilization**: Kamath et al. observed 70% utilization during prefill
   - [arXiv:2410.18038](https://arxiv.org/pdf/2410.18038v1)

## Usage

To calculate energy cost for a model:

```python
model = Model(name="example_model", ...)
model.calculate_energy_cost(input_len=1000, output_len=500)
```

This will output:
- FLOP count and energy consumption for prefill phase
- FLOP count and energy consumption for decoding phase
- Total energy consumption in Watt-hours

## Future Improvements

Potential enhancements to the energy model:
- Include memory access patterns and bandwidth limitations
- Account for different GPU architectures
- Add infrastructure and cooling overhead
- Incorporate dynamic voltage and frequency scaling effects
- Consider batch processing efficiency