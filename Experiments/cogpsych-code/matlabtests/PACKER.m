function p = PACKER(parms,stimTest,stimTrain,categories,task)
% PACKER model of categorisation
% Written to see if the python version is actually making any sense.
% Parms is a vector of [specificity, tradeoff, determinism]
% Task can be 'generate' or 'assign'. 'generate' will yield predictions of
% the probability that a stimulus is generated as category 1
% given the training stim, and 'assign' will yield predictions of the 
% probability that a stimulus is assigned as category 1.
% 270218 Start

nStimTest = size(stimTest,1);
nStimTrain = size(stimTrain,1);
nDim = size(stimTrain,2);
w_k = ones(nStimTrain,nDim);
specificity = parms(1);
tradeoff = parms(2);
determinism = parms(3);

if nDim~=2
    error('Fix generation of fx vector in the code before proceeding')
else
    %This will need to be fixed if nDim>2
    fx = repmat(1-tradeoff,nStimTrain,nDim); %gammas
    for k = 1:nDim       
        fx(categories==k,k) = tradeoff;
    end
end

similarity = zeros(nStimTest,nDim);
for i = 1:nStimTest
    currStimTest = stimTest(i,:);
    distance = zeros(nStimTrain,1);
    for j = 1:nStimTrain         
        currStimTrain = stimTrain(j,:);
        diff = currStimTest-currStimTrain;
        weighted_diff = diff .* w_k(j);
        summed_diff = sum(weighted_diff,2);
        distance(j,1) = exp(-specificity*summed_diff);
    end
    for k = 1:nDim
        similarity(i,k) = sum(fx(:,k) .* distance);
    end
end
exp_sim = exp(determinism*similarity);


switch task
    case 'generate'
        sum_sim = sum(exp_sim(:,1)); %across all stim
        sum_sim = repmat(sum_sim,1,nStimTest);
        p = exp_sim ./ sum_sim;
    case 'assign'        
        sum_sim = sum(exp_sim,2); %across all dim
        sum_sim = repmat(sum_sim,1,nDim);
        p = exp_sim ./ sum_sim;
    case 'error'
                
end

p = p(:,1); %only take out category 1 (for now?) 010318





