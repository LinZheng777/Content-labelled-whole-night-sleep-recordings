%% Script 2: Visualize Group Phase Circular Plots and Heatmap
clc; clear;

%% ================== 1) LOAD DATA ==================
% Update this path if necessary
data_path = 'Fig.4\Fig4_phase_first.mat'; % revise your file path
load(data_path, 'PP', 'Z_mean', 'phi_grid', 'stages', 'nSub');

out_dir = 'I:\second_resource\code_submit\Fig.4';

% Define stage colors (N1=Green, N2=Blue, N3=Red)
stage_colors = {'g', 'b', 'r'}; 
stage_col_rgb = [0 0.5 0; 0 0.4470 0.7410; 0.8500 0.3250 0.0980]; 

%% ================== 2) HELPER: CIRCULAR STATS ==================
circ_mean = @(ang) angle(mean(exp(1i*ang), 'omitnan'));

% Calculate Bootstrap 95% CI for preferred phase across stages
B = 1000;
pp_mean = nan(3, 1);
pp_ci   = nan(3, 2);

for k = 1:3
    a = PP(:, k);
    a = a(isfinite(a));
    pp_mean(k) = circ_mean(a);
    
    if numel(a) >= 5
        boot = nan(B, 1);
        for b = 1:B
            idx = randi(numel(a), [numel(a), 1]);
            boot(b) = circ_mean(a(idx));
            boot(b) = pp_mean(k) + wrapToPi(boot(b) - pp_mean(k));
        end
        pp_ci(k, :) = prctile(boot, [2.5 97.5]);
    end
end

%% ================== 3) PLOTTING ==================
fig = figure('Color', 'w', 'Position', [100, 100, 1000, 600]);
tiledlayout(3, 3, 'Padding', 'compact', 'TileSpacing', 'compact');

% --- A) Left Column: 3 Circular Phase Plots ---
for k = 1:3
    temp_SIp = PP(:, k);
    temp_SIp = temp_SIp(isfinite(temp_SIp));
    
    nexttile((3-k)*3 + 1); % Position: Bottom to Top (N1, N2, N3) to align with heatmap
    
    % Draw circular plot with individual dots
    circ_plot(temp_SIp, 'pretty', 'ro', true, 'linewidth', 2, 'color', stage_colors{k});
    
    % Calculate V-test against 0 radians (Peak of SO)
    p_sp = circ_vtest(temp_SIp, 0);
    mean_angle_deg = circ_mean(temp_SIp) * 180 / pi;
    
    % Annotation Title
    title(sprintf('%s (n=%d)\nMean: %.1f\\circ, P_{vtest}=%.3f', ...
        stages{k}, numel(temp_SIp), mean_angle_deg, p_sp), 'FontSize', 10);
end

% --- B) Right Columns: Combined Stage Heatmap ---
axh = nexttile(2, [3, 2]); % Occupy remaining 2 columns across 3 rows
imagesc(phi_grid, 1:3, Z_mean);
axis xy;

% Configure Heatmap Axes
yticks(1:3); 
yticklabels(stages);
xlabel('SO Phase (rad)', 'FontWeight', 'bold');
title(sprintf('Model With Stage (Group mean, n=%d)', nSub), 'FontWeight', 'bold');

% Color mapping
colormap(axh, parula);
cb = colorbar;
ylabel(cb, 'Rate (events/min)', 'FontWeight', 'bold');

hold on;

% Overlay preferred phase mean and CI as vertical markers on the heatmap
for k = 1:3
    y0 = k;
    % Draw Mean Line
    plot([pp_mean(k), pp_mean(k)], [y0-0.45, y0+0.45], 'LineStyle', '-', ...
        'Color', stage_col_rgb(k,:), 'LineWidth', 2.5);
    
    % Draw CI dashed lines
    if all(isfinite(pp_ci(k, :)))
        plot([pp_ci(k,1), pp_ci(k,1)], [y0-0.45, y0+0.45], 'LineStyle', '--', ...
            'Color', stage_col_rgb(k,:), 'LineWidth', 1.5);
        plot([pp_ci(k,2), pp_ci(k,2)], [y0-0.45, y0+0.45], 'LineStyle', '--', ...
            'Color', stage_col_rgb(k,:), 'LineWidth', 1.5);
    end
end
xlim([-pi, pi]);
xticks([-pi, -pi/2, 0, pi/2, pi]);
xticklabels({'-\pi', '-\pi/2', '0', '\pi/2', '\pi'});

%% ================== 4) EXPORT ==================
out_svg = fullfile(out_dir, 'Phase_event_heatmap_combined.svg');
set(fig, 'PaperPositionMode', 'auto');
print(fig, out_svg, '-dsvg', '-r300');
fprintf('\n🎉 Figure successfully saved to: %s\n', out_svg);