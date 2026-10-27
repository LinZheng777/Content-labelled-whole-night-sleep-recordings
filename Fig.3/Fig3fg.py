# -*- coding: utf-8 -*-
"""
Project: Coupling Metrics Visualization (Power & Phase)
Description: Generates scatter plots with mean and SEM error bars for
             coupling Power and Phase across different frequency bands and sleep stages.
             Includes circular statistics and phase-wrapping adjustments for phase data.
Author: zhenglin (Optimized for GitLab Submission)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import circmean, circstd
from matplotlib.lines import Line2D
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
        'axes.labelsize': 13,
        'axes.titlesize': 15,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12
    })


# ==========================================
# Part 2: Main Plotting Function
# ==========================================
def plot_coupling_metrics(input_csv: Union[str, Path], output_fig: Optional[Union[str, Path]] = None) -> None:
    """
    Reads long-format coupling data and plots Power and Phase metrics with
    statistical markers (Mean + SEM). Applies circular statistics for Phase.
    """
    # 1. Load Data
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        raise RuntimeError(f"[!] Failed to load data from {input_csv}: {e}")

    # 2. Plotting Configuration
    freqs = ['fast', 'slow', 'theta']
    stages = ['N2', 'N3']
    metrics = ['Power', 'Phase']

    # Color palette
    palette = {'N2': '#64AAD2', 'N3': '#C83C3C'}  # N2: Light Blue, N3: Light Red

    # 3. Initialize Figure
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=True, dpi=120)

    # Fix random seed for reproducible jitter in scatter plot
    np.random.seed(42)

    for i, ax in enumerate(axes):
        metric = metrics[i]

        for idx, freq in enumerate(freqs):
            for s_idx, stage in enumerate(stages):

                # Extract relevant subset
                subset_raw = df[(df['Frequency'] == freq) & (df['Stage'] == stage)][metric].dropna()
                if subset_raw.empty:
                    continue

                # --- Core Logic: Compute Stats (Standard vs. Circular) ---
                if metric == 'Phase':
                    # Calculate circular mean and standard error within [-pi, pi]
                    mean_val = circmean(subset_raw, low=-np.pi, high=np.pi)
                    sem_val = circstd(subset_raw, low=-np.pi, high=np.pi) / np.sqrt(len(subset_raw))

                    # Phase Unwrapping / Visual Shifting
                    # Shifts points distant from the mean by +/- 2pi to visually cluster around the mean
                    subset = subset_raw.copy()
                    subset[subset - mean_val > np.pi] -= 2 * np.pi
                    subset[subset - mean_val < -np.pi] += 2 * np.pi
                else:
                    subset = subset_raw
                    mean_val = subset.mean()
                    sem_val = subset.std() / np.sqrt(len(subset))

                # Define X-axis positions (with jitter for scatter points)
                base_x = idx + (s_idx * 0.4 - 0.2)
                scatter_x = base_x - 0.05 + (np.random.rand(len(subset)) - 0.5) * 0.1
                err_x = base_x + 0.15

                # Plot Raw Data Scatter
                ax.scatter(scatter_x, subset, color=palette[stage], alpha=0.4, s=30, edgecolors='none', zorder=2)

                # Plot Mean Line
                ax.hlines(mean_val, err_x - 0.1, err_x + 0.1, colors=palette[stage], lw=4, zorder=10)

                # Plot Error Bar (SEM)
                ax.errorbar(err_x, mean_val, yerr=sem_val, fmt='none', ecolor=palette[stage],
                            elinewidth=2.5, capsize=5, zorder=9)

        # Aesthetic formatting for each subplot
        ax.set_xticks(range(len(freqs)))
        ax.set_xticklabels([f.capitalize() for f in freqs], fontweight='bold')
        ax.set_title(f'Coupling {metric}', fontweight='bold', pad=15)

        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)
        ax.tick_params(direction='out', width=1.2)

        # Special axis formatting for Phase
        if metric == 'Phase':
            # Allow limits to slightly exceed pi to accommodate phase-shifted points
            ax.set_yticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi, 1.5 * np.pi])
            ax.set_yticklabels(['-π', '-π/2', '0', 'π/2', 'π', ''])
            ax.set_ylabel('Phase (rad)', fontweight='bold')
            ax.set_ylim([-1.2 * np.pi, 1.5 * np.pi])
        else:
            ax.set_ylabel('Power', fontweight='bold')

    # 4. Add Global Legend
    custom_lines = [Line2D([0], [0], color=palette['N2'], lw=5),
                    Line2D([0], [0], color=palette['N3'], lw=5)]
    fig.legend(custom_lines, ['N2', 'N3'], loc='upper center',
               bbox_to_anchor=(0.5, 1.05), ncol=2, frameon=False,
               prop={'weight': 'bold', 'size': 13})

    # 5. Finalize Layout and Export
    plt.tight_layout()

    if output_fig:
        out_path = Path(output_fig)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, bbox_inches='tight', dpi=300)
        print(f"[*] Plot successfully saved to: {out_path}")

    plt.show()


# ==========================================
# Main Execution Block
# ==========================================
if __name__ == '__main__':
    # Apply global styles
    configure_plot_style()

    # Define Paths (Adjust to your repository structure)
    INPUT_CSV = Path(r'Fig3\Fig3_fg.csv')
    OUTPUT_SVG = Path(r'Fig3\Fig3_fg.svg')

    try:
        # Execute plotting function
        plot_coupling_metrics(input_csv=INPUT_CSV, output_fig=OUTPUT_SVG)
    except Exception as err:
        print(f"\n[!] Pipeline Failed: {err}")