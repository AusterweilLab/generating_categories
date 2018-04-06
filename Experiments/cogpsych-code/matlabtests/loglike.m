function [ll,preds] = loglike(parms,model,data_kSet, data_totalSet, stim, parmRules)
%Take in the model+parms and data generate predictions. 
%Then spit out the binomial likelihood for
%each element in prediction array. DATA_K should be a vector of the
%observed counts, and DATA_TOTAL should be a vector (of the same size)
%representing total counts
%STIM is a cell where 
% STIM{1} is an index of stimuli to test
% STIM{2} is the indices of trained stimuli arranged as an array where each row is a condition
% STIM{3} is an array indicating the categories of stimulis specified in STIM{2} 
% STIM{4} is the coordinates of all stimuli in the stimuli space
% STIM{5} is the task required (i.e., 'assign','generate', or 'error')

%Un-transform parms
if nargin==6
    parms = parmsxform(parms,parmRules(1,:),parmRules(2,:),-1);
end

%Unpack stim 
stimTestIdx = stim{1};
stimTrainIdx = stim{2};
categoriesSet = stim{3};
stimCoords = stim{4};
task = stim{5};

nStim = numel(stimTestIdx);
nConditions = size(stimTrainIdx,1);

stimTest = stimCoords(stimTestIdx,:);

preds = zeros(nConditions,nStim);
lle = zeros(nConditions,nStim);
for i = 1:nConditions
    stimTrain = stimCoords(stimTrainIdx(i,:),:);
    data_k = data_kSet(i,:);
    data_total = data_totalSet(i,:);
    categories = categoriesSet(i,:);
    preds(i,:) = model(parms,stimTest,stimTrain,categories,task)';
    %Using matlab function
    switch task
        case 'generate'
            %use mnpdf instead here
        case 'assign'
            lle(i,:) = -log(binopdf(data_k,data_total,preds(i,:)));
    end
end

ll = sum(sum(lle));




