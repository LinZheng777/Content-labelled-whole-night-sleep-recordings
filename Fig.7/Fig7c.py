import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.text as mtext
import mne
import os

# ================= 1. 设置全局绘图字体 =================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['svg.fonttype'] = 'none'

# ================= 2. 配置文件路径和条件 =================
# 你截图里的文件夹路径
data_dir = r'I:\second_resource\code_submit\Fig.7'

# 根据你截图里的 CSV 文件名，定义四个条件
conditions = ['REM', 'NREM', 'Aud', 'Img']
csv_files = [f'Fig7c_{cond}.csv' for cond in conditions]

# ================= 3. 创建 1 行 4 列的大画布 =================
# figsize=(24, 5) 确保每个子图有足够的横向空间，不会挤在一起
fig, axes = plt.subplots(1, 4, figsize=(24, 5))

# 统一的 Y 轴范围，方便直接对比不同条件的波幅大小
ylim_dict = dict(eeg=[-21, 10])

# ================= 4. 循环读取并绘图 =================
for i, (cond, csv_file) in enumerate(zip(conditions, csv_files)):
    file_path = os.path.join(data_dir, csv_file)
    ax = axes[i]

    try:
        # --- A. 读取 CSV 数据 ---
        # index_col=0 表示第一列（如 F3, F4, C3...）作为索引通道名
        df = pd.read_csv(file_path, index_col=0)

        ch_names = df.index.tolist()
        data_matrix = df.values
        times = df.columns.astype(float).values

        # --- B. 还原为 MNE 的轻量级 Evoked 对象 (纯画图用) ---
        # 根据两个时间点的时间差，自动计算采样率 (如 0.01s 差值就是 100Hz)
        sfreq = 1.0 / (times[1] - times[0])
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
        evoked = mne.EvokedArray(data_matrix, info, tmin=times[0])

        # 赋予标准电极坐标，这样 MNE 才能画出左上角的彩色头皮标
        evoked.set_montage('standard_1020', match_case=False, on_missing='ignore')

        # --- C. 绘制子图 ---
        evoked.plot(
            axes=ax,
            spatial_colors=True,
            ylim=ylim_dict,
            time_unit='s',
            show=False,
            titles=f'{cond}'  # 设置子图标题
        )

        # 为了让并排图看起来更干净，只保留最左侧 (REM) 的 Y 轴 μV 标签
        if i > 0:
            ax.set_ylabel('')

    except Exception as e:
        print(f"❌ 处理 {cond} 时出错: {e}")



plt.tight_layout()

# ================= 6. 保存最终成品图 =================
output_path = os.path.join(data_dir, 'Fig7c_Combined_Waveforms.svg')
fig.savefig(output_path, format='svg', transparent=True, bbox_inches='tight')
print(f"✅ 1行4列汇总蝴蝶图已生成: {output_path}")

plt.show()