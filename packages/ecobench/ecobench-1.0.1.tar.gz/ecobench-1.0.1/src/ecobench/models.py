from .model import Model, scale_model

# Model registry for easy access
MODEL_REGISTRY = {}

# Mixtral 8x22B is an open-weight model with known architecture
Mixtral_8x22B = Model(name="Mixtral 8x22B",
                      d_model=6144,
                      d_ff=16384,
                      ff_matrix_count=(2, 1),
                      layers=56,
                      n_experts=8,
                      n_active_experts=2,
                      num_query_heads=48,
                      d_head=128,
                      group_size=6,
                      activation_precision_bytes=2,
                      weight_precision_bytes=2,
                      vocab_size=32000,
                      cost_per_input_token=0.0001,
                      cost_per_output_token=0.0002,
                      routing_overhead_factor=1.10,  # 10% overhead from expert routing
                      memory_bandwidth_factor=1.20   # 20% memory bandwidth impact
)

# GPT-4o is estimated to have around 200 billion parameters and is an MoE model.
# Scaling factor is calculated as (200B / 39B) ≈ 5.1
# GPT-4o is believed to have 16 experts with 2-4 active per token
GPT_4o = scale_model("GPT-4o", Mixtral_8x22B, scale_factor=5.1,
                    # Corrected pricing: $5.00/1M input, $15.00/1M output.
                    cost_per_input_token=5.0/1000000,
                    cost_per_output_token=15.0/1000000,
                    cost_per_cache_token=None, # Cache token cost is not typically specified in this format
                    routing_overhead_factor=1.15,  # 15% overhead from expert routing
                    memory_bandwidth_factor=1.25)  # 25% memory bandwidth impact from loading all experts

# GPT-4o-mini is estimated to have approximately 8 billion parameters.
# Scaling factor is calculated as (8B / 39B) ≈ 0.2
GPT_4o_mini = scale_model("GPT-4o-mini", Mixtral_8x22B, scale_factor=0.2,
                         # Correct pricing: $0.15/1M input, $0.60/1M output.
                         cost_per_input_token=0.15/1000000,
                         cost_per_output_token=0.6/1000000,
                         cost_per_cache_token=None)

# The parameter count for o3-mini is also not public.
# The scaling factor is a rough estimate based on its positioning as a capable but smaller model.
o3_mini = scale_model("o3-mini", Mixtral_8x22B, scale_factor=5.1, # Speculative scaling
                      # Corrected pricing: $1.10/1M input, $4.40/1M output.
                      cost_per_input_token=1.1/1000000,
                      cost_per_output_token=4.4/1000000,
                      cost_per_cache_token=0.55/1000000, 
                      uses_chain_of_thought=True,
                      cot_token_multiplier=2.0)

# Populate the model registry
MODEL_REGISTRY = {
    "GPT-4o": GPT_4o,
    "GPT-4o-mini": GPT_4o_mini,
    "o3-mini": o3_mini,
    "Mixtral-8x22B": Mixtral_8x22B
}
