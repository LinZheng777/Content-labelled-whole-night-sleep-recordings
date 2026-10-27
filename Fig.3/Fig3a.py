# -*- coding: utf-8 -*-
"""
Project: Time-Series Waveform Visualization (Mean + SEM)
Description: Generates a 1x4 subplot figure showing EEG/waveform amplitudes
             over time with standard error of the mean (SEM) shaded regions.
             Optimized for GitLab repository submission.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
from typing import Union, Optional


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
        'axes.titlesize': 13,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11
    })


# ==========================================
# Part 2: Main Plotting Function
# ==========================================
def plot_waveforms(input_csv: Union[str, Path], output_fig: Optional[Union[str, Path]] = None) -> None:
    """
    Reads time-series data and generates a 1x4 subplot with Mean curves and SEM shading.

    Args:
        input_csv (str or Path): Path to the input CSV file.
        output_fig (str or Path, optional): Path to save the output figure.
    """
    # 1. Load data
    df = pd.read_csv(input_csv)

    if 'time' not in df.columns:
        raise ValueError("[!] Column 'time' is missing from the input CSV.")

    time_axis = df['time'].values

    # 2. Configuration for conditions, colors, and specific y-limits
    conditions = ["Fast_Spindles", "Slow_Spindles", "Theta_Oscillations", "Slow_Oscillations"]
    colors = {'N2': '#5bc0de', 'N3': '#d9534f'}

    # Define default y-limits and any condition-specific exceptions
    default_ylim = (-50, 15)
    custom_ylims = {
        "Slow_Oscillations": (-100, 50)
    }

    # 3. Initialize figure (1 row, 4 columns)
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.5), dpi=120)

    # 4. Iterate and plot
    for i, cond_name in enumerate(conditions):
        ax = axes[i]

        # Plot N2 and N3 lines for the current condition
        for line_type in ["N2", "N3"]:
            mean_col = f"{cond_name}_{line_type}_mean"
            sem_col = f"{cond_name}_{line_type}_sem"

            # Check if required columns exist before plotting
            if mean_col in df.columns and sem_col in df.columns:
                mean_val = df[mean_col].values
                sem_val = df[sem_col].values

                # Plot the solid mean line
                ax.plot(time_axis, mean_val, color=colors[line_type], label=line_type, linewidth=2)

                # Fill the SEM shaded area
                ax.fill_between(time_axis,
                                mean_val - sem_val,
                                mean_val + sem_val,
                                color=colors[line_type],
                                alpha=0.2,
                                edgecolor='none')
            else:
                print(f"[!] Warning: Missing data for {line_type} in condition '{cond_name}'")

        # Formatting titles and labels
        display_title = cond_name.replace("_", " ")
        ax.set_title(display_title, fontweight='bold')
        ax.set_xlabel("Time (s)")

        # Add zero-point reference line
        ax.axvline(0, color='gray', linestyle='--', linewidth=0.8, zorder=1)

        # Set axes limits
        ax.set_xlim([-2, 2])
        ax.set_ylim(custom_ylims.get(cond_name, default_ylim))

        # Tick parameters configuration
        ax.tick_params(direction='in', width=1.0)
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)

    # 5. Final adjustments
    # Add Y-axis label only to the first subplot to avoid clutter
    axes[0].set_ylabel("Amplitude (uV)", fontweight='bold')

    # Add legend only to the last subplot
    axes[3].legend(frameon=False, loc='upper right')

    plt.tight_layout()

    # 6. Save or display
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
    # Apply global plotting styles
    configure_plot_style()

    # Define paths (Adjust according to your repository structure)
    INPUT_CSV = r"I:\second_resource\code_submit\Fig.3\Fig3a.csv"
    OUTPUT_IMAGE = r"I:\second_resource\code_submit\Fig.3\Fig3a.svg"  # Using SVG or PDF for publication quality

    # Execute the plotting pipeline
    try:
        plot_waveforms(input_csv=INPUT_CSV, output_fig=OUTPUT_IMAGE)
    except FileNotFoundError:
        print(f"[!] Error: The file {INPUT_CSV} was not found. Please verify the path.")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")