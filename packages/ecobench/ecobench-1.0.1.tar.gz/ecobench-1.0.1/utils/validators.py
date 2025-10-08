"""
Validation utilities for input validation and error checking.
"""

from typing import Any, Dict, Optional


def validate_tokens(input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> None:
    """
    Validate token counts.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens  
        cached_tokens: Number of cached tokens
        
    Raises:
        ValueError: If token counts are invalid
    """
    if not isinstance(input_tokens, int) or input_tokens < 0:
        raise ValueError("input_tokens must be a non-negative integer")
    
    if not isinstance(output_tokens, int) or output_tokens < 0:
        raise ValueError("output_tokens must be a non-negative integer")
        
    if not isinstance(cached_tokens, int) or cached_tokens < 0:
        raise ValueError("cached_tokens must be a non-negative integer")


def validate_model_config(config: Dict[str, Any]) -> None:
    """
    Validate model configuration parameters.
    
    Args:
        config: Model configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_fields = ['d_model', 'd_ff', 'layers', 'num_query_heads']
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(config[field], (int, float)) or config[field] <= 0:
            raise ValueError(f"{field} must be a positive number")


def validate_tracker_input(
    input_tokens: int,
    output_tokens: int, 
    cached_tokens: int = 0,
    use_cot_reasoning: bool = False,
    cot_token_multiplier: float = 1.0
) -> None:
    """
    Validate tracker input parameters.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cached_tokens: Number of cached tokens
        use_cot_reasoning: Whether to use chain of thought reasoning
        cot_token_multiplier: Multiplier for CoT reasoning
        
    Raises:
        ValueError: If parameters are invalid
    """
    validate_tokens(input_tokens, output_tokens, cached_tokens)
    
    if not isinstance(use_cot_reasoning, bool):
        raise ValueError("use_cot_reasoning must be a boolean")
        
    if not isinstance(cot_token_multiplier, (int, float)) or cot_token_multiplier <= 0:
        raise ValueError("cot_token_multiplier must be a positive number")
