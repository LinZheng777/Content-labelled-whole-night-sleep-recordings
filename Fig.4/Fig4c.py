# -*- coding: utf-8 -*-
"""
Project: History Curve Similarity Visualization
Description: Generates a publication-ready scatter plot with error bars
             and statistical significance markers.
             Optimized for GitLab repository submission.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy.stats as stats
from pathlib import Path


# ==========================================
# Part 1: Global Plotting Configuration
# ==========================================
def configure_plot_style():
    """Configures global matplotlib styles for publication quality."""
    mpl.rcParams.update({
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'font.size': 12,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11
    })


# ==========================================
# Part 2: Main Plotting Function
# ==========================================
def plot_history_similarity(input_csv: Union[str, Path], output_fig: Optional[Union[str, Path]] = None) -> None:
    """
    Reads similarity data and generates a scatter plot with Mean ± SEM.

    Args:
        input_csv (str or Path): Path to the input CSV file.
        output_fig (str or Path, optional): Path to save the output figure. If None, only displays the plot.
    """
    # 1. Load data
    df = pd.read_csv(input_csv)

    # 2. Define target columns and corresponding axis labels
    columns = ['within_r', 'between_night1_r', 'between_night2_r']
    labels = ['Within', 'Between\nnight1', 'Between\nnight2']

    # Validate that columns exist in the dataframe
    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in the provided CSV file.")

    # 3. Initialize figure
    fig, ax = plt.subplots(figsize=(4.2, 6.5), dpi=120)

    # Layout parameters
    x_positions = [0, 1, 2]
    error_bar_offset = 0.35

    # 4. Iterate over columns to plot individual data points and error bars
    np.random.seed(42)  # Set seed for reproducible jitter

    for i, col in enumerate(columns):
        # Drop NaN values to ensure accurate statistical calculations
        y_data = df[col].dropna().values

        # Generate normal distribution jitter for X-axis to disperse dense points
        x_jitter = np.random.normal(loc=x_positions[i], scale=0.04, size=len(y_data))

        # Scatter plot for raw data points (left side)
        ax.scatter(x_jitter, y_data,
                   color='#4a4444',
                   alpha=0.5,
                   s=35,
                   edgecolors='none',
                   zorder=2)

        # Calculate Mean and Standard Error of the Mean (SEM)
        mean_val = np.mean(y_data)
        sem_val = stats.sem(y_data)

        # Plot error bars (Mean ± SEM) (right side)
        ax.errorbar(x_positions[i] + error_bar_offset, mean_val, yerr=sem_val,
                    fmt='o', color='black', markersize=5.5,
                    capsize=5, elinewidth=1.5, capthick=1.5, zorder=3)

    # 5. Add reference background line at y = 1.00
    ax.axhline(1.00, color='lightgray', linestyle='-', linewidth=0.8, zorder=1)

    # 6. Add significance markers (***)
    # Significance 1: Within vs Between night1
    y_line1 = 1.006
    ax.plot([0, 1], [y_line1, y_line1], color='black', linewidth=1, zorder=4)
    ax.text(0.5, y_line1 + 0.001, '***', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Significance 2: Within vs Between night2
    y_line2 = 1.013
    ax.plot([0, 2], [y_line2, y_line2], color='black', linewidth=1, zorder=4)
    ax.text(1.0, y_line2 + 0.001, '***', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # 7. Axes formatting and aesthetics
    ax.set_ylabel('History curve similarity (r)', fontweight='bold')

    # Align X-ticks with the center of the scattered data points
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, fontweight='bold')

    # Set axes limits
    ax.set_xlim([-0.4, 2.6])
    ax.set_ylim([0.90, 1.025])
    ax.set_yticks([0.92, 0.96, 1.00])

    # Adjust spine line width and tick properties
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    ax.tick_params(direction='in', width=1.2)

    # 8. Finalize layout and save/show
    plt.tight_layout()

    if output_fig:
        output_dir = Path(output_fig).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_fig, bbox_inches='tight', dpi=300)
        print(f"[*] Plot successfully saved to: {output_fig}")

    plt.show()


# ==========================================
# Main Execution Block
# ==========================================
if __name__ == "__main__":
    from typing import Union, Optional  # Local import for type hinting clarity

    # Apply global plotting styles
    configure_plot_style()

    # Define paths (Adjust these paths according to your repository structure)
    # Using raw strings for Windows paths or Pathlib for cross-platform compatibility
    INPUT_CSV = r"Fig.4\Fig4c.csv"
    OUTPUT_IMAGE = r"Fig.4\Fig4c.svg"  # Using SVG or PDF is recommended for publications

    # Execute the plotting function
    try:
        plot_history_similarity(input_csv=INPUT_CSV, output_fig=OUTPUT_IMAGE)
    except FileNotFoundError:
        print(f"[!] Error: The data file was not found at {INPUT_CSV}. Please check the path.")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")