"""
Simple test to demonstrate the library usage.
"""

from ecobench import Tracker

def main():
    print("Ecobench Library Demo")
    print("=" * 40)
    
    # Initialize tracker
    tracker = Tracker("GPT-4o")
    print(f"Initialized tracker for {tracker.model_name}")
    
    # Simulate a chat conversation
    print("\nSimulating chat conversation...")
    
    # First message
    result1 = tracker.update_state(
        input_tokens=50,
        output_tokens=25,
        cached_tokens=0
    )
    print(f"First message: ${result1['cost']:.4f}")
    
    # Second message (with some cached context)
    result2 = tracker.update_state(
        input_tokens=100,
        output_tokens=50,
        cached_tokens=30
    )
    print(f"Second message: ${result2['cost']:.4f}")
    
    # Third message with chain of thought reasoning
    result3 = tracker.update_state(
        input_tokens=75,
        output_tokens=40,
        use_cot_reasoning=True
    )
    print(f"Third message (CoT): ${result3['cost']:.4f}")
    
    # Show summary
    print("\nUsage Summary:")
    tracker.print_summary()
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
