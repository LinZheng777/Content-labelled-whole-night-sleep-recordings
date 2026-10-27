import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib

# Set backend (Optional: Note that 'TKAgg' might cause issues in headless CI/CD environments)
matplotlib.use('TKAgg')

# Enable exporting editable text in SVG format
plt.rcParams['svg.fonttype'] = 'none'

# ==========================================
# 1. Load Data
# ==========================================
# Use a relative path so the script works out-of-the-box for all collaborators
csv_file = 'fig6b.csv'
df = pd.read_csv(csv_file)

col_before = 'SAIBeforeSleep'
col_after = 'SAIAfterSleep'

# Clean data (drop rows with missing values in the target columns)
df_clean = df[[col_before, col_after]].dropna()
data_before = df_clean[col_before].values
data_after = df_clean[col_after].values

# ==========================================
# 2. Statistical Testing (Paired Sample t-test)
# ==========================================
t_stat, p_val = stats.ttest_rel(data_before, data_after)
df_t = len(data_before) - 1
mean_before, se_before = np.mean(data_before), stats.sem(data_before)
mean_after, se_after = np.mean(data_after), stats.sem(data_after)

# Determine significance asterisks
if p_val < 0.001: sig_star = '***'
elif p_val < 0.01: sig_star = '**'
elif p_val < 0.05: sig_star = '*'
else: sig_star = 'ns'

# ==========================================
# 3. Plot Advanced Jittered Scatter Plot
# ==========================================
fig, ax = plt.subplots(figsize=(6, 6))

x_before = 1
x_after = 2

# Add jitter to the x-axis to prevent points from overlapping
jitter_b = np.random.normal(0, 0.04, size=len(data_before))
jitter_a = np.random.normal(0, 0.04, size=len(data_after))

# Plot raw data points (Jittered scatter, no paired lines)
ax.scatter(np.repeat(x_before, len(data_before)) + jitter_b, data_before,
           color='#A9A9A9', alpha=0.6, s=50, edgecolor='w', zorder=1)
ax.scatter(np.repeat(x_after, len(data_after)) + jitter_a, data_after,
           color='#A9A9A9', alpha=0.6, s=50, edgecolor='w', zorder=1)

# Plot group means and standard errors (offset slightly to avoid obscuring scatter points)
ax.errorbar([x_before - 0.2, x_after + 0.2], [mean_before, mean_after],
            yerr=[se_before, se_after], fmt='-D', color='#D81B60',
            markersize=8, linewidth=2.5, capsize=6, capthick=2, zorder=2)

# ------------------------------------------
# Chart formatting and beautification
# ------------------------------------------
ax.set_xticks([x_before, x_after])
ax.set_xticklabels(['Before Sleep', 'After Sleep'], fontsize=14, fontweight='bold')
ax.set_ylabel('State Anxiety Inventory (SAI)', fontsize=14, fontweight='bold')

# Set dynamic axis limits based on data range
ax.set_xlim(0.4, 2.6)
y_min = min(min(data_before), min(data_after)) - 5
y_max = max(max(data_before), max(data_after)) + 5
ax.set_ylim(y_min, y_max)

# Add statistical results to the title
ax.set_title(f'Change in State Anxiety\n(t = {t_stat:.2f}, p = {p_val:.3f} {sig_star})',
             fontsize=16, fontweight='bold', pad=15)

# Clean up spines (remove top/right, thicken left/bottom)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)
ax.tick_params(width=1.5, labelsize=12)

plt.tight_layout()

# ==========================================
# 4. Save and Show Figure
# ==========================================
# Use relative path for saving output
output_img = 'SAI_before_after_dots.svg'
plt.savefig(output_img, dpi=300, bbox_inches='tight')
plt.show()

# Print statistical summary to console
print(f"🎉 Plot generated successfully! The scatter plot has been saved to:\n   {os.path.abspath(output_img)}")
print("-" * 50)
print(f"Statistical Results: t({df_t}) = {t_stat:.4f}, p = {p_val:.6f}")
print("-" * 50)