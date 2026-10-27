"""
Fig2fgh_correlation_plot.py

Purpose
-------
Compute Spearman correlations among self-reported, EEG-derived and
actigraphy-derived sleep measures for TST and WASO, apply FDR correction,
and plot pairwise scatter/regression panels.

Input
-----
Fig2fgh.xlsx
    Required columns:
    - subjects
    - WASO_scale
    - WASO
    - WASO_watch
    - TST_scale
    - TST
    - TST_watch

Output
------
Fig2fgh_correlation_results.csv
Fig2fgh_subjects_1_to_135_checked.csv
Fig2fgh_correlation_plot.svg
Fig2fgh_correlation_plot.png

Usage
-----
python Fig2fgh_correlation_plot.py

The input Excel file should be placed in the same folder as this script.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.multitest import multipletests


# ---------------------------------------------------------------------
# Figure settings
# ---------------------------------------------------------------------
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.family"] = "Arial"

sns.set_theme(style="white", palette="muted")


# ---------------------------------------------------------------------
# Input and output paths
# ---------------------------------------------------------------------
# The Excel file should be placed in the same folder as this script.
# To use an absolute path, replace this line, for example:
# data_file = Path(r"I:\second_resource\code_submit\Fig.2\Fig2fgh.xlsx")
script_dir = Path(__file__).resolve().parent
data_file = script_dir / "Fig2fgh.xlsx"

result_csv = script_dir / "Fig2fgh_correlation_results.csv"
checked_csv = script_dir / "Fig2fgh_subjects_1_to_135_checked.csv"
output_svg = script_dir / "Fig2fgh_correlation_plot.svg"
output_png = script_dir / "Fig2fgh_correlation_plot.png"


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def significance_stars(p_value: float) -> str:
    """Return significance stars based on p value."""
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return "n.s."


def get_pair_stats(results_df: pd.DataFrame, var1: str, var2: str) -> pd.Series:
    """
    Retrieve statistics for a variable pair, allowing either variable order.
    """
    match = results_df[
        ((results_df["Var1"] == var1) & (results_df["Var2"] == var2)) |
        ((results_df["Var1"] == var2) & (results_df["Var2"] == var1))
    ]

    if match.empty:
        raise ValueError(f"No correlation result found for pair: {var1}, {var2}")

    return match.iloc[0]


def normalise_subject_id(x):
    """
    Convert subject identifiers to integer IDs.

    Accepts:
    - 1, 2, 3...
    - '1', '2', '3'...
    - 'sub-001', 'sub-002'...
    """
    if pd.isna(x):
        return np.nan

    x_str = str(x).strip()

    if x_str.startswith("sub-"):
        x_str = x_str.replace("sub-", "")

    return int(float(x_str))


# ---------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------
df = pd.read_excel(data_file)

required_cols = [
    "subjects",
    "WASO_scale", "WASO", "WASO_watch",
    "TST_scale", "TST", "TST_watch"
]

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns in {data_file}: {missing_cols}")


# ---------------------------------------------------------------------
# 2. Standardise and check subjects
# ---------------------------------------------------------------------
df["subjects"] = df["subjects"].apply(normalise_subject_id)

# Keep only subjects 1-135 and sort by subject ID
required_subject_list = list(range(1, 136))

df = df[df["subjects"].isin(required_subject_list)].copy()

# If duplicate subject rows exist, keep the first and warn
duplicated_subjects = df.loc[df["subjects"].duplicated(), "subjects"].tolist()
if duplicated_subjects:
    print(f"Warning: duplicated subject IDs found and first occurrence kept: {duplicated_subjects}")
    df = df.drop_duplicates(subset="subjects", keep="first")

# Reindex to ensure subjects 1-135 are all represented
df = (
    df.set_index("subjects")
      .reindex(required_subject_list)
      .rename_axis("subjects")
      .reset_index()
)

# Save checked table for transparency
df.to_csv(checked_csv, index=False, encoding="utf-8-sig")

print(f"Checked subject table saved to: {checked_csv}")
print(f"Total expected subjects: {len(required_subject_list)}")
print(f"Rows after reindexing: {len(df)}")


# ---------------------------------------------------------------------
# 3. Log transformation
# ---------------------------------------------------------------------
measure_cols = [
    "WASO_scale", "WASO", "WASO_watch",
    "TST_scale", "TST", "TST_watch"
]

# Make sure target columns are numeric
for col in measure_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Use log10(x + 1) to reduce skewness while keeping zero values valid.
for col in measure_cols:
    df[f"log_{col}"] = np.log10(df[col] + 1)


# ---------------------------------------------------------------------
# 4. Define variable groups
# ---------------------------------------------------------------------
groups = {
    "WASO": ["log_WASO_scale", "log_WASO", "log_WASO_watch"],
    "TST": ["log_TST_scale", "log_TST", "log_TST_watch"]
}

results = []


# ---------------------------------------------------------------------
# 5. Compute Spearman correlations
# ---------------------------------------------------------------------
for metric_label, variables in groups.items():
    pairs = [
        (variables[0], variables[1]),
        (variables[0], variables[2]),
        (variables[1], variables[2])
    ]

    for x_var, y_var in pairs:
        temp_df = df[[x_var, y_var]].dropna()

        if len(temp_df) <= 5:
            continue

        stats = pg.corr(
            x=temp_df[x_var],
            y=temp_df[y_var],
            method="spearman"
        )

        results.append({
            "Metric": metric_label,
            "Var1": x_var.replace("log_", ""),
            "Var2": y_var.replace("log_", ""),
            "r": stats["r"].values[0],
            "p_uncorrected": stats["p-val"].values[0],
            "N": len(temp_df)
        })


res_df = pd.DataFrame(results)

if res_df.empty:
    raise ValueError("No valid correlations were computed. Please check the input data.")


# ---------------------------------------------------------------------
# 6. FDR correction
# ---------------------------------------------------------------------
reject, p_adj, _, _ = multipletests(
    res_df["p_uncorrected"],
    method="fdr_bh"
)

res_df["p_adj_FDR"] = p_adj
res_df["is_significant"] = reject

res_df.to_csv(result_csv, index=False, encoding="utf-8-sig")

print("Correlation results saved to:")
print(result_csv)
print(res_df)


# ---------------------------------------------------------------------
# 7. Plot
# ---------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.subplots_adjust(hspace=0.4, wspace=0.3)

plot_configs = [
    {
        "x": "log_TST_scale",
        "y": "log_TST",
        "ax": axes[0, 0],
        "title": "TST: Self-report vs EEG"
    },
    {
        "x": "log_TST_scale",
        "y": "log_TST_watch",
        "ax": axes[0, 1],
        "title": "TST: Self-report vs Actigraphy"
    },
    {
        "x": "log_TST",
        "y": "log_TST_watch",
        "ax": axes[0, 2],
        "title": "TST: EEG vs Actigraphy"
    },
    {
        "x": "log_WASO_scale",
        "y": "log_WASO",
        "ax": axes[1, 0],
        "title": "WASO: Self-report vs EEG"
    },
    {
        "x": "log_WASO_scale",
        "y": "log_WASO_watch",
        "ax": axes[1, 1],
        "title": "WASO: Self-report vs Actigraphy"
    },
    {
        "x": "log_WASO",
        "y": "log_WASO_watch",
        "ax": axes[1, 2],
        "title": "WASO: EEG vs Actigraphy"
    },
]

# Fix jitter locations for reproducible plotting
np.random.seed(42)

for config in plot_configs:
    ax = config["ax"]

    x_var = config["x"]
    y_var = config["y"]

    plot_df = df[[x_var, y_var]].dropna()

    sns.regplot(
        data=plot_df,
        x=x_var,
        y=y_var,
        ax=ax,
        x_jitter=0.02,
        y_jitter=0.02,
        scatter_kws={
            "alpha": 0.4,
            "s": 25,
            "color": "#4C72B0"
        },
        line_kws={
            "color": "#C44E52",
            "lw": 2.5
        }
    )

    var1_name = x_var.replace("log_", "")
    var2_name = y_var.replace("log_", "")

    stats = get_pair_stats(res_df, var1_name, var2_name)

    stars = significance_stars(stats["p_adj_FDR"])

    stat_text = (
        f"$r_s = {stats['r']:.2f}^{{{stars}}}$\n"
        f"$p_{{FDR}} = {stats['p_adj_FDR']:.3f}$\n"
        f"$N = {int(stats['N'])}$"
    )

    ax.text(
        0.05,
        0.95,
        stat_text,
        transform=ax.transAxes,
        verticalalignment="top",
        fontsize=11,
        fontweight="bold",
        bbox={
            "boxstyle": "round",
            "facecolor": "white",
            "alpha": 0.7,
            "edgecolor": "none"
        }
    )

    ax.set_title(config["title"], fontsize=14, pad=15)
    ax.set_xlabel(f"log10({var1_name} + 1)")
    ax.set_ylabel(f"log10({var2_name} + 1)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


fig.tight_layout()

fig.savefig(output_svg, dpi=300, bbox_inches="tight")
fig.savefig(output_png, dpi=300, bbox_inches="tight")

plt.show()

print("Figure saved to:")
print(output_svg)
print(output_png)