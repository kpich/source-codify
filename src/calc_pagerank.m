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
% the pagerank matrix gets printed to {adj_matrix_filename}.pagerank.txt
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = calc_pagerank(adj_matrix_filename)

% we are doing scaled pagerank. (1 - alpha) is the percentage chance of
% a random jump:
alpha = 0.9;

A = dlmread(adj_matrix_filename);
A = sparse(A);

outdegrees = sum(A');

% FixedA is A, but any rows with outdegree zero have value 1/size(A,2).
FixedA = A;
for i=1:size(A,2)
    if outdegrees(i) == 0
        FixedA(i,:) = ones(1, size(A,2)) / size(A,2);
    end
end

% if a node has no outgoing edges, set its outdegree to 1 so we don't
% divide by 0 below (this doesn't mess up the calculations):
outdegrees = max(outdegrees, 1);

% P is the row-stochastic matrix ultimately giving our pagerank graph:
M = diag(outdegrees) \ FixedA;
R = ones(size(A)) / size(A,2);
P = alpha * M + (1 - alpha) * R;

[W,D] = eig(P.');
W = conj(W);
v = W(:, 1);

%scale v to sum to 1
v = v / sum(v)

dlmwrite(strcat(adj_matrix_filename, '.pagerank.txt'), v);

exit
