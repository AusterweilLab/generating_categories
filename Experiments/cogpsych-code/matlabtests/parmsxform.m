function parmsx = parmsxform(parms,min,max,direction)
% Scales parameter values within a logit (if min and max is defined) or logistic space
% (if only min is defined). Useful to restrict values when fitting.
% MIN and MAX must be a vector of the same size as PARMS
% DIRECTION can be either 1 or -1.

if isnan(max)
    type = 'log';
else
    type = 'logit';
end

switch type
    case 'log'       
        if direction==1
            parmsx = log(parms - min);
        elseif direction==-1
            parmsx = exp(parms) + min;
        end
    case 'logit'
        range = max-min;
        if direction==1            
            parmsadj = (parms-min)./range;
            parmsx = log(parmsadj./(1 - parmsadj));
        elseif direction==-1
            parmsadj = 1./(1 + exp(-parms));
            parmsx = parmsadj.*range + min;
        end        
end

