%% Script 2: Visualize Group Average Topoplots
clc, clear, close all;

%% ================== 1) LOAD DATA AND EEGLAB ==================
% Ensure EEGLAB is on path for topoplot function
addpath(genpath('J:\script\resource_second_processing\eeglab2023.1'))

data_path = 'Fig.4\Fig4d.mat';  % revise your file path
out_dir   = 'Fig.4';  % revise your file path

load(data_path);

%% ================== 2) COLORMAPS & LIMITS ==================
% Custom Colormaps
cmap_N2  = [linspace(0.8, 0, 256)', linspace(0.9, 0, 256)', linspace(1, 1, 256)'];   % Blue gradient
cmap_N3  = [linspace(1, 1, 256)', linspace(0.9, 0, 256)', linspace(0.9, 0, 256)'];   % Red gradient
cmap_All = parula(256);                                                              % Blue-Yellow gradient

% Determine dynamic maximums for plotting limits
max_Local_All = max(mean_Local_All); if max_Local_All == 0; max_Local_All = 1; end
max_Local_N2  = max(mean_Local_N2);  if max_Local_N2 == 0;  max_Local_N2 = 1;  end
max_Local_N3  = max(mean_Local_N3);  if max_Local_N3 == 0;  max_Local_N3 = 1;  end

max_Global_All = max(mean_Global_All); if max_Global_All == 0; max_Global_All = 1; end
max_Global_N2  = max(mean_Global_N2);  if max_Global_N2 == 0;  max_Global_N2 = 1;  end
max_Global_N3  = max(mean_Global_N3);  if max_Global_N3 == 0;  max_Global_N3 = 1;  end

%% ================== 3) PLOT LOCAL SO DISTRIBUTION ==================
fprintf('🎨 Plotting LOCAL Slow Wave Group Average...\n');
fig_local = figure('Color', 'w', 'Position', [100, 100, 1500, 450]);

% N2
subplot(1, 3, 1);
topoplot(mean_Local_N2, locs_to_plot, 'maplimits', [0, max_Local_N2], 'colormap', cmap_N2, 'numcontour', 8);
title('LOCAL: N2 Stage', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'SO Proportion (%)', 'FontSize', 12, 'FontWeight', 'bold');

% N3
subplot(1, 3, 2);
topoplot(mean_Local_N3, locs_to_plot, 'maplimits', [0, max_Local_N3], 'colormap', cmap_N3, 'numcontour', 8);
title('LOCAL: N3 Stage', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'SO Proportion (%)', 'FontSize', 12, 'FontWeight', 'bold');

% Total NREM
subplot(1, 3, 3);
topoplot(mean_Local_All, locs_to_plot, 'maplimits', [0, max_Local_All], 'colormap', cmap_All, 'numcontour', 8);
title('LOCAL: Total NREM', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'SO Proportion (%)', 'FontSize', 12, 'FontWeight', 'bold');

sgtitle(sprintf('Group Average LOCAL Slow Wave Distribution (N = %d)', num_subs), 'FontSize', 20, 'FontWeight', 'bold');

% Save Local SVG
file_local = fullfile(out_dir, 'Group_Average_LOCAL_SO_Distribution_rel_first.svg');
print(fig_local, file_local, '-dsvg', '-painters'); 
fprintf('✅ Local plot saved: %s\n', file_local);

%% ================== 4) PLOT GLOBAL SO DISTRIBUTION ==================
fprintf('🎨 Plotting GLOBAL Slow Wave Group Average...\n');
fig_global = figure('Color', 'w', 'Position', [100, 600, 1500, 450]);

% N2
subplot(1, 3, 1);
topoplot(mean_Global_N2, locs_to_plot, 'maplimits', [0, max_Global_N2], 'colormap', cmap_N2, 'numcontour', 8);
title('GLOBAL: N2 Stage', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'SO Proportion (%)', 'FontSize', 12, 'FontWeight', 'bold');

% N3
subplot(1, 3, 2);
topoplot(mean_Global_N3, locs_to_plot, 'maplimits', [0, max_Global_N3], 'colormap', cmap_N3, 'numcontour', 8);
title('GLOBAL: N3 Stage', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'SO Proportion (%)', 'FontSize', 12, 'FontWeight', 'bold');

% Total NREM
subplot(1, 3, 3);
topoplot(mean_Global_All, locs_to_plot, 'maplimits', [0, max_Global_All], 'colormap', cmap_All, 'numcontour', 8);
title('GLOBAL: Total NREM', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'SO Proportion (%)', 'FontSize', 12, 'FontWeight', 'bold');

sgtitle(sprintf('Group Average GLOBAL Slow Wave Distribution (N = %d)', num_subs), 'FontSize', 20, 'FontWeight', 'bold');

% Save Global SVG
file_global = fullfile(out_dir, 'Group_Average_GLOBAL_SO_Distribution_rel_first.svg');
print(fig_global, file_global, '-dsvg', '-painters'); 
fprintf('✅ Global plot saved: %s\n', file_global);

fprintf('=========================================================================\n');
fprintf('🎉 All topographic maps successfully generated and saved!\n');