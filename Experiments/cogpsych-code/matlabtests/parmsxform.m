function parmsx = parmsxform(parms,min,max,direction)
% Scales parameter values within a logit (if min and max is defined) or logistic space
% (if only min is defined). Useful to restrict values when fitting.
% MIN and MAX must be a vector of the same size as PARMS
% DIRECTION can be either 1 or -1.

if nargin<4
    direction = 1;
end
if nargin<3
    max = NaN;
end

nparms = numel(parms);
nmin = numel(min);
nmax = numel(max);
parmsx = nan(size(parms));
if nmin~=nparms || nmax ~= nparms
    %Expand min and max to parm-sized vector if just one element
    if nmin==1
        min = ones(size(nparms));
    else
       error('Number of min values not equal to number of parms.');       
    end
    if nmax==1
        max = ones(size(nparms));
    else
       error('Number of max values not equal to number of parms.');        
    end
end

for i = 1:nparms
    currparm = parms(i);
    currmin = min(i);
    currmax = max(i);
    if isnan(currmax)
        type = 'log';
    else
        type = 'logit';
    end
    
    switch type
        case 'log'
            if direction==1
                parmsx(i) = log(currparm - currmin);
            elseif direction==-1
                parmsx(i) = exp(currparm) + currmin;
            end
        case 'logit'
            range = currmax-currmin;
            if direction==1
                parmsadj = (currparm-currmin)./range;
                parmsx(i) = log(parmsadj./(1 - parmsadj));
            elseif direction==-1
                parmsadj = 1./(1 + exp(-currparm));
                parmsx(i) = parmsadj.*range + currmin;
            end
    end
    
end