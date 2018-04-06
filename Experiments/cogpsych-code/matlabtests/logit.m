function o = logit(x,direction,steepness)
%Logit function. Direction can be either 1 or -1.
if nargin<3
    steepness = 1;
end
if nargin == 1
    direction = 1;
end

switch direction
    case 1      
        o = log(x./(1 - x));
        o = o.*steepness;
    case -1
        x = x./steepness;        
        o = 1./(1 + exp(-x));
end