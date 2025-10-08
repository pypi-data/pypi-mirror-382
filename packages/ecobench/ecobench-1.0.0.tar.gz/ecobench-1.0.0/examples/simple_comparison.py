"""
Simple model comparison example using the Ecobench library.
"""

from ecobench import Tracker

def simple_comparison():
    """Simple comparison between models."""
    print("🚀 Simple Model Comparison")
    print("=" * 40)
    
    # Test different models
    models = ["GPT-4o", "GPT-4o-mini", "o3-mini"]
    
    for model_name in models:
        print(f"\n📊 Testing {model_name}:")
        tracker = Tracker(model_name)
        
        # Simulate a conversation
        for i in range(5):
            input_tokens = 50 + i * 20  # Growing context
            output_tokens = 100
            
            result = tracker.update_state(
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            print(f"  Message {i+1}: ${result['cost']:.4f} | {result['energy_wh']:.2f} Wh")
        
        # Show summary
        summary = tracker.get_summary()
        print(f"  Total: ${summary['total_cost_usd']:.4f} | {summary['total_energy_wh']:.2f} Wh")

if __name__ == "__main__":
    simple_comparison()
