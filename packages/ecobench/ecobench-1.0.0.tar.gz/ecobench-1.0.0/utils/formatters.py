"""
Formatting utilities for displaying results in a user-friendly way.
"""

from typing import Dict, Any


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    if amount < 0.01:
        return f"${amount:.6f} {currency}"
    elif amount < 1:
        return f"${amount:.4f} {currency}"
    else:
        return f"${amount:.2f} {currency}"


def format_energy(energy_wh: float) -> str:
    """
    Format energy consumption for display.
    
    Args:
        energy_wh: Energy in Watt-hours
        
    Returns:
        Formatted energy string
    """
    if energy_wh < 1:
        return f"{energy_wh:.4f} Wh"
    elif energy_wh < 1000:
        return f"{energy_wh:.2f} Wh"
    else:
        return f"{energy_wh/1000:.2f} kWh"


def format_water(water_liters: float) -> str:
    """
    Format water usage for display.
    
    Args:
        water_liters: Water usage in liters
        
    Returns:
        Formatted water string
    """
    if water_liters < 1:
        return f"{water_liters*1000:.2f} mL"
    elif water_liters < 1000:
        return f"{water_liters:.2f} L"
    else:
        return f"{water_liters/1000:.2f} kL"


def format_summary(summary: Dict[str, Any]) -> str:
    """
    Format a complete summary for display.
    
    Args:
        summary: Summary dictionary from tracker
        
    Returns:
        Formatted summary string
    """
    lines = [
        "=" * 50,
        "ECOBENCH USAGE SUMMARY",
        "=" * 50,
        f"Model: {summary.get('model_name', 'Unknown')}",
        f"Total Input Tokens: {summary.get('total_input_tokens', 0):,}",
        f"Total Output Tokens: {summary.get('total_output_tokens', 0):,}",
        f"Total Cached Tokens: {summary.get('total_cached_tokens', 0):,}",
        "",
        "COSTS:",
        f"  Total Cost: {format_currency(summary.get('total_cost', 0))}",
        "",
        "ENVIRONMENTAL IMPACT:",
        f"  Energy Consumption: {format_energy(summary.get('total_energy_wh', 0))}",
        f"  Water Usage: {format_water(summary.get('total_water_liters', 0))}",
        f"  Carbon Footprint: {summary.get('total_carbon_kg', 0):.4f} kg CO2",
        "",
        "PER MESSAGE AVERAGES:",
        f"  Messages Tracked: {len(summary.get('costs_per_message', []))}",
        f"  Avg Cost per Message: {format_currency(summary.get('avg_cost_per_message', 0))}",
        f"  Avg Energy per Message: {format_energy(summary.get('avg_energy_per_message', 0))}",
        "=" * 50
    ]
    
    return "\n".join(lines)
