import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from statsmodels.stats.multitest import multipletests

# Enable exporting editable text in SVG format
plt.rcParams['svg.fonttype'] = 'none'

# ==========================================
# 1. Load Data
# ==========================================
# Use relative path for GitLab/collaboration compatibility
csv_file = 'fig6c.csv'
df = pd.read_csv(csv_file)

# Extract relevant columns and convert to numeric, coercing errors to NaN
x_rem = pd.to_numeric(df.iloc[:, 2], errors="coerce")
x_nrem = pd.to_numeric(df.iloc[:, 1], errors="coerce")
y = pd.to_numeric(df["SAIDifference"], errors="coerce")

# ==========================================
# 2. Helper Functions for Statistics
# ==========================================
def p_to_star(p):
    """Convert p-value to significance asterisks."""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"

def format_p(p):
    """Format p-value for display."""
    if p < 0.001:
        return "< 0.001"
    else:
        return f"= {p:.3f}"

def calc_corr(x, y, name):
    """Calculate Pearson correlation for valid pairs."""
    temp = pd.DataFrame({"x": x, "y": y}).dropna()
    r, p = pearsonr(temp["x"], temp["y"])

    return {
        "comparison": name,
        "n": len(temp),
        "r": r,
        "p_raw": p
    }

# ==========================================
# 3. Statistical Testing & FDR Correction
# ==========================================
# Calculate raw p-values for both correlation analyses
results = [
    calc_corr(x_rem, y, "REM"),
    calc_corr(x_nrem, y, "NREM")
]

results_df = pd.DataFrame(results)

# Apply Benjamini-Hochberg FDR correction
reject, p_fdr, _, _ = multipletests(
    results_df["p_raw"],
    alpha=0.05,
    method="fdr_bh"
)

# Append corrected results to the dataframe
results_df["p_fdr"] = p_fdr
results_df["significant_fdr_0.05"] = reject
results_df["star_raw"] = results_df["p_raw"].apply(p_to_star)
results_df["star_fdr"] = results_df["p_fdr"].apply(p_to_star)

# Display statistical results in console
print("=" * 60)
print(" 🔬 Pearson Correlation & FDR Correction Results ")
print("=" * 60)
print(results_df.to_string(index=False))
print("=" * 60)

# Save statistical results to a CSV file
output_csv = 'FAA_SAI_FDR_results.csv'
results_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
print(f"📊 Stats saved to: {os.path.abspath(output_csv)}")

# ==========================================
# 4. Plotting
# ==========================================
def draw_scatter(ax, x, y, xlabel, title, stats_row):
    """Draw a scatter plot with regression line and statistical annotations."""
    temp = pd.DataFrame({"x": x, "y": y}).dropna()

    sns.regplot(
        data=temp,
        x="x",
        y="y",
        ax=ax,
        scatter_kws={
            "s": 28,
            "color": "#7a7a7a",
            "alpha": 0.85,
            "edgecolor": "none"
        },
        line_kws={
            "color": "black",
            "linewidth": 1.5
        },
        ci=95,
        color="black"
    )

    # Extract statistical values for annotation
    r = stats_row["r"]
    p_raw = stats_row["p_raw"]
    p_fdr = stats_row["p_fdr"]
    star = stats_row["star_raw"]

    # Add text annotations inside the plot
    ax.text(0.62, 0.90, rf"$r$ = {r:.2f}$^{{{star}}}$", transform=ax.transAxes, fontsize=11)
    ax.text(0.62, 0.82, rf"$p$ {format_p(p_raw)}", transform=ax.transAxes, fontsize=10)
    ax.text(0.62, 0.74, rf"$p_{{FDR}}$ {format_p(p_fdr)}", transform=ax.transAxes, fontsize=10)

    # Set labels and title
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel("SAI (After - Before)", fontsize=11)

    # Clean up axes
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(8, 4), dpi=300)

# Plot REM
draw_scatter(
    axes[0],
    x_rem,
    y,
    "FAA (F4 - F3)-REM",
    "REM",
    results_df.loc[results_df["comparison"] == "REM"].iloc[0]
)

# Plot NREM
draw_scatter(
    axes[1],
    x_nrem,
    y,
    "FAA (F4 - F3)-NREM",
    "NREM",
    results_df.loc[results_df["comparison"] == "NREM"].iloc[0]
)

plt.tight_layout()

# Save the figure
output_img = 'FAA_SAI_scatter.svg'
plt.savefig(output_img, dpi=300, bbox_inches="tight")
plt.show()

print(f"🎉 Plot saved to: {os.path.abspath(output_img)}\n")