function out = cartesian(varargin)
% Generates the cartesian product of the input vectors
vArg = varargin;
nVec = numel(vArg);

%If only two arguments and second one is a scalar, then repmat the first
%vector as many times as specified in second arg.
monoArgIn = false;
if nVec==2
    if isscalar(vArg{2})
        monoArgIn = true;
    end
elseif nVec==1
    error('Second argument needs to be supplied either as a scalar or vector');
end

if monoArgIn
    ndim = vArg{2};
    inStr = 'vArg{1},'; %trailing comma is left in there on purpose
else
    ndim = nVec;
    inStr = sprintf('vArg{%d},',1:ndim);
end

%Prepare output variables
outStr = sprintf('x%d,',1:ndim);
concatStr = sprintf('x%d(:),',ndim:-1:1);
evalStr = sprintf('[%s] = ndgrid(%s); out = [%s];',outStr(1:end-1),inStr(1:end-1),concatStr(1:end-1)); %the (1:end-1) is to remove the trailing comma
eval(evalStr);

end