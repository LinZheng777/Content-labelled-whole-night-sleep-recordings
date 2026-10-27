import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import os

# --- 1. 设置全局绘图参数 ---
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.family'] = 'Arial'
# 设置随机种子，确保每次运行散点的抖动位置一致
np.random.seed(42)

# --- 2. 数据准备 ---
categories = ["Pre-SO", "Trans-1st-Up", "1st-Up", "Trans-Down", "Down", "Trans-2nd-Up", "2nd-Up", "Post-SO"]

data_dict = {
    'Pre-SO': [28.440367, 13.157895, 17.391304, 21.428571, 18.421053, 28.915663, 21.212121, 24.460432, 28.961749,
               21.008403, 25.0, 20.481928],
    'Trans-1st-Up': [33.333333, 44.186047, 32.258065, 36.170213, 41.176471, 30.864198, 33.544304, 41.346154, 34.745763,
                     46.728972, 38.157895, 33.333333],
    '1st-Up': [25.0, 21.428571, 14.285714, 25.454545, 32.075472, 14.814815, 32.222222, 31.764706, 28.387097, 32.53012,
               26.984127, 29.032258],
    'Trans-Down': [16.216216, 7.692308, 17.857143, 20.0, 33.333333, 30.0, 16.27907, 37.209302, 20.0, 16.0, 50.0,
                   22.222222],
    'Down': [24.528302, 12.5, 23.684211, 21.333333, 14.285714, 9.375, 13.636364, 15.555556, 25.806452, 16.27907, 31.25,
             10.526316],
    'Trans-2nd-Up': [24.489796, 42.857143, 25.0, 16.981132, 33.333333, 23.809524, 19.71831, 33.333333, 28.378378,
                     42.105263, 33.333333, 38.461538],
    '2nd-Up': [20.37037, 31.578947, 26.086957, 25.0, 40.0, 26.415094, 18.421053, 26.923077, 27.058824, 21.333333,
               17.948718, 16.071429],
    'Post-SO': [12.244898, 20.0, 23.684211, 19.130435, 23.076923, 17.948718, 9.375, 17.307692, 22.222222, 30.434783,
                16.666667, 16.981132]
}

colors = {
    "Post-SO": '#88C6FB', "2nd-Up": '#C41C1F', "Trans-2nd-Up": '#E85E61', "Down": '#004ECB',
    "Trans-Down": '#88C6FB', "1st-Up": '#C41C1F', "Trans-1st-Up": '#E85E61', 'Pre-SO': "#9294A0"
}

# --- 3. 统计检验输出 ---
print("--- Statistical Tests ---")
print("Trans-1st-Up vs 1st-Up:", scipy.stats.ttest_rel(data_dict["Trans-1st-Up"], data_dict["1st-Up"]))
# (保留需要的统计输出... 这里为简洁省略部分print)

# --- 4. 计算均值和标准误 ---
bar_dict = {}
for key in categories:
    origin_data = np.asarray(data_dict[key])
    new_data = [
        np.mean(origin_data),
        scipy.stats.sem(origin_data, axis=0, ddof=1, nan_policy='propagate')
    ]
    bar_dict[key] = new_data

# --- 5. 开始绘图 ---
plt.figure(figsize=(9, 7))

bar_positions = np.arange(len(categories))

for i, category in enumerate(categories):
    current_pos = bar_positions[i]
    mean_val = bar_dict[category][0]
    sem_val = bar_dict[category][1]
    individual_points = np.array(data_dict[category])
    color_val = colors[category]

    # 层1: 个体散点图 (Scatter with Jitter)
    jitter = np.random.uniform(-0.12, 0.12, size=len(individual_points))
    plt.scatter(current_pos + jitter, individual_points,
                s=35,
                color=color_val,
                alpha=0.8,
                edgecolor='white', linewidth=0.8,
                zorder=1)

    # 层2: 误差棒和均值点 (Errorbar & Mean marker)
    plt.errorbar(current_pos, mean_val, yerr=sem_val,
                 fmt='none', ecolor='black',
                 elinewidth=2.5, capsize=8, capthick=2.5,
                 zorder=2)

    plt.plot(current_pos, mean_val, marker='o', color='black',
             markersize=6, zorder=2)

# --- 6. 图表美化 ---
ax = plt.gca()
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)

plt.ylabel('Accuracy (%)', fontdict={'size': 22, 'weight': 'bold'})
plt.ylim((5, 55))
plt.tick_params(axis='y', width=2, length=8, labelsize=16)

xtick_labels = ["Pre\nSO", "Trans\n1st-Up", "1st\nUp", "Trans\nDown", "Down", "Trans\n2nd-Up", "2nd\nUp", "Post\nSO"]
plt.xticks(bar_positions, xtick_labels, fontsize=16, weight='bold')
plt.tick_params(axis='x', width=2, length=8)

plt.tight_layout()

# 保存路径 (修改为当前目录的相对路径，适合 GitHub 开源)
figure_save_path = './Figure3b_decoding_scatter.svg'
plt.savefig(figure_save_path, format='svg', transparent=True)
plt.show()