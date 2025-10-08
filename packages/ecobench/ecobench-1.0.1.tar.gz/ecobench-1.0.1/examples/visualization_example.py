"""
Example demonstrating the visualization functionality using the separate visualizer module.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ecobench import Tracker, Visualizer, compare_trackers

def main():
    # Create a tracker
    tracker = Tracker("GPT-4o")
    
    # Simulate some usage
    print("Simulating LLM usage...")
    tracker.update_state(input_tokens=100, output_tokens=50)
    tracker.update_state(input_tokens=200, output_tokens=75)
    tracker.update_state(input_tokens=150, output_tokens=60)
    tracker.update_state(input_tokens=300, output_tokens=100)
    tracker.update_state(input_tokens=80, output_tokens=40)
    
    # Print summary
    tracker.print_summary()
    
    # Show per-message data
    print("\nPer-message costs:", tracker.get_costs_per_message())
    print("Cumulative costs:", tracker.get_cumulative_costs())
    
    # Create visualizations using the separate visualizer
    print("\nCreating visualizations...")
    
    # Create visualizer
    visualizer = Visualizer(tracker)
    
    # Basic visualization
    visualizer.visualize_usage()
    
    # Save visualization
    visualizer.visualize_usage(save_path="usage_visualization.png")
    
    # Plot specific metric trends
    visualizer.plot_metric_trends('cost', save_path="cost_trends.png")
    
    # Create comparison with another model
    tracker2 = Tracker("GPT-4o-mini")
    tracker2.update_state(input_tokens=100, output_tokens=50)
    tracker2.update_state(input_tokens=200, output_tokens=75)
    tracker2.update_state(input_tokens=150, output_tokens=60)
    
    # Compare models using the convenience function
    compare_trackers([tracker, tracker2], save_path="model_comparison.png")

if __name__ == "__main__":
    main()
