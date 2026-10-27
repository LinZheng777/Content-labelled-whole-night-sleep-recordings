%% Fig5a.m
% -------------------------------------------------------------------------
% Project: PCA-CCA Pipeline for Sleep Objective Metrics & Subjective
% Reports during first night
% Purpose:
%   Compute Spearman correlations between subjective sleep reports and 
%   two sets of objective sleep measures (N2 and N3).
%   Applies Benjamini-Hochberg FDR correction and plots the resulting 
%   significance heatmaps using SHeatmap11.
%
% Author: zhenglin (Optimized for GitLab Submission)
% -------------------------------------------------------------------------

clear; clc; close all;

%% 1. Define Paths and Load Data
base_dir = 'I:\second_resource\code_submit\Fig.5';

file_sub = fullfile(base_dir, 'Fig5a_subjective.csv');
file_n2  = fullfile(base_dir, 'Fig5a_N2_objective.csv');
file_n3  = fullfile(base_dir, 'Fig5a_N3_objective.csv'); % Assuming this naming convention

fprintf('Loading datasets...\n');
data_sub = readtable(file_sub);
data_n2  = readtable(file_n2);
data_n3  = readtable(file_n3);

%% 2. Data Preprocessing
% Remove non-variable columns based on user specifications
data_sub(:, 1:3) = []; 
data_n2(:, 1)    = []; 
data_n3(:, 1)    = [];

% Retain only the first 10 items for subjective reports
if size(data_sub, 2) >= 10
    data_sub = data_sub(:, 1:10); 
end

% Extract labels
labels_y = data_sub.Properties.VariableNames; % Y-axis: Subjective
labels_x_n2 = data_n2.Properties.VariableNames; % X-axis: N2 Objective
labels_x_n3 = data_n3.Properties.VariableNames; % X-axis: N3 Objective

% Convert to numeric arrays
matrix_sub = table2array(data_sub);
matrix_n2  = table2array(data_n2);
matrix_n3  = table2array(data_n3);

fprintf('Preprocessing complete. Generating Heatmaps...\n\n');

%% 3. Compute and Plot for N2
fprintf('--- Processing N2 Data ---\n');
[r_n2, p_fdr_n2] = compute_correlations(matrix_sub, matrix_n2);

if exist('SHeatmap11', 'file') == 2
    figure('Name', 'N2 Correlation Heatmap', 'Color', 'w');
    SHM_N2 = SHeatmap11(r_n2, p_fdr_n2, 'Format', 'sq');
    SHM_N2 = SHM_N2.draw();
    SHM_N2.ax.XTickLabel = labels_x_n2;
    SHM_N2.ax.YTickLabel = labels_y;
    title(SHM_N2.ax, 'N2 Objective vs Subjective (FDR-corrected)');
    fprintf('N2 Heatmap successfully generated.\n\n');
else
    warning('SHeatmap11.m not found on path. Skipping N2 plot.');
end

%% 4. Compute and Plot for N3
fprintf('--- Processing N3 Data ---\n');
[r_n3, p_fdr_n3] = compute_correlations(matrix_sub, matrix_n3);

if exist('SHeatmap11', 'file') == 2
    figure('Name', 'N3 Correlation Heatmap', 'Color', 'w');
    SHM_N3 = SHeatmap11(r_n3, p_fdr_n3, 'Format', 'sq');
    SHM_N3 = SHM_N3.draw();
    SHM_N3.ax.XTickLabel = labels_x_n3;
    SHM_N3.ax.YTickLabel = labels_y;
    title(SHM_N3.ax, 'N3 Objective vs Subjective (FDR-corrected)');
    fprintf('N3 Heatmap successfully generated.\n');
else
    warning('SHeatmap11.m not found on path. Skipping N3 plot.');
end

fprintf('\n[*] All processes complete.\n');

%% ========================================================================
% Local Functions
% ========================================================================

function [result_r, result_p_fdr] = compute_correlations(mat_sub, mat_obj)
    % Compute Spearman correlations and apply FDR correction
    n_sub = size(mat_sub, 2);
    n_obj = size(mat_obj, 2);
    
    result_r = zeros(n_sub, n_obj); 
    result_p = zeros(n_sub, n_obj);
    
    for i = 1:n_sub
        for j = 1:n_obj
            [r, p] = corr(mat_sub(:, i), mat_obj(:, j), ...
                'Type', 'Spearman', 'Rows', 'complete');
            result_r(i, j) = r;
            result_p(i, j) = p;
        end
    end
    
    % Apply FDR correction
    result_p_fdr = benjamini_hochberg_fdr(result_p);
end

function p_fdr = benjamini_hochberg_fdr(p_matrix)
    % Apply Benjamini-Hochberg FDR correction to all non-NaN p values.
    p_vec = p_matrix(:);
    valid_idx = ~isnan(p_vec);

    p_fdr_vec = nan(size(p_vec));
    p_valid = p_vec(valid_idx);
    
    [p_sorted, sort_idx] = sort(p_valid);
    m = numel(p_sorted);
    q_sorted = p_sorted .* m ./ (1:m)';

    % Enforce monotonicity
    q_sorted = flipud(cummin(flipud(q_sorted)));

    % p values cannot exceed 1
    q_sorted(q_sorted > 1) = 1;

    % Restore original order
    q_valid = nan(size(p_valid));
    q_valid(sort_idx) = q_sorted;

    p_fdr_vec(valid_idx) = q_valid;
    p_fdr = reshape(p_fdr_vec, size(p_matrix));
end