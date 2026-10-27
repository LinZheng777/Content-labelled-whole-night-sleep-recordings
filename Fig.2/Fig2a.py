import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Make SVG text editable
plt.rcParams['svg.fonttype'] = 'none'

# ---------------------------------------------------------------------
# Input data
# ---------------------------------------------------------------------
# The CSV file should be placed in the same folder as this script.
# If running the script from another working directory, replace this
# relative path with the absolute path to the CSV file, e.g.:
# data_file_path = r'I:\second_resource\code_submit\Fig.2\Fig2a.csv'
script_dir = Path(__file__).resolve().parent
data_file_path = script_dir / 'Fig2a.csv'

df = pd.read_csv(data_file_path)

# ---------------------------------------------------------------------
# Data cleaning and reshaping
# ---------------------------------------------------------------------
cols_to_plot = {
    'W/N1 percent (%)': 'W/N1',
    'N2 percent (%)': 'N2',
    'N3 percent (%)': 'N3',
    'REM percent (%)': 'REM'
}

# Calculate NREM2/3
df['NREM2/3'] = df['N2 percent (%)'] + df['N3 percent (%)']

df_long = df.melt(
    id_vars=['subjects'],
    value_vars=cols_to_plot.keys(),
    var_name='Original_Col',
    value_name='Percent'
)

df_long['Stage'] = df_long['Original_Col'].map(cols_to_plot)

# ---------------------------------------------------------------------
# Plot 1: All sleep stages
# ---------------------------------------------------------------------
sns.set_context("paper", font_scale=1.5)
sns.set_style("ticks")

np.random.seed(42)  # Fix jittered scatter locations for reproducible plotting

plt.figure(figsize=(6, 9))

sns.stripplot(
    x='Stage', y='Percent', data=df_long,
    jitter=0.2, size=6, color='gray', alpha=0.6, zorder=0
)

sns.pointplot(
    x='Stage', y='Percent', data=df_long,
    estimator=np.mean, errorbar='se', join=False, capsize=0.15,
    color='black', markers='_', scale=1.2,
    err_kws={'linewidth': 2}, zorder=10
)

plt.ylabel('Percent (%)', fontweight='bold')
plt.xlabel('Expert staging', fontweight='bold')
sns.despine()
plt.ylim(0, 100)

plt.tight_layout()

# Output path. By default, the figure is saved in the same folder as this script.
output_path = script_dir / 'Fig2a_sleep_stage_distribution.svg'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

# ---------------------------------------------------------------------
# Plot 2: NREM2/3 vs REM
# ---------------------------------------------------------------------
df_b = df.melt(
    id_vars=['subjects'],
    value_vars=['NREM2/3', 'REM percent (%)'],
    var_name='Original_Col',
    value_name='Percent'
)

label_mapping = {
    'NREM2/3': 'NREM2/3',
    'REM percent (%)': 'REM'
}

df_b['Stage'] = df_b['Original_Col'].map(label_mapping)

np.random.seed(42)

plt.figure(figsize=(6, 9))

sns.stripplot(
    x='Stage', y='Percent', data=df_b,
    jitter=0.2, size=6, color='gray', alpha=0.6, zorder=0
)

sns.pointplot(
    x='Stage', y='Percent', data=df_b,
    estimator=np.mean, errorbar='se', join=False, capsize=0.15,
    color='black', markers='_', scale=1.2,
    err_kws={'linewidth': 2}, zorder=10
)

plt.ylabel('Percent (%)', fontweight='bold', fontsize=14)
plt.xlabel('Ratio of NREM2/3 and REM', fontweight='bold', fontsize=14)
plt.ylim(0, 100)
sns.despine()

plt.tight_layout()

output_path = script_dir / 'Fig2a_nrem23_rem_distribution.svg'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()