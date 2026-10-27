import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import matplotlib

# Enable exporting editable text in SVG format
plt.rcParams['svg.fonttype'] = 'none'

# ==========================================
# 1. Load Data
# ==========================================
# Using a relative path for easy sharing and GitLab submission
csv_path = 'Fig4f.csv'
df = pd.read_csv(csv_path)

# Extract X and Y data
x_data = df['TST'].values
y_data = df['N3_Global_Percent'].values

# Remove NaN values to prevent errors during statistical calculations
mask = ~np.isnan(x_data) & ~np.isnan(y_data)
x_data = x_data[mask]
y_data = y_data[mask]

# ==========================================
# 2. Statistical Calculations
# ==========================================
# Calculate Pearson correlation coefficient (r) and p-value
r_val, p_val = pearsonr(x_data, y_data)

# Determine significance asterisks automatically
if p_val < 0.001:
    stars = "***"
elif p_val < 0.01:
    stars = "**"
elif p_val < 0.05:
    stars = "*"
else:
    stars = ""

stat_label = f"$r = {r_val:.2f}${stars}"

# ==========================================
# 3. Plotting
# ==========================================
fig, ax = plt.subplots(figsize=(5, 4.5), dpi=120)

# Draw the 95% Confidence Interval and Regression Line using seaborn
# scatter=False prevents seaborn from drawing default points
# color='#7f7f7f' sets the CI shadow to a clean, light gray
sns.regplot(
    x=x_data, y=y_data, ax=ax, ci=95, scatter=False, color='#7f7f7f',
    line_kws={'color': 'black', 'linewidth': 1.8, 'zorder': 3}
)

# Draw the raw data points as a scatter plot layered on top
# edgecolors='white' gives the dots the distinct academic style
ax.scatter(
    x_data, y_data,
    color='#7f7f7f',
    edgecolors='white',
    linewidths=0.8,
    s=50,
    alpha=0.9,
    zorder=4
)

# ==========================================
# 4. Formatting and Beautification
# ==========================================
ax.set_title("Undisturbed night", fontsize=13, fontweight='bold', pad=10)
ax.set_xlabel("Total Sleep Time (min)", fontsize=11, fontweight='bold')
ax.set_ylabel("Global sleep percent - N3 (%)", fontsize=11, fontweight='bold')

# Set specific axis limits and ticks to match the reference image
ax.set_xlim([200, 500])
ax.set_xticks([200, 300, 400, 500])

ax.set_ylim([25, 60])
ax.set_yticks([30, 40, 50, 60])

# Clean up spines (remove top and right borders)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Thicken the remaining spines and turn ticks inward
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)
ax.tick_params(direction='in', width=1.2)

# Add the statistical annotation text to the bottom right
ax.text(420, 27, stat_label, fontsize=12, fontweight='bold', color='black')

# ==========================================
# 5. Export and Show
# ==========================================
plt.tight_layout()

# Save the figure as an SVG
output_img = 'Fig4f_scatter_regression.svg'
plt.savefig(output_img, dpi=300, bbox_inches='tight')
plt.show()

print(f"🎉 Plot successfully generated and saved to:\n   {os.path.abspath(output_img)}")
print(f"Statistics: r = {r_val:.4f}, p = {p_val:.6f}")