%% Fig2e_spearman_fdr_heatmap.m
% -------------------------------------------------------------------------
% Purpose:
%   Compute Spearman correlations between subjective sleep reports and
%   objective sleep measures, apply Benjamini-Hochberg FDR correction,
%   and optionally plot a significance heatmap.
%
% Input files:
%   Fig2e_obj.csv
%       Objective sleep measures. Must include a column named "subjects".
%
%   Fig2e_suj.csv
%       Subjective sleep reports. Must include a column named "subjects".
%
% Output files:
%   Fig2e_spearman_r.csv
%   Fig2e_spearman_p_uncorrected.csv
%   Fig2e_spearman_p_fdr.csv
%
% Notes:
%   Put this script, Fig2e_obj.csv and Fig2e_suj.csv in the same folder.
%   If SHeatmap11.m is available on the MATLAB path, the heatmap will be
%   plotted using FDR-corrected p values.
% -------------------------------------------------------------------------

clear; clc;

%% 1. Define paths

script_path = mfilename('fullpath');
script_dir = fileparts(script_path);

obj_file = fullfile(script_dir, 'Fig2e_obj.csv');
suj_file = fullfile(script_dir, 'Fig2e_suj.csv');

output_dir = script_dir;

fprintf('Objective data file: %s\n', obj_file);
fprintf('Subjective data file: %s\n', suj_file);
fprintf('Output directory: %s\n', output_dir);

%% 2. Load data

data_obj = readtable(obj_file);
data_suj = readtable(suj_file);

if ~ismember('subjects', data_obj.Properties.VariableNames)
    error('Fig2e_obj.csv must contain a column named "subjects".');
end

if ~ismember('subjects', data_suj.Properties.VariableNames)
    error('Fig2e_suj.csv must contain a column named "subjects".');
end

%% 3. Match subjects and keep the same order

common_subjects = intersect(data_obj.subjects, data_suj.subjects, 'stable');

[~, idx_obj] = ismember(common_subjects, data_obj.subjects);
[~, idx_suj] = ismember(common_subjects, data_suj.subjects);

data_obj_matched = data_obj(idx_obj, :);
data_suj_matched = data_suj(idx_suj, :);

fprintf('Matched participants: %d\n', numel(common_subjects));

%% 4. Remove subject column and convert to matrices

data_obj_values = removevars(data_obj_matched, 'subjects');
data_suj_values = removevars(data_suj_matched, 'subjects');

labels_x = data_obj_values.Properties.VariableNames;  % objective variables
labels_y = data_suj_values.Properties.VariableNames;  % subjective variables

matrix_obj = table2array(data_obj_values);
matrix_suj = table2array(data_suj_values);

if ~isnumeric(matrix_obj) || ~isnumeric(matrix_suj)
    error('All columns except "subjects" must be numeric.');
end

%% 5. Compute Spearman correlations

n_suj = size(matrix_suj, 2);
n_obj = size(matrix_obj, 2);

result_r = nan(n_suj, n_obj);
result_p = nan(n_suj, n_obj);

for i = 1:n_suj
    for j = 1:n_obj
        [r, p] = corr( ...
            matrix_suj(:, i), ...
            matrix_obj(:, j), ...
            'Type', 'Spearman', ...
            'Rows', 'complete' ...
        );

        result_r(i, j) = r;
        result_p(i, j) = p;
    end
end

fprintf('Spearman correlations completed.\n');

%% 6. Apply Benjamini-Hochberg FDR correction

result_p_fdr = benjamini_hochberg_fdr(result_p);

fprintf('FDR correction completed.\n');

%% 7. Save result matrices

r_table = array2table(result_r, ...
    'VariableNames', labels_x, ...
    'RowNames', labels_y);

p_table = array2table(result_p, ...
    'VariableNames', labels_x, ...
    'RowNames', labels_y);

p_fdr_table = array2table(result_p_fdr, ...
    'VariableNames', labels_x, ...
    'RowNames', labels_y);

writetable(r_table, fullfile(output_dir, 'Fig2e_spearman_r.csv'), ...
    'WriteRowNames', true);

writetable(p_table, fullfile(output_dir, 'Fig2e_spearman_p_uncorrected.csv'), ...
    'WriteRowNames', true);

writetable(p_fdr_table, fullfile(output_dir, 'Fig2e_spearman_p_fdr.csv'), ...
    'WriteRowNames', true);

fprintf('Saved correlation matrices:\n');
fprintf('  Fig2e_spearman_r.csv\n');
fprintf('  Fig2e_spearman_p_uncorrected.csv\n');
fprintf('  Fig2e_spearman_p_fdr.csv\n');

%% 8. Plot heatmap if SHeatmap11 is available

if exist('SHeatmap11', 'file') == 2
    SHM = SHeatmap11(result_r, result_p_fdr, 'Format', 'acirc');
    SHM = SHM.draw();

    SHM.ax.XTickLabel = labels_x;
    SHM.ax.YTickLabel = labels_y;

    SHM.setText();
    SHM.setp();

    title(SHM.ax, 'Spearman correlation, FDR-corrected');

    fprintf('Heatmap plotted using FDR-corrected p values.\n');
else
    warning(['SHeatmap11.m was not found on the MATLAB path. ', ...
             'The CSV result matrices were saved, but the heatmap was not plotted.']);
end

%% ------------------------------------------------------------------------
% Local function: Benjamini-Hochberg FDR correction
% ------------------------------------------------------------------------

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
