%% Fig3_wave_time_frequency_spectrograms.m
% -------------------------------------------------------------------------
% Project: Time-Frequency Spectrogram Visualization (Multiple Waves)
% Description: Loads group-averaged time-frequency data from a .mat file
%              and plots publication-ready spectrograms for N2 and N3 
%              across multiple wave types (fast, slow, theta).
%              Outputs SVG vectors directly to the target directory.
% Author: zhenglin (Optimized for GitLab Submission)
% -------------------------------------------------------------------------

clear; clc; close all;

%% 1. Configuration and Data Loading

% Define Paths
out_dir = 'Fig.3';
data_file = fullfile(out_dir, 'Fig3c.mat');

% Verify file existence before attempting to load
if ~exist(data_file, 'file')
    error('[!] Data file not found: %s. Please verify the path.', data_file);
end

fprintf('[*] Loading time-frequency data from: %s\n', data_file);
load(data_file, 'all_results');

tim_interp  = all_results.tim_interp;
freq_interp = all_results.freq_interp;
chan        = all_results.chan;
waves       = {'fast', 'slow', 'theta'};

%% 2. Generate Custom Colormaps
% Call local function to keep the main script clean
[cmap_red_N3, cmap_blue_N2] = create_custom_colormaps(256);

% Define uniform color limits for valid comparison
c_limits = [0, 0.7]; 

%% 3. Plotting Loop
fprintf('[*] Initiating plotting sequence...\n');

for w = 1:numel(waves)
    wave = waves{w};
    fprintf('    -> Processing wave: %s\n', upper(wave));
    
    % Extract current wave data for N2 and N3
    powN2 = all_results.(wave).N2;
    powN3 = all_results.(wave).N3;
    
    % Initialize figure (Side-by-Side layout)
    fig = figure('Name', sprintf('%s Wave Spectrogram', upper(wave)), ...
                 'Color', 'w', 'Position', [200, 200, 1100, 450]);
    
    % ================== N2 Spectrogram (Left Side, Blue) ==================
    ax1 = subplot(1, 2, 1);
    imagesc(tim_interp, freq_interp, powN2);
    axis xy; 
    
    colormap(ax1, cmap_blue_N2);
    caxis(ax1, c_limits);
    
    % Axes formatting
    xlim([-1.5, 1.5]);
    xlabel('Time (s)', 'FontWeight', 'bold'); 
    ylabel('Frequency (Hz)', 'FontWeight', 'bold');
    title(sprintf('%s - N2 (%s mean)', upper(wave), chan), 'FontWeight', 'normal');
    set(ax1, 'FontSize', 12, 'TickDir', 'out', 'Box', 'off', 'LineWidth', 1.2);
    
    % Add vertical reference line at Time = 0
    hold on;
    plot([0 0], [min(freq_interp), max(freq_interp)], 'k:', 'LineWidth', 1.5);
    hold off;
    
    % N2 Colorbar
    cb1 = colorbar(ax1, 'eastoutside'); 
    cb1.Label.String = 'Power (a.u.)';
    cb1.Label.FontWeight = 'bold';
    cb1.LineWidth = 1.2;
    
    % ================== N3 Spectrogram (Right Side, Red) ==================
    ax2 = subplot(1, 2, 2);
    imagesc(tim_interp, freq_interp, powN3);
    axis xy; 
    
    colormap(ax2, cmap_red_N3);
    caxis(ax2, c_limits);
    
    % Axes formatting
    xlim([-1.5, 1.5]);
    xlabel('Time (s)', 'FontWeight', 'bold'); 
    % Hide Y-label for the right subplot to reduce visual clutter
    title(sprintf('%s - N3 (%s mean)', upper(wave), chan), 'FontWeight', 'normal');
    set(ax2, 'FontSize', 12, 'TickDir', 'out', 'Box', 'off', 'LineWidth', 1.2, 'YTickLabel', []);
    
    % Add vertical reference line at Time = 0
    hold on;
    plot([0 0], [min(freq_interp), max(freq_interp)], 'k:', 'LineWidth', 1.5);
    hold off;
    
    % N3 Colorbar
    cb2 = colorbar(ax2, 'eastoutside'); 
    cb2.Label.String = 'Power (a.u.)';
    cb2.Label.FontWeight = 'bold';
    cb2.LineWidth = 1.2;
    
    % ================== Finalize & Export ==================
    sgtitle(sprintf('Group TF (%s) - %s (N2 blue / N3 red)', chan, upper(wave)), ...
            'FontWeight', 'bold', 'FontSize', 14);
    
    out_svg = fullfile(out_dir, sprintf('group_%s_TF_%s_N2blue_N3red_second.svg', chan, wave));
    set(fig, 'PaperPositionMode', 'auto');      
    print(fig, out_svg, '-dsvg', '-r300');      
    
    close(fig);
end

fprintf('[*] All spectrograms successfully exported to: %s\n', out_dir);

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