%% Script 2: Visualize Group Average Global Propagation Delay
clc, clear, close all;

%% ================== 1) LOAD DATA AND EEGLAB ==================
% Ensure EEGLAB is on path for the topoplot function
addpath(genpath('J:\script\resource_second_processing\eeglab2023.1'))

% Using relative path for the output directory
data_path = 'Fig.4\Fig4e.mat'; % revise your file path
out_dir   = 'Fig.4'; % revise your file path

load(data_path);

%% ================== 2) COLORMAPS & LIMITS ==================
% Delay Colormap: Blue indicates early (0ms), Yellow indicates late
cmap_delay = parula(256); 

% Set unified colorbar limits to ensure the scale is consistent across both plots
global_max = max([mean_delay_global_N2, mean_delay_global_N3]);
if global_max <= 0; global_max = 1; end % Failsafe
c_limits = [0, global_max];

%% ================== 3) PLOTTING ==================
fprintf('🎨 Plotting GLOBAL Propagation Delay Group Average...\n');
% Create a figure optimized for a 1x2 layout
fig = figure('Color', 'w', 'Position', [100, 100, 1000, 450]);

% --- Left: Global N2 Delay ---
subplot(1, 2, 1);
topoplot(mean_delay_global_N2, locs_to_plot, 'maplimits', c_limits, 'colormap', cmap_delay, 'numcontour', 8);
title('GLOBAL: N2 Delay', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'Delay (ms)', 'FontSize', 12, 'FontWeight', 'bold');

% --- Right: Global N3 Delay ---
subplot(1, 2, 2);
topoplot(mean_delay_global_N3, locs_to_plot, 'maplimits', c_limits, 'colormap', cmap_delay, 'numcontour', 8);
title('GLOBAL: N3 Delay', 'FontSize', 16, 'FontWeight', 'bold');
ylabel(colorbar, 'Delay (ms)', 'FontSize', 12, 'FontWeight', 'bold');

% Add a main title for the figure
sgtitle(sprintf('Group Average GLOBAL Propagation Delay (N = %d)', num_subs), 'FontSize', 20, 'FontWeight', 'bold');

%% ================== 4) EXPORT ==================
file_name = fullfile(out_dir, 'Group_Average_GLOBAL_Delay_first.svg');
% Save as SVG, preserving editable text and vector quality
print(fig, file_name, '-dsvg', '-painters'); 

fprintf('✅ GLOBAL Delay Topoplot successfully generated and saved to:\n   %s\n', file_name);
fprintf('=========================================================================\n');