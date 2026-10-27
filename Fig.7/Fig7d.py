import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import os

# --- 1. 全局样式设置 ---
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.family'] = 'Arial'
np.random.seed(42)

# --- 2. 原始数据 ---
categories = ['N2N3', 'REM']
partitions = ['Lasso GLM', 'LSTM', 'CNN', 'Transformer', 'SI-SD', 'SI-MD']

data_dict = {
    'N2N3': [[11.9, 9.88, 11.69, 13.82, 10.59, 9.86, 11.21, 10.86, 10.95, 11.61, 9.04, 12.99],
             [17, 17.92, 16, 14.64, 19.07, 15.86, 17.16, 18.11, 19.25, 18.23, 17.09, 17.29],
             [20.73, 19.33, 17.44, 18.36, 20.47, 19.18, 19.76, 18.8, 20.55, 20.3, 17.09, 20.04],
             [23.24, 19.98, 18.1, 17.09, 18.37, 19.71, 19.65, 18.61, 20.48, 20.63, 18.75, 22.2],
             [22.33, 19.97, 19.73, 21.12, 19.94, 20.86, 19.4, 21.69, 23.7, 19.51, 21.12, 23.48],
             [23.97, 24.0, 21.28, 20.82, 22.19, 23.39, 22.14, 21.41, 26.15, 22.14, 21.48, 26.07]],

    'REM':  [[12.94, 11.19, 10.13, 13.69, 9.65, 8.57, 10.14, 13.45, 13.3, 10.92, 6.67, 15.96],
             [9.07, 10.73, 10.17, 12.53, 12.92, 11.64, 13.26, 9.09, 15.91, 10.68, 9.68, 10.56],
             [16.35, 15.08, 17.26, 12.8, 13.82, 6.81, 14.7, 15.81, 20.6, 13.66, 14.41, 15.79],
             [12.94, 16.97, 15.93, 12.85, 14.47, 9.52, 14.24, 15.13, 19.31, 12.66, 16.08, 19.47],
             [17.39, 17.26, 17.62, 12.65, 16.09, 8.57, 14.31, 15.74, 21.24, 14.94, 17.75, 19.01],
             [18.24, 21.66, 18.06, 20.11, 19.74, 7.62, 17.97, 26.05, 28.20, 15.72, 18.75, 19.15]]
}

colors = {
    'N2N3': ['#9294A0', '#C2EABA', '#18C994', '#0093F5', '#FE5D26', '#DF3901'],
    'REM':  ['#9294A0', '#C2EABA', '#18C994', '#0093F5', '#FE5D26', '#DF3901']
}

# --- 3. 绘图准备 ---
plt.figure(figsize=(12, 8))
bar_width = 0.22
category_spacing = 2.0
xticks_position = []
xticks_labels = []

# --- 4. 循环绘制 ---
for i, category in enumerate(categories):
    base_pos = i * category_spacing

    for j, partition in enumerate(partitions):
        current_x = base_pos + j * (bar_width + 0.05)
        xticks_position.append(current_x)
        xticks_labels.append(partition)

        raw_values = np.array(data_dict[category][j])
        mean_val = np.mean(raw_values)
        sem_val = scipy.stats.sem(raw_values)
        color = colors[category][j]

        # A. 绘制个体散点 (带有抖动)
        jitter = np.random.uniform(-0.06, 0.06, size=len(raw_values))
        plt.scatter(current_x + jitter, raw_values,
                    color=color, s=20, alpha=0.7, edgecolor='white', linewidth=0.5, zorder=1)

        # B. 绘制误差棒
        plt.errorbar(current_x, mean_val, yerr=sem_val,
                     fmt='none', ecolor='black', capsize=4, elinewidth=1.5, capthick=1.5, zorder=2)

        # C. 绘制均值点
        plt.plot(current_x, mean_val, marker='o', markersize=4, color='black', zorder=3)

# --- 5. 图表修饰 ---
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

# 绘制 Chance Level
plt.axhline(y=6.67, ls=":", c="black", linewidth=1.5, zorder=0)
plt.text(x=-0.1, y=7.2, s='chance level', fontsize=12, fontweight='bold')

plt.ylabel('Decoding Accuracies (%)', fontsize=20, fontweight='bold')
plt.title('Zeroshot Decoding Accuracies (N2N3 vs REM)', fontsize=22, fontweight='bold', pad=20)

plt.xticks(xticks_position, xticks_labels, rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=14)

# 添加大类别标签 (N2N3 / REM)
for i, category in enumerate(categories):
    center_pos = i * category_spacing + (len(partitions) - 1) * (bar_width + 0.05) / 2
    plt.text(center_pos, -6, category, fontsize=18, fontweight='bold', ha='center')

plt.ylim(0, 35)
plt.tick_params(width=1.5, length=7)
plt.tight_layout()

# 保存并显示 (修改为当前目录的相对路径)
figure_save_path = "./Grouped_Zeroshot_Decoding_Scatter.svg"
plt.savefig(figure_save_path, format='svg', dpi=300)
plt.show()