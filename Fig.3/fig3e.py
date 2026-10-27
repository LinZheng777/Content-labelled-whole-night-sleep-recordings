# -*- coding: utf-8 -*-
"""
Project: Time-Frequency Permutation Cluster Analysis (N3 vs. N2)
Description: Loads sleep MEG/EEG data, computes paired t-tests, performs
             permutation cluster testing, applies global FDR correction
             across all conditions, and plots the significant clusters.
Author: zhenglin (Optimized for GitLab Submission)
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import mne
from scipy.stats import ttest_rel, t
from statsmodels.stats.multitest import multipletests
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
from typing import Dict, List, Any


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
        'axes.titlesize': 14,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11
    })


# ==========================================
# Part 2: Core Analytical Functions
# ==========================================
def load_h5_data(file_path: Path) -> Dict[str, np.ndarray]:
    """Loads specific sleep stage data from an HDF5 (.mat) file."""
    data_dict = {}
    try:
        with h5py.File(file_path, 'r') as f:
            data_dict['N2_slow'] = np.array(f['data_N2_slow']).T
            data_dict['N2_fast'] = np.array(f['data_N2_fast']).T
            data_dict['N2_theta'] = np.array(f['data_N2_theta']).T
            data_dict['N3_slow'] = np.array(f['data_N3_slow']).T
            data_dict['N3_fast'] = np.array(f['data_N3_fast']).T
            data_dict['N3_theta'] = np.array(f['data_N3_theta']).T
        return data_dict
    except Exception as e:
        raise RuntimeError(f"[!] Failed to load data from {file_path}: {e}")


def run_cluster_analysis_with_fdr(
        data_dict: Dict[str, np.ndarray],
        freq_idx: np.ndarray,
        n_permutations: int = 1000,
        alpha_initial: float = 0.05
) -> List[Dict[str, Any]]:
    """
    Executes permutation cluster testing across conditions and applies FDR correction.
    """
    spindle_types = ['fast', 'slow', 'theta']
    all_cluster_info = []

    print(f"[*] Starting Permutation Cluster Tests ({n_permutations} permutations)...")

    # Stage 1: Gather cluster p-values for all conditions
    for current_type in spindle_types:
        all_N2 = data_dict[f'N2_{current_type}']
        all_N3 = data_dict[f'N3_{current_type}']

        # Select target frequency range
        all_N2_sel = all_N2[:, freq_idx, :]
        all_N3_sel = all_N3[:, freq_idx, :]
        n_subjects = all_N2_sel.shape[0]

        # Calculate observation T-values for plotting
        t_vals_obs, _ = ttest_rel(all_N3_sel, all_N2_sel, axis=0)

        # Execute MNE Permutation Cluster Test
        thresh = t.ppf(1 - alpha_initial / 2, n_subjects - 1)
        T_obs, clusters, cluster_p_values, _ = mne.stats.permutation_cluster_test(
            [all_N3_sel, all_N2_sel],
            threshold=thresh,
            n_permutations=n_permutations,
            tail=0,
            out_type='mask',
            verbose=False
        )

        # Store results
        for c_idx, mask in enumerate(clusters):
            all_cluster_info.append({
                'type': current_type,
                't_map': t_vals_obs,
                'mask': mask,
                'p_val': cluster_p_values[c_idx]
            })

    # Stage 2: Cross-condition FDR Correction
    p_values_list = [c['p_val'] for c in all_cluster_info]

    if not p_values_list:
        print("[!] No candidate clusters found across any condition.")
        return []

    print(f"[*] Applying Benjamini-Hochberg FDR correction across {len(p_values_list)} clusters...")
    reject, p_corrected, _, _ = multipletests(p_values_list, method='fdr_bh')

    # Update dictionary with FDR outcomes
    for i, cluster in enumerate(all_cluster_info):
        cluster['is_significant'] = reject[i]
        cluster['p_corrected'] = p_corrected[i]

    return all_cluster_info


# ==========================================
# Part 3: Visualization Function
# ==========================================
def plot_significant_clusters(
        cluster_info: List[Dict[str, Any]],
        freq_vals: np.ndarray,
        out_dir: Path
) -> None:
    """Renders and exports T-value time-frequency maps with FDR-significant cluster contours."""

    # Custom Colormap (Blue -> White -> Red)
    custom_cmap = LinearSegmentedColormap.from_list(
        'bwr_custom',
        [(78 / 256, 160 / 256, 210 / 256), (1, 1, 1), (202 / 256, 86 / 256, 92 / 256)],
        N=256
    )

    spindle_types = ['fast', 'slow', 'theta']

    for current_type in spindle_types:
        # Isolate clusters for the specific wave type
        type_clusters = [c for c in cluster_info if c['type'] == current_type]
        if not type_clusters:
            continue

        t_values = type_clusters[0]['t_map']
        n_f, n_t = t_values.shape

        # Aggregate masks for FDR-significant clusters only
        mask_fdr = np.zeros((n_f, n_t), dtype=bool)
        sig_count = 0

        for c in type_clusters:
            if c['is_significant']:
                mask_fdr |= c['mask']
                sig_count += 1
                print(f"    -> [{current_type.upper()}] Significant Cluster FDR-p: {c['p_corrected']:.4f}")

        # Initialize Plot
        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=120)
        im = ax.imshow(t_values, cmap=custom_cmap, origin='lower', aspect='auto', vmin=-6, vmax=6)

        # Colorbar configuration
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('T-value (N3 - N2)', fontweight='bold')

        # Draw contour if significant clusters exist
        if mask_fdr.any():
            ax.contour(mask_fdr, colors='black', linewidths=1.5, origin='lower')

        # X-Axis formatting (Time)
        ax.set_xticks(np.linspace(0, n_t - 1, 7))
        ax.set_xticklabels(['-1.5', '-1.0', '-0.5', '0.0', '0.5', '1.0', '1.5'])
        ax.set_xlabel('Time (s)', fontweight='bold')

        # Y-Axis formatting (Frequency)
        yticks_hz = [2, 5, 10, 15, 20, 25]
        yticks_pos = [np.where(freq_vals == hz)[0][0] for hz in yticks_hz]
        ax.set_yticks(yticks_pos)
        ax.set_yticklabels([str(hz) for hz in yticks_hz])
        ax.set_ylabel('Frequency (Hz)', fontweight='bold')

        # Aesthetic tweaks
        ax.tick_params(direction='out', width=1.0)
        ax.set_title(
            f'N3 vs N2 Difference ({current_type.capitalize()})\n{sig_count} Significant Clusters (FDR < 0.05)', pad=15)

        # Export
        save_path = out_dir / f'{current_type}_diff_FDR_corrected.svg'
        plt.tight_layout()
        plt.savefig(save_path, format='svg', bbox_inches='tight')
        plt.close(fig)

        print(f"[OK] Exported {current_type.upper()} map with {sig_count} clusters: {save_path.name}")


# ==========================================
# Main Execution Block
# ==========================================
if __name__ == '__main__':
    # Apply global styles
    configure_plot_style()

    # Define Paths
    DATA_PATH = Path(r'Fig.3\Fig3e.mat.mat')
    OUT_DIR = Path(r'Fig.3')
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Core Parameters
    FREQ_IDX = np.arange(2, 26)
    FREQ_VALS = FREQ_IDX.astype(float)
    N_PERMUTATIONS = 1000
    ALPHA = 0.05

    try:
        # Execute Pipeline
        data_dict = load_h5_data(DATA_PATH)

        cluster_results = run_cluster_analysis_with_fdr(
            data_dict=data_dict,
            freq_idx=FREQ_IDX,
            n_permutations=N_PERMUTATIONS,
            alpha_initial=ALPHA
        )

        if cluster_results:
            plot_significant_clusters(
                cluster_info=cluster_results,
                freq_vals=FREQ_VALS,
                out_dir=OUT_DIR
            )
            print("\n[*] Pipeline execution completed successfully.")

    except Exception as err:
        print(f"\n[!] Pipeline Failed: {err}")