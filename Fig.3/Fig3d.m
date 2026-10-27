%% Script 2: Visualization from CSV
clear; clc;

% ==== 1) Paths and Settings ====
outDir = 'I:\second_resource\code_submit\Fig.3';
inCsv  = fullfile(outDir, 'Fig3d.csv');

waves  = {'fast', 'slow', 'theta'};
stages = {'para_N2_', 'para_N3_'};  

% Load the data
dataTable = readtable(inCsv, 'TextType', 'string');

% ==== 2) Plotting Loop ====
for w = 1:numel(waves)
    wave = waves{w};
    
    for s = 1:numel(stages)
        stage = stages{s};
        
        % Filter data for current wave and stage
        idx = (dataTable.Wave == wave) & (dataTable.Stage == stage);
        temp_phase = dataTable.Phase(idx);
        
        if isempty(temp_phase)
            fprintf('[WARNING] No data found for %s %s. Skipping.\n', wave, stage);
            continue;
        end
        
        % 🌟 Dynamic Color Logic: N2 = Blue, N3 = Red 🌟
        if contains(stage, 'N2')
            plot_color = 'b'; % Blue for N2
            marker_fmt = 'bo';
        else
            plot_color = 'r'; % Red for N3
            marker_fmt = 'ro';
        end
        
        % Create figure (hidden during drawing to prevent screen flashing)
        fig = figure('Color', 'w', 'Visible', 'off'); 
        
        % Plot Circular Phase
        circ_plot(temp_phase, 'pretty', marker_fmt, true, 'linewidth', 2, 'color', plot_color);    
        
        % Statistical Test
        p_sp = circ_vtest(temp_phase, circ_ang2rad(0));
        mean_angle = circ_mean(temp_phase) * 180 / pi;
        
        % Add Annotation Text
        annotation_text = sprintf('Coupling count: %d, V Test (r=0) P = %.3f, Mean Angle = %.2f°', ...
            numel(temp_phase), p_sp, mean_angle);
            
        annotation('textbox', [0 0.9 1 0.1], 'String', annotation_text, ...
            'FontSize', 11, 'EdgeColor', 'none', 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
            
        % Save SVG
        outSvg = fullfile(outDir, sprintf('SO_phase_for_sp_peak_%s_%s.svg', wave, stage));
        set(fig, 'PaperPositionMode', 'auto');
        print(fig, outSvg, '-dsvg', '-r300');
        close(fig);
        
        fprintf('[OK] Saved plot: %s\n', outSvg);
    end
end