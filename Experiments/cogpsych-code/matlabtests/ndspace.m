function out = ndspace(n,d,low,high)
% Generate coordinates of points based on an evenly distributed d-dimensional
% grid, sampled at n points along each dimension. User may specify low and high
% points of grid. Defaults: low = -1, high = +1
% 
% Example: Making a 3-dimensional binary space
% >> ndspace(2, 3, 0)
%    [[ 0.  0.  0.]
%     [ 0.  0.  1.]
%     [ 0.  1.  0.]
%     [ 0.  1.  1.]
%     [ 1.  0.  0.]
%     [ 1.  0.  1.]
%     [ 1.  1.  0.]
%     [ 1.  1.  1.]]

if nargin<4
    high = 1;
end

if nargin<3
    low = -1;
end

baseVector = linspace(low,high,n);
%Prepare output variables
outStr = sprintf('x%d,',1:d);
concatStr = sprintf('x%d(:),',d:-1:1);
evalStr = sprintf('[%s] = ndgrid(baseVector); out = [%s];',outStr,concatStr);
eval(evalStr)
