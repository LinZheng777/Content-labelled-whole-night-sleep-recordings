%% Script 2: Visualization of Group History Curve
clc, clear

%% ================== 1) Load Pre-calculated Data ==================
% Update this path if you move the .mat file
data_path = 'Fig.4\Fig4a_long.mat'; % revise your file path
load(data_path, 'common_xlag', 'm', 'lo', 'hi');

%% ================== 2) Plot Settings & Canvas Initialization ==================
fig = figure('Color','w', 'Position', [200 200 600 450]); 
hold on;

% Define colors
shade_color = [0.7 0.7 0.7];
line_color  = 'k';

%% ================== 3) Plotting ==================
x = common_xlag;

% 1. Plot 95% Confidence Interval (Shading)
% Remove NaNs just in case to prevent filling errors at the edges
valid_idx = ~isnan(m) & ~isnan(lo) & ~isnan(hi);
x_valid = x(valid_idx);
lo_valid = lo(valid_idx);
hi_valid = hi(valid_idx);

fill([x_valid, fliplr(x_valid)], [hi_valid, fliplr(lo_valid)], shade_color, ...
    'FaceAlpha', 0.35, 'EdgeColor', 'none');

% 2. Plot Group Mean Line
plot(x_valid, m(valid_idx), '-', 'Color', line_color, 'LineWidth', 2);

% 3. Plot Baseline (y = 1)
yline(1, '--', 'Color', line_color, 'LineWidth', 1.2);

%% ================== 4) Formatting & Beautification ==================
xlim([0 90]);
% Adjust ylim dynamically based on data, keeping 1.0 visible
y_min = min(lo_valid) * 0.95; 
y_max = max(hi_valid) * 1.05;
ylim([min(y_min, 0.95), max(y_max, 1.05)]);

xlabel('Time Lag (sec)', 'FontWeight', 'bold');
ylabel('Rate Multiplier', 'FontWeight', 'bold');
title('History Modulation with 95%% CI', 'FontWeight', 'normal');

% Apply academic styling
set(gca, 'Box','off', 'TickDir', 'in', 'LineWidth', 1.2, 'FontSize', 12);

%% ================== 5) Export SVG ==================
out_dir = 'I:\second_resource\code_submit\Fig.4';
out_svg = fullfile(out_dir, 'GroupHistory_night_CI.svg');

% Save SVG while keeping text editable
set(fig, 'PaperPositionMode', 'auto');
print(fig, out_svg, '-dsvg', '-r300');

fprintf('🎉 Plot successfully generated and saved to: %s\n', out_svg);