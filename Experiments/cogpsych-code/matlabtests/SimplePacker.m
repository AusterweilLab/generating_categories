%Testing simple run of PACKER

specificity = 1;
determinism = 1;
tradeoff = [.887,.5,.4,.1];
% tradeoff2 = .1;

task = 'assign';
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

stimTest = [1,0;0,1];
stimTrain = [0,1;1,0];

nStimTrain = size(stimTrain,1);
nStimTest = size(stimTest,1);
%Generate category indices that equally split the stim, if it can
categories = repmat(1:2,floor(nStimTrain/2),1);%[1,1,1,1,2,2,2,2,2];
if mod(nStimTrain,2)==0
    categories = reshape(categories,nStimTrain,1);
else
    categories = [reshape(categories,nStimTrain-1,1);1];
end



pset = nan(nStimTest,numel(tradeoff));
distanceset = cell(1,numel(tradeoff));
for i = 1:numel(tradeoff)
    parms = [specificity,tradeoff(i),determinism];
    [pset(:,i),distanceset{i}] = PACKER(parms,stimTest,stimTrain,categories,task);
end
pset