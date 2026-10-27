"""
Plot mean ROC curve for sleep staging classification.

Input:
    y_predict_all.pickle
        A list of prediction scores/probabilities for each participant.
    y_test_all.pickle
        A list of true binary labels for each participant.

Output:
    Fig2c_ROC.svg
    Fig2c_ROC.png

Usage:
    python Fig2c.py

Or with custom paths:
    python Fig2c.py --data-dir path/to/Fig2c --output-dir path/to/output
"""

from pathlib import Path
import argparse
import pickle

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from scipy.interpolate import make_interp_spline


def load_pickle(file_path: Path):
    """Load a pickle file."""
    with open(file_path, "rb") as f:
        return pickle.load(f)


def compute_mean_roc(y_true_list, y_score_list, n_points=100):
    """
    Compute subject-level ROC curves and average them on a common FPR grid.
    """
    mean_fpr = np.linspace(0, 1, n_points)
    tprs = []
    aucs = []

    for y_true, y_score in zip(y_true_list, y_score_list):
        y_true = np.asarray(y_true).ravel()
        y_score = np.asarray(y_score).ravel()

        # Skip invalid cases with only one class
        if len(np.unique(y_true)) < 2:
            continue

        fpr, tpr, _ = roc_curve(y_true, y_score)
        subject_auc = auc(fpr, tpr)
        aucs.append(subject_auc)

        interp_tpr = np.interp(mean_fpr, fpr, tpr)
        interp_tpr[0] = 0.0
        interp_tpr[-1] = 1.0
        tprs.append(interp_tpr)

    if len(tprs) == 0:
        raise ValueError("No valid ROC curves could be computed. Check y_true and y_score.")

    tprs = np.asarray(tprs)
    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[0] = 0.0
    mean_tpr[-1] = 1.0

    se_tpr = np.std(tprs, axis=0, ddof=1) / np.sqrt(tprs.shape[0])

    return mean_fpr, mean_tpr, se_tpr, np.asarray(aucs)


def plot_mean_roc(
    mean_fpr,
    mean_tpr,
    se_tpr,
    aucs,
    output_dir: Path,
    title="Watch staging ROC curve"
):
    """Plot and save the mean ROC curve."""
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["svg.fonttype"] = "none"

    mean_auc = np.mean(aucs)
    se_auc = np.std(aucs, ddof=1) / np.sqrt(len(aucs))

    # Smooth mean ROC curve for visualisation only
    smooth_fpr = np.linspace(0, 1, 200)
    smooth_tpr = make_interp_spline(mean_fpr, mean_tpr, k=3)(smooth_fpr)
    smooth_tpr = np.clip(smooth_tpr, 0, 1)

    lower_tpr = np.clip(mean_tpr - se_tpr, 0, 1)
    upper_tpr = np.clip(mean_tpr + se_tpr, 0, 1)

    fig, ax = plt.subplots(figsize=(5, 5))

    ax.plot(
        smooth_fpr,
        smooth_tpr,
        color="black",
        linewidth=2,
        label=f"Mean ROC (AUC = {mean_auc:.2f} ± {se_auc:.2f})"
    )

    ax.fill_between(
        mean_fpr,
        lower_tpr,
        upper_tpr,
        color="gray",
        alpha=0.2,
        label="± 1 s.e.m."
    )

    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right", frameon=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()

    fig.savefig(output_dir / "Fig2c_ROC.svg", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "Fig2c_ROC.png", dpi=300, bbox_inches="tight")

    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot mean ROC curve for Fig. 2c.")

    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Folder containing y_predict_all.pickle and y_test_all.pickle. "
             "Default: same folder as this script."
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Folder to save output figures. Default: same folder as this script."
    )

    parser.add_argument(
        "--title",
        type=str,
        default="Watch staging ROC curve",
        help="Figure title."
    )

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    data_dir = Path(args.data_dir) if args.data_dir else script_dir
    output_dir = Path(args.output_dir) if args.output_dir else script_dir

    y_score_path = data_dir / "y_predict_all.pickle"
    y_true_path = data_dir / "y_test_all.pickle"

    y_score_list = load_pickle(y_score_path)
    y_true_list = load_pickle(y_true_path)

    print(f"Loaded prediction scores from: {y_score_path}")
    print(f"Loaded true labels from: {y_true_path}")
    print(f"Number of participants: {len(y_true_list)}")

    mean_fpr, mean_tpr, se_tpr, aucs = compute_mean_roc(
        y_true_list=y_true_list,
        y_score_list=y_score_list
    )

    print(f"Valid ROC curves: {len(aucs)}")
    print(f"Mean AUC ± s.e.m.: {np.mean(aucs):.4f} ± {np.std(aucs, ddof=1) / np.sqrt(len(aucs)):.4f}")

    plot_mean_roc(
        mean_fpr=mean_fpr,
        mean_tpr=mean_tpr,
        se_tpr=se_tpr,
        aucs=aucs,
        output_dir=output_dir,
        title=args.title
    )


if __name__ == "__main__":
    main()