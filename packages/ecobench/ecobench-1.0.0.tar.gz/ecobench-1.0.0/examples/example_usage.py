"""
Example usage of the Ecobench library.

This file demonstrates how to use the library to track LLM usage,
costs, and environmental impact.
"""

from ecobench import Tracker, create_tracker, Model, GPT_4o, GPT_4o_mini


def basic_usage_example():
    """Basic usage example with GPT-4o."""
    print("=== Basic Usage Example ===")
    
    # Initialize tracker
    tracker = Tracker("GPT-4o")
    
    # Simulate some API calls
    print("Making API calls...")
    
    # First call: 100 input tokens, 50 output tokens
    result1 = tracker.update_state(input_tokens=100, output_tokens=50)
    print(f"Call 1 - Cost: ${result1['cost']:.4f}, Energy: {result1['energy_wh']:.4f} Wh")
    
    # Second call: 200 input tokens, 100 output tokens, 50 cached tokens
    result2 = tracker.update_state(input_tokens=200, output_tokens=100, cached_tokens=50)
    print(f"Call 2 - Cost: ${result2['cost']:.4f}, Energy: {result2['energy_wh']:.4f} Wh")
    
    # Third call with chain of thought reasoning
    result3 = tracker.update_state(input_tokens=150, output_tokens=75, use_cot_reasoning=True)
    print(f"Call 3 (CoT) - Cost: ${result3['cost']:.4f}, Energy: {result3['energy_wh']:.4f} Wh")
    
    # Print summary
    tracker.print_summary()


def comparison_example():
    """Compare different models."""
    print("\n=== Model Comparison Example ===")
    
    # Test with GPT-4o
    tracker_gpt4o = Tracker("GPT-4o")
    result_gpt4o = tracker_gpt4o.update_state(input_tokens=1000, output_tokens=500)
    
    # Test with GPT-4o-mini
    tracker_mini = Tracker("GPT-4o-mini")
    result_mini = tracker_mini.update_state(input_tokens=1000, output_tokens=500)
    
    print(f"GPT-4o cost: ${result_gpt4o['cost']:.4f}")
    print(f"GPT-4o-mini cost: ${result_mini['cost']:.4f}")
    print(f"Cost difference: ${result_gpt4o['cost'] - result_mini['cost']:.4f}")


def custom_model_example():
    """Example with custom model."""
    print("\n=== Custom Model Example ===")
    
    # Create a custom model
    custom_model = Model(
        name="Custom Model",
        d_model=4096,
        d_ff=11008,
        layers=32,
        num_query_heads=32,
        cost_per_input_token=0.001/1000,  # $0.001 per 1K tokens
        cost_per_output_token=0.002/1000,  # $0.002 per 1K tokens
        cost_per_cache_token=0.0005/1000   # $0.0005 per 1K tokens
    )
    
    # Create tracker with custom model
    tracker = Tracker(custom_model=custom_model)
    
    # Track usage
    result = tracker.update_state(input_tokens=500, output_tokens=250, cached_tokens=100)
    print(f"Custom model cost: ${result['cost']:.4f}")
    
    tracker.print_summary()


def batch_tracking_example():
    """Example of tracking multiple API calls in a batch."""
    print("\n=== Batch Tracking Example ===")
    
    tracker = Tracker("GPT-4o")
    
    # Simulate a batch of API calls
    api_calls = [
        {"input_tokens": 50, "output_tokens": 25},
        {"input_tokens": 100, "output_tokens": 50, "cached_tokens": 20},
        {"input_tokens": 200, "output_tokens": 100, "use_cot_reasoning": True},
        {"input_tokens": 75, "output_tokens": 40, "cached_tokens": 15},
    ]
    
    total_cost = 0
    for i, call in enumerate(api_calls, 1):
        result = tracker.update_state(**call)
        total_cost += result['cost']
        print(f"Call {i}: ${result['cost']:.4f}")
    
    print(f"\nTotal batch cost: ${total_cost:.4f}")
    tracker.print_summary()


def integration_example():
    """Example of how to integrate with existing chat applications."""
    print("\n=== Integration Example ===")
    
    # This is how you would integrate with a chat application
    class ChatApp:
        def __init__(self):
            self.tracker = Tracker("GPT-4o")
        
        def make_api_call(self, prompt, response, cached_tokens=0):
            """Simulate making an API call and tracking it."""
            # In a real application, you would get these from your API response
            input_tokens = len(prompt.split())  # Rough estimation
            output_tokens = len(response.split())  # Rough estimation
            
            # Track the usage
            result = self.tracker.update_state(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens
            )
            
            return response, result
        
        def get_usage_summary(self):
            return self.tracker.get_summary()
    
    # Simulate chat application usage
    chat_app = ChatApp()
    
    # Simulate a conversation
    prompt1 = "What is the capital of France?"
    response1, result1 = chat_app.make_api_call(prompt1, "The capital of France is Paris.")
    print(f"Q: {prompt1}")
    print(f"A: {response1}")
    print(f"Cost: ${result1['cost']:.4f}")
    
    prompt2 = "What is the population of Paris?"
    response2, result2 = chat_app.make_api_call(prompt2, "The population of Paris is approximately 2.1 million people.", cached_tokens=10)
    print(f"\nQ: {prompt2}")
    print(f"A: {response2}")
    print(f"Cost: ${result2['cost']:.4f}")
    
    # Get final summary
    summary = chat_app.get_usage_summary()
    print(f"\nTotal conversation cost: ${summary['total_cost_usd']:.4f}")


if __name__ == "__main__":
    # Run all examples
    basic_usage_example()
    comparison_example()
    custom_model_example()
    batch_tracking_example()
    integration_example()
