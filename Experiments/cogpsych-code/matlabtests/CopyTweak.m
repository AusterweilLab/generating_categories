function [p,distance] = CopyTweak(parms,stimTest,stimTrain,categories,task)
% CopyTweak model of categorisation - the GCM instantiation
% Written to see if the python version is actually making any sense.
% Parms is a vector of [specificity, tradeoff, determinism]
% Task can be 'generate' or 'assign'. 'generate' will yield predictions of
% the probability that a stimulus is generated as category 1
% given the training stim, and 'assign' will yield predictions of the 
% probability that a stimulus is assigned as category 1.
% 060318 Start

%Simply run PACKER with tradeoff set to 1
parms2packer = zeros(numel(parms)+1,1); %[parms(1), 1,parms(2), parms(3)];
cntA = 0;
cntB = 0;
while cntA<numel(parms2packer)
    cntA = cntA + 1;
    if cntA~=2
        cntB = cntB + 1;
        parms2packer(cntA) = parms(cntB);
    end
end
[p, distance] = PACKER(parms2packer,stimTest,stimTrain,categories,task);
