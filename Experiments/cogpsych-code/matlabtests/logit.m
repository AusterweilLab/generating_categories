function o = logit(x,direction)
%Logit function. Direction can be either 1 or -1.
if nargin == 1
    direction = 1;
end

switch direction
    case 1
        o = log(x./(1 - x));
    case -1
        o = 1./(1 + exp(-x));
end