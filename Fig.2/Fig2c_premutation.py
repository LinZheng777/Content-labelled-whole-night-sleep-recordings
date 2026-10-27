"""
Plot explained variance against the permutation-derived null distribution.

Input
-----
Fig2c_permutation.csv
    Required columns:
    - low_bounds: lower bound of the null distribution, e.g. 5th percentile
    - high_bounds: upper bound of the null distribution, e.g. 95th percentile
    - auc_data: observed explained variance or AUC values

Output
------
Fig2c_permutation_explained_variance.svg
Fig2c_permutation_explained_variance.png

Usage
-----
python Fig2c_permutation_plot.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# Figure settings
# ---------------------------------------------------------------------
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"  # Keep SVG text editable


# ---------------------------------------------------------------------
# Input and output paths
# ---------------------------------------------------------------------
# The CSV file should be placed in the same folder as this script.
# If running from another location, replace this with an absolute path, e.g.:
# data_file = Path(r"I:\second_resource\code_submit\Fig.2\Fig2c\Fig2c_permutation.csv")
script_dir = Path(__file__).resolve().parent
data_file = script_dir / "Fig2c_permutation.csv"

output_svg = script_dir / "Fig2c_permutation_explained_variance.svg"
output_png = script_dir / "Fig2c_permutation_explained_variance.png"


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
data = pd.read_csv(data_file)

required_cols = ["low_bounds", "high_bounds", "auc_data"]
missing_cols = [col for col in required_cols if col not in data.columns]

if missing_cols:
    raise ValueError(f"Missing required columns in {data_file}: {missing_cols}")

lower_bounds = data["low_bounds"].to_numpy(dtype=float)
upper_bounds = data["high_bounds"].to_numpy(dtype=float)
observed_values = data["auc_data"].to_numpy(dtype=float)


# ---------------------------------------------------------------------
# Prepare x-axis
# ---------------------------------------------------------------------
n_components = len(observed_values)
components = np.arange(1, n_components + 1)


# ---------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7))

# Null distribution interval
ax.fill_between(
    components,
    lower_bounds,
    upper_bounds,
    color="lightgrey",
    alpha=0.6,
    label="5th–95th percentile range"
)

# Observed values
ax.plot(
    components,
    observed_values,
    marker="o",
    linewidth=1.8,
    markersize=4,
    color="lightskyblue",
    label="Observed value"
)

# Optional reference line at zero
ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

ax.set_xlabel("Component index", fontsize=13, fontweight="bold")
ax.set_ylabel("Explained variance", fontsize=13, fontweight="bold")
ax.set_title("Explained variance and permutation-derived null distribution", fontsize=14)

ax.set_xlim(1, n_components)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(frameon=False)

fig.tight_layout()

fig.savefig(output_svg, dpi=300, bbox_inches="tight")
fig.savefig(output_png, dpi=300, bbox_inches="tight")

plt.show()

print(f"Figure saved to:\n{output_svg}\n{output_png}")