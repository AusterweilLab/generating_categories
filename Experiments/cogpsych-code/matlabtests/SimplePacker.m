%Testing simple run of PACKER

specificity = 1;
determinism = 1;
tradeoff = .887;
tradeoff2 = .2;

task = 'generate';
% stimTest = [0,1;1,0;0,0;1,1];
% stimTrain = [0,1;1,0;];

%This gives same p for generate
% stimTest = [0,1;1,0;0,0;1,1];
% stimTrain = [0,1;1,0;0,0;1,1];

%So does this. So it looks like the scale and position of stim don't matter
%as long as it is square? No, see further below for larger squares that don't produce
%invariance
% stimTest = [1,2;2,1;1,1;2,2];
% stimTrain = [1,2;2,1;1,1;2,2];

%a 3X3 square doesn't seem to produce invariance
stimTest = cartesian([1:3],2);%[1,2;2,1;1,1;2,2;1,3;3,1;3,2;3,3;2,3;];
stimTrain = cartesian([1:3],2);

%a 4X4 square doesn't seem to produce invariance
stimTest = cartesian([1:4],2);%[1,2;2,1;1,1;2,2;1,3;3,1;3,2;3,3;2,3;];
stimTrain = cartesian([1:4],2);

%What about a 2X2X2 cube? Ah! Invariance!
stimTest = cartesian([1:2],3);%[1,2;2,1;1,1;2,2;1,3;3,1;3,2;3,3;2,3;];
stimTrain = cartesian([1:2],3);

%2^4 hypercube? Also invariant!
stimTest = cartesian([1:2],4);%
stimTrain = cartesian([1:2],4);
% stimTest = [1,2;2,1;1,1;2,2;1,3;3,1;3,2;3,3;];
% stimTrain = [1,2;2,1;1,1;2,2;1,3;3,1;3,2;3,3;];

% stimTest = [0,1;1,0;0,0;1,1];
% stimTrain = [0,1;1,0;0,0;1,1];

stimTest = [.5,1;2,0;];
stimTrain = [0,1;1,0];

nStimTrain = size(stimTrain,1);

%Generate category indices that equally split the stim, if it can
categories = repmat(1:2,floor(nStimTrain/2),1);%[1,1,1,1,2,2,2,2,2];
if mod(nStimTrain,2)==0
    categories = reshape(categories,nStimTrain,1);
else
    categories = [reshape(categories,nStimTrain-1,1);1];
end

categories

parms = [specificity,tradeoff,determinism];
parms2 = parms;
parms2(2) = tradeoff2;
[p,distance] = PACKER(parms,stimTest,stimTrain,categories,task);
[p2,distance2] = PACKER(parms2,stimTest,stimTrain,categories,task);

[p,p2]