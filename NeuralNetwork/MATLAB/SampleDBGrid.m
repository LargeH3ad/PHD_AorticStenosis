% 1. Create the base combinations
Inc = (0:0.25:5)';
[A, B, C] = ndgrid(Inc, Inc, Inc);
Pressures = [C(:), B(:), A(:)];

% 2. Determine the number of rows (9,261)
numRows = size(Pressures, 1);

% 3. Generate random data for columns 4, 5, and 6
% rand(numRows, 1) creates values between 0 and 1
EOA  = rand(numRows, 1); 
Vmax = rand(numRows, 1);
MPG  = rand(numRows, 1);

% 4. Append the new columns to the Pressures matrix
Database = [Pressures, EOA, Vmax, MPG];

% 5. Save the database to a CSV file
writematrix(Database, 'RandomDataBase.csv');

%%
% 1. Create the base combinations
Inc = (0:0.25:5)';
[A_mat, B_mat, C_mat] = ndgrid(Inc, Inc, Inc);

% Extract as column vectors for easy math
A = A_mat(:); 
B = B_mat(:); 
C = C_mat(:);

% 2. Define relationships (Ground Truth)
% EOA: Simple Linear Relationship
EOA = 1.5*A + 0.8*B + 2.1*C;
% Add 2% random noise to EOA
% EOA = EOA + 0.02 * randn(size(EOA));

% Vmax: Non-linear (Quadratic) Relationship
Vmax = (A.^2) + sqrt(B + 1) + log(C + 1);

% MPG: Interaction Relationship (where variables affect each other)
MPG = (A .* B) ./ (C + 1);

% 3. Combine into the final matrix
Database = [C, B, A, EOA, Vmax, MPG];

writematrix(Database, 'TrendDataBase.csv');

%%

% 1. Create the base combinations
Inc = (0:0.1:5)';
[A_mat, B_mat, C_mat] = ndgrid(Inc, Inc, Inc);

% Extract as column vectors
A = A_mat(:); 
B = B_mat(:); 
C = C_mat(:);

% 2. Define NEW relationships (Ground Truth)

% --- EOA: Nonlinear + interaction + mild saturation ---
% Combines linear, interaction, and tanh saturation
EOA = ...
    1.2*A + ...
    0.6*B - ...
    0.9*C + ...
    0.4*(A .* B) - ...
    0.3*(B .* C) + ...
    2.0*tanh(0.5*A - 0.2*C);

% Optional noise (small, controlled)
% EOA = EOA + 0.01 * randn(size(EOA));

% --- Vmax: Smooth nonlinear + exponential decay ---
% Tests NN ability to learn curvature and decay
Vmax = ...
    3.0*(1 - exp(-0.4*A)) + ...
    0.8*sqrt(B + 1) + ...
    log(C + 1) - ...
    0.2*A.*C;

% --- MPG: Strong interaction + periodic component ---
% Harder: requires learning multiplicative + sinusoidal structure
MPG = ...
    (A .* B) ./ (C + 1) + ...
    0.5*sin(0.8*A) - ...
    0.3*cos(0.6*B) + ...
    0.1*C.^2;

% 3. Combine into the final matrix
Database = [C, B, A, EOA, Vmax, MPG];

writematrix(Database, 'TrendDataBaseV2.csv');


%% Dataset with minor noise

% 0. Reproducibility
rng(42);   % Fixed seed so results are repeatable

% 1. Create the base combinations
Inc = (0:0.1:5)';
[A_mat, B_mat, C_mat] = ndgrid(Inc, Inc, Inc);

% Extract as column vectors
A = A_mat(:); 
B = B_mat(:); 
C = C_mat(:);

% 2. Define ground-truth relationships (noise-free)

EOA_clean = ...
    1.2*A + ...
    0.6*B - ...
    0.9*C + ...
    0.4*(A .* B) - ...
    0.3*(B .* C) + ...
    2.0*tanh(0.5*A - 0.2*C);

Vmax_clean = ...
    3.0*(1 - exp(-0.4*A)) + ...
    0.8*sqrt(B + 1) + ...
    log(C + 1) - ...
    0.2*A.*C;

MPG_clean = ...
    (A .* B) ./ (C + 1) + ...
    0.5*sin(0.8*A) - ...
    0.3*cos(0.6*B) + ...
    0.1*C.^2;

% 3. Add small noise (≈1% of each signal)

noise_level = 0.01;   % 1%

A = A + noise_level * std(A)   * randn(size(A));
B = B + noise_level * std(B)   * randn(size(B));
C = C + noise_level * std(C)   * randn(size(C));

EOA  = EOA_clean  + noise_level * std(EOA_clean)  * randn(size(EOA_clean));
Vmax = Vmax_clean + noise_level * std(Vmax_clean) * randn(size(Vmax_clean));
MPG  = MPG_clean  + noise_level * std(MPG_clean)  * randn(size(MPG_clean));

% 4. Combine into final matrix
Database = [C, B, A, EOA, Vmax, MPG];

writematrix(Database, 'TrendDataBaseNoise.csv');

