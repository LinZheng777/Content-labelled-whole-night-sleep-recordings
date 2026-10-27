# -*- coding: utf-8 -*-
"""
Project: PCA-CCA Pipeline for Sleep N3 Objective Metrics and Subjective Reports (Second Night).
Description: Data preprocessing, PCA dimensionality reduction, CCA modeling (CCA1 focus),
             canonical loadings visualization (FDR filtered by V1), and permutation testing.
Author: zhenglin (Optimized for GitLab Submission)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import CCA
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests
from adjustText import adjust_text
from matplotlib.patches import FancyArrowPatch

# ==========================================
# Part 1: Global Plotting Configuration
# ==========================================
sns.set_theme(style="white")
mpl.rcParams.update({
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14
})

# --- Directory and File Paths ---
BASE_DIR = r'Fig.5' #revise your path
FILE_X = os.path.join(BASE_DIR, 'Fig5_second_N3_objective.csv')
FILE_Y = os.path.join(BASE_DIR, 'Fig5_second_N3_subjective.csv')

OUTPUT_DIR = os.path.join(BASE_DIR, 'N3')
os.makedirs(OUTPUT_DIR, exist_ok=True)
night = 'second'

# ==========================================
# Part 2: Data Import & Preprocessing
# ==========================================
neuro_data = pd.read_csv(FILE_X)
questionnaire_data = pd.read_csv(FILE_Y)

# 1. Filter rows with > 50% missing values
def filter_nan(df):
    threshold = df.shape[1] / 2
    return df[df.isnull().sum(axis=1) <= threshold]

plot_neuro = filter_nan(neuro_data)
plot_quality = questionnaire_data.iloc[filter_nan(questionnaire_data).index, :]

# 2. Drop variables with too many zeros (> 33.3%)
zero_counts = plot_quality.eq(0).sum()
cols_mostly_zero = zero_counts[zero_counts > len(plot_quality) / 3].index.tolist()
plot_quality = plot_quality.drop(cols_mostly_zero, axis=1)

# 3. Align subjects between X and Y
common_index = plot_quality.index.intersection(plot_neuro.index)

# 4. Missing value imputation based on age group mean
def fill_by_age(df):
    for c in df.columns:
        if c not in ['subjects', 'age', 'gender']:
            df.loc[:, c] = df.groupby('age')[c].transform(lambda x: x.fillna(x.mean()))
    return df

plot_neuro = fill_by_age(plot_neuro.loc[common_index])
plot_quality = fill_by_age(plot_quality.loc[common_index])

# 5. Remove demographic covariates and standardize (Z-score)
X_raw = plot_neuro.drop(['subjects', 'age', 'gender'], axis=1)
Y_raw = plot_quality.drop(['subjects', 'age', 'gender'], axis=1)

scalar = StandardScaler()
X_std = scalar.fit_transform(X_raw)
Y_std = scalar.fit_transform(Y_raw)

print(f"[*] Preprocessing complete. X shape: {X_std.shape}, Y shape: {Y_std.shape}")

# ==========================================
# Part 3: PCA Dimensionality Reduction & CCA
# ==========================================
n_comp = 5

# 1. PCA Transformation
pca_x = PCA(n_components=n_comp)
pca_y = PCA(n_components=n_comp)

X_pca = pca_x.fit_transform(X_std)
Y_pca = pca_y.fit_transform(Y_std)

print(f"[*] PCA X Variance Explained (5 PCs): {np.sum(pca_x.explained_variance_ratio_) * 100:.2f}%")
print(f"[*] PCA Y Variance Explained (5 PCs): {np.sum(pca_y.explained_variance_ratio_) * 100:.2f}%")

# 2. CCA Modeling on PCA scores
cca = CCA(scale=False, n_components=n_comp)
cca.fit(X_pca, Y_pca)
U, V = cca.transform(X_pca, Y_pca)  # U = Canonical Objective, V = Canonical Subjective

# 3. Calculate observed canonical correlations
obs_results = [spearmanr(U[:, i], V[:, i]) for i in range(n_comp)]
obs_corrs = [res[0] for res in obs_results]
print(f"[*] CCA Correlations: {np.round(obs_corrs, 3)}")

# ==========================================
# Part 4: Visualization 1 - CCA1 Scatter Plot
# ==========================================
fig1, ax1 = plt.subplots(figsize=(6, 5))
sns.regplot(x=U[:, 0], y=V[:, 0], ax=ax1, color='#D46A6A', scatter_kws={'alpha': 0.6})
ax1.set_title(f'CCA1 Correlation (R = {obs_corrs[0]:.3f})')
ax1.set_xlabel('Objective Sleep Profile (U1)')
ax1.set_ylabel('Subjective Sleep Report (V1)')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, f'N3_{night}_CCA1_Scatter.svg'), bbox_inches='tight', dpi=300)
plt.show()

# ==========================================
# Part 5: CCA1 Canonical Loadings & Biplot
# ==========================================
# Utility function to extract correlation loadings mapping back to ORIGINAL features
def get_loadings(data, U_scores, V_scores, comp=0):
    loadings = []
    for i in range(data.shape[1]):
        r_u, p_u = spearmanr(data[:, i], U_scores[:, comp])
        r_v, p_v = spearmanr(data[:, i], V_scores[:, comp])
        loadings.append([r_u, r_v, p_u, p_v])
    return np.array(loadings)

# Calculate statistics for CCA1 using the STANDARDIZED data (X_std, Y_std)
x_stats = get_loadings(X_std, U, V, 0)
y_stats = get_loadings(Y_std, U, V, 0)

# FDR Correction & Export (Export significant variables for CCA1)
res_x = pd.DataFrame(
    {'Variable': X_raw.columns, 'r_with_U': x_stats[:, 0], 'r_with_V': x_stats[:, 1], 'p_with_U': x_stats[:, 2]})
res_x['q_FDR_U'] = multipletests(res_x['p_with_U'], method='fdr_bh')[1]

res_y = pd.DataFrame(
    {'Variable': Y_raw.columns, 'r_with_U': y_stats[:, 0], 'r_with_V': y_stats[:, 1], 'p_with_V': y_stats[:, 3]})
res_y['q_FDR_V'] = multipletests(res_y['p_with_V'], method='fdr_bh')[1]

# --- Figure 2: CCA1 Loadings Biplot ---
xy_loadings = np.vstack((x_stats[:, :2], y_stats[:, :2]))
all_labels = list(X_raw.columns) + list(Y_raw.columns)

fig2, ax2 = plt.subplots(figsize=(9, 7))
max_radius = np.max(np.abs(xy_loadings)) * 1.15
ax2.set_xlim([-max_radius, max_radius])
ax2.set_ylim([-0.8, 0.8])

# Draw reference lines
ax2.axhline(y=0, color='lightgray', linestyle='--', zorder=0)
ax2.axvline(x=0, color='lightgray', linestyle='--', zorder=0)

# Draw arrows and labels (filter out low loadings where abs() < 0.20 for clarity)
texts = []
for idx, (x_coord, y_coord) in enumerate(xy_loadings):
    # Invert directions based on original visual representation logic
    x_coord, y_coord = -x_coord, -y_coord
    if abs(y_coord) >= 0.20:
        arrow = FancyArrowPatch((0, 0), (x_coord, y_coord), color='#CA565C', arrowstyle='fancy', mutation_scale=15, alpha=0.3)
        ax2.add_patch(arrow)
        txt = ax2.text(x_coord + 0.02, y_coord, all_labels[idx], color='#7CB7C0')
        texts.append(txt)

adjust_text(texts, arrowprops=dict(arrowstyle='-', color='none', alpha=0))
ax2.set_xlabel('Canonical Loading on U1')
ax2.set_ylabel('Canonical Loading on V1')
ax2.set_title('N3 CCA1 Variable Loadings Space')
plt.savefig(os.path.join(OUTPUT_DIR, f'{night}_N3_CCA1_Loadings.svg'), bbox_inches='tight', dpi=300)
plt.show()

# ==========================================
# Part 6: Permutation Testing
# ==========================================
print("[*] Performing 10,000 permutation tests, please wait...")
Nperm = 10000
num_rows = Y_pca.shape[0]  # Shuffle based on the PCA arrays
perm_correlations = np.zeros((Nperm, n_comp))

np.random.seed(42)  # Set random seed for reproducibility
for j in range(Nperm):
    idx_x = np.random.permutation(num_rows)
    idx_y = np.random.permutation(num_rows)

    # CCA fit on shuffled PCA scores
    cca_perm = CCA(scale=False, n_components=n_comp, max_iter=1000)
    cca_perm.fit(X_pca[idx_x], Y_pca[idx_y])
    pU, pV = cca_perm.transform(X_pca[idx_x], Y_pca[idx_y])

    for i in range(n_comp):
        perm_correlations[j, i] = spearmanr(pU[:, i], pV[:, i])[0]

# Calculate corrected P-values
final_p_values = [(1 + np.sum(perm_correlations[:, i] >= obs_corrs[i])) / Nperm for i in range(n_comp)]
print(f"[*] Permutation P-values: {np.round(final_p_values, 4)}")

# --- Figure 3: Null Distribution Visualization ---
fig3 = plt.figure(figsize=(7, 5.5))
lower = np.percentile(perm_correlations, 5, axis=0)
upper = np.percentile(perm_correlations, 95, axis=0)

plt.fill_between(range(1, n_comp + 1), lower, upper, color='lightgrey', alpha=0.5, label='Null Range (5-95%)')
plt.plot(range(1, n_comp + 1), obs_corrs, 'o-', color='lightskyblue', lw=2, markersize=8, label='Observed')

plt.title('N3 CCA Permutation Test Results')
plt.xlabel('Canonical Component Index')
plt.ylabel('Canonical Correlation (R)')
plt.xticks(range(1, n_comp + 1))
plt.legend(frameon=True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, f'{night}_N3_Permutation_Null_Dist.svg'), bbox_inches='tight', dpi=300)
plt.show()

print(f"[*] Analysis complete! Core figures and significant CSVs saved to: {OUTPUT_DIR}")