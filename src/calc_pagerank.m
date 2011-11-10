%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% calc_pagerank
%
% This file takes an adjacency matrix representing a network and calculates
% its pagerank.
%
% The matrix's filename must be passed as a param to the function, and the file
% must be a comma-delimited matrix (so if the matrix is m x n, the file will have
% m lines, each of which has n comma-delimited values).
%
% the pagerank matrix gets printed to pagerank-{adj_matrix_filename}
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = calc_pagerank(adj_matrix_filename)

% we are doing scaled pagerank. (1 - alpha) is the percentage chance of
% a random jump:
alpha = 0.9;

A = dlmread(adj_matrix_filename);

outdegrees = sum(A')

%P is the row-stochastic matrix ultimately giving our pagerank graph:
M = diag(outdegrees) \ A;
R = ones(size(A)) / size(A,2);
P = alpha * M + (1 - alpha) * R

[W,D] = eig(P.')
W = conj(W);
v = W(:, 1);

%scale v to sum to 1
v = v / sum(v)

dlmwrite(strcat('pagerank-', adj_matrix_filename), v);

exit
