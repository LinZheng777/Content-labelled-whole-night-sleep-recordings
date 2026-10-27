import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# Enable exporting editable text in SVG format
plt.rcParams['svg.fonttype'] = 'none'

# ==========================================
# 1. Basic Settings and Data Loading
# ==========================================
# Assuming Fig6a.csv is in the same directory as this script
csv_file = 'Fig6a.csv'
df = pd.read_csv(csv_file)

sns.set_theme(style="ticks", context="talk")

# Core metrics to analyze and plot
metrics_config = {
    'FAA (F4 minus F3)': [
        'FAA (F4 F3) NREM',
        'FAA (F4 F3) REM'
    ],
    'Relative Theta Fz': [
        'Rel Theta Power NREM',
        'Rel Theta Power REM'
    ],
    'Theta/Alpha Ratio Max': [
        'Theta Alpha Ratio NREM',
        'Theta Alpha Ratio REM'
    ]
}

# ==========================================
# 2. Outlier Removal Function (IQR Method)
# ==========================================
def remove_outliers_iqr(dataframe, columns):
    df_clean = dataframe.copy()
    for col in columns:
        if col in df_clean.columns:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            # Identify outliers beyond the threshold and set them to NaN
            outlier_mask = (df_clean[col] < (Q1 - 1.5 * IQR)) | (df_clean[col] > (Q3 + 1.5 * IQR))
            df_clean.loc[outlier_mask, col] = np.nan
    return df_clean

# Extract all target feature columns for cleaning
all_plot_cols = [col for cols in metrics_config.values() for col in cols]
df_cleaned = remove_outliers_iqr(df, all_plot_cols)

# ==========================================
# 3. Statistical Testing (Paired t-test + FDR Correction)
# ==========================================
stats_results = []
conditions_order = ['NREM', 'REM']

# Collect all p-values
for title, cols in metrics_config.items():
    pairs = [('NREM vs REM', cols[0], cols[1])]

    for pair_name, col1, col2 in pairs:
        # Only use valid paired data (excluding rows with NaNs in either column)
        df_pair = df_cleaned[[col1, col2]].dropna()
        if len(df_pair) > 2:
            t_stat, p_val = stats.ttest_rel(df_pair[col1], df_pair[col2])
            mean1, se1 = df_pair[col1].mean(), df_pair[col1].sem()
            mean2, se2 = df_pair[col2].mean(), df_pair[col2].sem()
            stats_results.append({
                'Metric': title, 'Pair': pair_name, 'N': len(df_pair),
                't_stat': t_stat, 'p_uncorr': p_val,
                'Desc': f"{mean1:.3f}±{se1:.3f} vs {mean2:.3f}±{se2:.3f}"
            })

df_stats = pd.DataFrame(stats_results)

# Perform Benjamini-Hochberg FDR correction
pvals = df_stats['p_uncorr'].values
n_tests = len(pvals)
sort_ind = np.argsort(pvals)
qvals = np.zeros(n_tests)
for i, p in enumerate(pvals[sort_ind]):
    qvals[sort_ind[i]] = p * n_tests / (i + 1)

for i in range(n_tests - 2, -1, -1):
    qvals[sort_ind[i]] = min(qvals[sort_ind[i]], qvals[sort_ind[i + 1]])
df_stats['p_FDR'] = np.minimum(qvals, 1.0)


# Generate significance asterisks
def get_stars(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    return "ns"

df_stats['Significance'] = df_stats['p_FDR'].apply(get_stars)

# Print highly readable statistical report to the console
print("=" * 80)
print(" 🔬 Core EEG Metrics: Paired Sample t-test Report (SE & FDR Corrected) ")
print("=" * 80)
for metric in df_stats['Metric'].unique():
    print(f"\n▶ [{metric}]")
    sub_df = df_stats[df_stats['Metric'] == metric]
    for _, row in sub_df.iterrows():
        print(f"  ➤ {row['Pair']} (n={row['N']})")
        print(f"     Mean±SE : {row['Desc']}")
        print(
            f"     Stats   : t = {row['t_stat']:.3f}, p_raw = {row['p_uncorr']:.2e}, p_FDR = {row['p_FDR']:.2e}  {row['Significance']}")
print("\n" + "=" * 80)

# ==========================================
# 4. Plot Advanced Offset Scatter Plot (Mean ± SE)
# ==========================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, (title, cols) in enumerate(metrics_config.items()):
    df_sub = df_cleaned[cols].dropna()
    df_melt = df_sub.melt(value_vars=cols, var_name='Condition', value_name='Value')

    # Extract the last word of the string as Condition (NREM/REM)
    df_melt['Condition'] = df_melt['Condition'].apply(lambda x: x.split(' ')[-1])

    # 1. Bottom layer: Plot jittered scatter of raw data
    sns.stripplot(data=df_melt, x='Condition', y='Value', order=conditions_order,
                  ax=axes[i], color='gray', alpha=0.35, jitter=0.12, zorder=1)

    # Calculate Mean and Standard Error (SE) for each condition
    means = [df_melt[df_melt['Condition'] == cond]['Value'].mean() for cond in conditions_order]
    ses = [df_melt[df_melt['Condition'] == cond]['Value'].sem() for cond in conditions_order]

    # 2. Right side connection: Offset Mean and SE to the right by 0.25 units
    x_coords = np.arange(len(conditions_order))
    offset = 0.25

    # Plot error bars with connecting lines
    axes[i].errorbar(x_coords + offset, means, yerr=ses,
                     fmt='-D', color='#D81B60', markersize=8,
                     linewidth=2.5, capsize=6, capthick=2, zorder=2)

    # Aesthetic details
    axes[i].set_title(title, fontweight='bold', pad=15)
    axes[i].set_xlabel('')
    axes[i].set_xlim(-0.5, 1.7)

    if i == 0:
        axes[i].set_ylabel('Asymmetry Score')
    elif i == 1:
        axes[i].set_ylabel('Relative Power')
    else:
        axes[i].set_ylabel('Ratio Value')

    sns.despine(ax=axes[i])

plt.tight_layout()

# Save using a relative path so it generates in the same directory for anyone pulling from GitLab
output_img = 'rem_nrem_dot_second.svg'
plt.savefig(output_img, dpi=300, bbox_inches='tight')
plt.show()

print(f"\n🎉 Plot generated successfully! The chart (NREM & REM only) has been saved to:\n   {os.path.abspath(output_img)}")