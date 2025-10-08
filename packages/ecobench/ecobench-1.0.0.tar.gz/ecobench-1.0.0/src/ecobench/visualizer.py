"""
LLM Usage Visualizer

A module for creating visualizations of LLM usage, costs, and environmental impact.
"""

from typing import Optional, List, TYPE_CHECKING
import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from .tracker import Tracker

class Visualizer:
    """
    A visualizer for LLM usage data from Tracker instances.
    """
    
    def __init__(self, tracker: 'Tracker'):
        """
        Initialize the visualizer with a tracker.
        
        Args:
            tracker (Tracker): The tracker instance to visualize
        """
        self.tracker = tracker
    
    def visualize_usage(self, figsize: tuple = (15, 10), show_per_message: bool = True, 
                       show_cumulative: bool = True, save_path: Optional[str] = None):
        """
        Create visualizations of usage metrics.
        
        Args:
            figsize (tuple): Figure size for the plots
            show_per_message (bool): Whether to show per-message plots
            show_cumulative (bool): Whether to show cumulative plots
            save_path (str, optional): Path to save the figure
        """
        if not self.tracker.usage_history:
            print("No usage data to visualize. Run some updates first.")
            return
        
        # Determine number of subplots needed
        num_plots = 0
        if show_per_message:
            num_plots += 3  # cost, energy, water
        if show_cumulative:
            num_plots += 3  # cumulative cost, energy, water
        
        if num_plots == 0:
            print("No plots to show. Enable show_per_message or show_cumulative.")
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle(f'LLM Usage Visualization - {self.tracker.model_name}', fontsize=16, fontweight='bold')
        
        # Flatten axes for easier indexing
        axes_flat = axes.flatten()
        plot_idx = 0
        
        # Per-message plots
        if show_per_message:
            # Cost per message
            axes_flat[plot_idx].plot(range(1, len(self.tracker.costs_per_message) + 1), 
                                   self.tracker.costs_per_message, 
                                   color='skyblue',  markersize=6, linewidth=2)
            axes_flat[plot_idx].set_title('Cost per Message')
            axes_flat[plot_idx].set_xlabel('Message Number')
            axes_flat[plot_idx].set_ylabel('Cost ($)')
            axes_flat[plot_idx].grid(True, alpha=0.3)
            plot_idx += 1
            
            # Energy per message
            axes_flat[plot_idx].plot(range(1, len(self.tracker.energy_per_message) + 1), 
                                   self.tracker.energy_per_message, 
                                   color='lightgreen', markersize=6, linewidth=2)
            axes_flat[plot_idx].set_title('Energy per Message')
            axes_flat[plot_idx].set_xlabel('Message Number')
            axes_flat[plot_idx].set_ylabel('Energy (Wh)')
            axes_flat[plot_idx].grid(True, alpha=0.3)
            plot_idx += 1
            
            # Water per message
            axes_flat[plot_idx].plot(range(1, len(self.tracker.water_per_message) + 1), 
                                   self.tracker.water_per_message, 
                                   color='lightcoral', markersize=6, linewidth=2)
            axes_flat[plot_idx].set_title('Water per Message')
            axes_flat[plot_idx].set_xlabel('Message Number')
            axes_flat[plot_idx].set_ylabel('Water (liters)')
            axes_flat[plot_idx].grid(True, alpha=0.3)
            plot_idx += 1
        
        # Cumulative plots
        if show_cumulative:
            cumulative_costs = self.tracker.get_cumulative_costs()
            cumulative_energy = self.tracker.get_cumulative_energy()
            cumulative_water = self.tracker.get_cumulative_water()
            
            # Cumulative cost
            axes_flat[plot_idx].plot(range(1, len(cumulative_costs) + 1), cumulative_costs, 
                                    linewidth=2, markersize=6, color='blue')
            axes_flat[plot_idx].set_title('Cumulative Cost')
            axes_flat[plot_idx].set_xlabel('Message Number')
            axes_flat[plot_idx].set_ylabel('Total Cost ($)')
            axes_flat[plot_idx].grid(True, alpha=0.3)
            plot_idx += 1
            
            # Cumulative energy
            axes_flat[plot_idx].plot(range(1, len(cumulative_energy) + 1), cumulative_energy, 
                                linewidth=2, markersize=6, color='green')
            axes_flat[plot_idx].set_title('Cumulative Energy')
            axes_flat[plot_idx].set_xlabel('Message Number')
            axes_flat[plot_idx].set_ylabel('Total Energy (Wh)')
            axes_flat[plot_idx].grid(True, alpha=0.3)
            plot_idx += 1
            
            # Cumulative water
            axes_flat[plot_idx].plot(range(1, len(cumulative_water) + 1), cumulative_water, 
                                    linewidth=2, markersize=6, color='red')
            axes_flat[plot_idx].set_title('Cumulative Water Usage')
            axes_flat[plot_idx].set_xlabel('Message Number')
            axes_flat[plot_idx].set_ylabel('Total Water (liters)')
            axes_flat[plot_idx].grid(True, alpha=0.3)
            plot_idx += 1
        
        # Hide unused subplots
        for i in range(plot_idx, len(axes_flat)):
            axes_flat[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def plot_comparison(self, other_trackers: List['Tracker'], metrics: List[str] = None, 
                       figsize: tuple = (12, 8), save_path: Optional[str] = None):
        """
        Compare multiple trackers on the same plot.
        
        Args:
            other_trackers (List[Tracker]): List of other trackers to compare with
            metrics (List[str]): Metrics to compare ('cost', 'energy', 'water')
            figsize (tuple): Figure size
            save_path (str, optional): Path to save the figure
        """
        if metrics is None:
            metrics = ['cost', 'energy', 'water']
        
        all_trackers = [self.tracker] + other_trackers
        tracker_names = [t.model_name for t in all_trackers]
        
        fig, axes = plt.subplots(1, len(metrics), figsize=figsize)
        if len(metrics) == 1:
            axes = [axes]
        
        fig.suptitle('LLM Tracker Comparison', fontsize=16, fontweight='bold')
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(all_trackers)))
        
        for i, metric in enumerate(metrics):
            ax = axes[i]
            
            for j, tracker in enumerate(all_trackers):
                if metric == 'cost':
                    data = tracker.get_cumulative_costs()
                    ylabel = 'Total Cost ($)'
                elif metric == 'energy':
                    data = tracker.get_cumulative_energy()
                    ylabel = 'Total Energy (Wh)'
                elif metric == 'water':
                    data = tracker.get_cumulative_water()
                    ylabel = 'Total Water (liters)'
                else:
                    continue
                
                if data:  # Only plot if there's data
                    ax.plot(range(1, len(data) + 1), data, 
                           marker='o', linewidth=2, markersize=4, 
                           color=colors[j], label=tracker_names[j])
            
            ax.set_title(f'Cumulative {metric.title()}')
            ax.set_xlabel('Message Number')
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison figure saved to {save_path}")
        
        plt.show()
    
    def plot_metric_trends(self, metric: str = 'cost', figsize: tuple = (10, 6), 
                          save_path: Optional[str] = None):
        """
        Plot trends for a specific metric with both per-message and cumulative views.
        
        Args:
            metric (str): Metric to plot ('cost', 'energy', 'water')
            figsize (tuple): Figure size
            save_path (str, optional): Path to save the figure
        """
        if not self.tracker.usage_history:
            print("No usage data to visualize. Run some updates first.")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle(f'{metric.title()} Trends - {self.tracker.model_name}', 
                    fontsize=14, fontweight='bold')
        
        # Get data based on metric
        if metric == 'cost':
            per_message_data = self.tracker.costs_per_message
            cumulative_data = self.tracker.get_cumulative_costs()
            ylabel = 'Cost ($)'
            color = 'blue'
        elif metric == 'energy':
            per_message_data = self.tracker.energy_per_message
            cumulative_data = self.tracker.get_cumulative_energy()
            ylabel = 'Energy (Wh)'
            color = 'green'
        elif metric == 'water':
            per_message_data = self.tracker.water_per_message
            cumulative_data = self.tracker.get_cumulative_water()
            ylabel = 'Water (liters)'
            color = 'red'
        else:
            print(f"Unknown metric: {metric}. Use 'cost', 'energy', or 'water'.")
            return
        
        # Per-message plot
        ax1.plot(range(1, len(per_message_data) + 1), per_message_data, 
               color=color, markersize=6, linewidth=2)
        ax1.set_title(f'{metric.title()} per Message')
        ax1.set_xlabel('Message Number')
        ax1.set_ylabel(ylabel)
        ax1.grid(True, alpha=0.3)
        
        # Cumulative plot
        ax2.plot(range(1, len(cumulative_data) + 1), cumulative_data, 
                color=color, markersize=6, linewidth=2)
        ax2.set_title(f'Cumulative {metric.title()}')
        ax2.set_xlabel('Message Number')
        ax2.set_ylabel(f'Total {ylabel}')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Trend figure saved to {save_path}")
        
        plt.show()


# Convenience functions
def create_visualizer(tracker: 'Tracker') -> Visualizer:
    """
    Create a new visualizer for a tracker.
    
    Args:
        tracker (Tracker): The tracker to visualize
        
    Returns:
        Visualizer: New visualizer instance
    """
    return Visualizer(tracker)


def compare_trackers(trackers: List['Tracker'], metrics: List[str] = None, 
                    figsize: tuple = (12, 8), save_path: Optional[str] = None):
    """
    Compare multiple trackers without creating a visualizer instance.
    
    Args:
        trackers (List[Tracker]): List of trackers to compare
        metrics (List[str]): Metrics to compare
        figsize (tuple): Figure size
        save_path (str, optional): Path to save the figure
    """
    if not trackers:
        print("No trackers provided for comparison.")
        return
    
    visualizer = Visualizer(trackers[0])
    visualizer.plot_comparison(trackers[1:], metrics, figsize, save_path)
