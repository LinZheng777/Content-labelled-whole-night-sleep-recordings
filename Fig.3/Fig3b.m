%% Fig3_time_frequency_spectrogram.m
% -------------------------------------------------------------------------
% Project: Time-Frequency Spectrogram Visualization
% Description: Loads group-averaged time-frequency data from a .mat file 
%              and plots publication-ready spectrograms for N3 and N2 
%              using custom gradient colormaps.
% Optimized for GitLab repository submission.
% -------------------------------------------------------------------------

clear; clc; close all;

%% 1. Configuration and Data Loading

% Define file path (Adjust as needed for your repository structure)
data_file = fullfile('Fig.3', 'Fig3b.mat');

% Verify file existence before attempting to load
if ~exist(data_file, 'file')
    error('[!] Data file not found: %s. Please check the path.', data_file);
end

fprintf('[*] Loading time-frequency data from: %s\n', data_file);
load(data_file, 'grand_TF_N2', 'grand_TF_N3', 'time_tf', 'freq_tf');

%% 2. Generate Custom Colormaps
% Call the local function to keep the main script clean
[cmap_red_N3, cmap_blue_N2] = create_custom_colormaps(256);

%% 3. Plotting Setup

% Initialize figure with specific dimensions and white background
fig = figure('Name', 'Time-Frequency Spectrogram', ...
             'Position', [100, 100, 900, 400], ...
             'Color', 'w');

% Define uniform color limits for valid comparison between stages
c_limits = [0, 0.3]; 

%% 4. Plot N3 Spectrogram (Left Side, Red Colormap)
ax1 = subplot(1, 2, 1);
imagesc(time_tf, freq_tf, grand_TF_N3);
axis xy; % Correct the Y-axis direction for frequencies

colormap(ax1, cmap_red_N3);
caxis(ax1, c_limits);

% Axes formatting
xlim([-1.5 1.5]);
ylim([2 25]);
xlabel('Time (s)', 'FontWeight', 'bold');
ylabel('Frequency (Hz)', 'FontWeight', 'bold');
title('Time-frequency results of all Slow oscillations (N3)', 'FontWeight', 'normal');

% Aesthetics
set(ax1, 'FontSize', 12, 'TickDir', 'out', 'Box', 'off', 'LineWidth', 1.2);

%% 5. Plot N2 Spectrogram (Right Side, Blue Colormap)
ax2 = subplot(1, 2, 2);
imagesc(time_tf, freq_tf, grand_TF_N2);
axis xy;

colormap(ax2, cmap_blue_N2);
caxis(ax2, c_limits);

% Axes formatting (Hide Y-axis label to avoid redundancy)
xlim([-1.5 1.5]);
ylim([2 25]);
xlabel('Time (s)', 'FontWeight', 'bold');
title('(N2)', 'FontWeight', 'normal');

% Aesthetics
set(ax2, 'FontSize', 12, 'TickDir', 'out', 'Box', 'off', 'LineWidth', 1.2, 'YTickLabel', []);

%% 6. Colorbar Configuration
% Attach colorbar to the second axes but position it outside
cb = colorbar(ax2, 'eastoutside');
cb.Label.String = 'Power (Z)';
cb.Label.FontWeight = 'bold';
cb.Ticks = [0, 0.15, 0.3];
cb.LineWidth = 1.2;

fprintf('[*] Plotting successfully completed.\n');

%% ========================================================================
% Local Functions
% ========================================================================

function [cmap_red, cmap_blue] = create_custom_colormaps(n_colors)
    % CREATE_CUSTOM_COLORMAPS Generates specific red and blue gradient colormaps.
    %
    % Inputs:
    %   n_colors - Total number of colors in the map (e.g., 256)
    %
    % Outputs:
    %   cmap_red  - N x 3 RGB matrix for the red colormap
    %   cmap_blue - N x 3 RGB matrix for the blue colormap

    % Calculate lengths for white/fade region and solid color region
    white_len = round(n_colors * 0.4 / 0.9);
    color_len = n_colors - white_len;

    % Generate white/faded base
    white_part_red  = [ones(white_len, 1)*255, ones(white_len, 1)*250, ones(white_len, 1)*250];
    white_part_blue = [ones(white_len, 1)*250, ones(white_len, 1)*255, ones(white_len, 1)*255];

    % Generate gradient color transitions
    red_part  = [linspace(255, 202, color_len)', linspace(250,  86, color_len)', linspace(250,  92, color_len)'];
    blue_part = [linspace(250,  78, color_len)', linspace(255, 160, color_len)', linspace(255, 210, color_len)'];

    % Combine and normalize to [0, 1] for MATLAB colormap compatibility
    cmap_red  = [white_part_red;  red_part]  / 255;
    cmap_blue = [white_part_blue; blue_part] / 255;
end