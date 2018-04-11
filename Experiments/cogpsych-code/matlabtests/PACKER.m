function [p,distance] = PACKER(parms,stimTest,stimTrain,categories,task)
% PACKER model of categorisation
% Written to see if the python version is actually making any sense.
% Parms is a vector of [specificity, tradeoff, determinism]
% Task can be 'generate' or 'assign'. 'generate' will yield predictions of
% the probability that a stimulus is generated as category 1
% given the training stim, and 'assign' will yield predictions of the 
% probability that a stimulus is assigned as category 1.
% Remember, when tradeoff==1, only target category is considered. When
% tradeoff==0, only contrast is considered.
% 270218 Start

nStimTest = size(stimTest,1);
nStimTrain = size(stimTrain,1);
nCat = numel(unique(categories));
nDim = size(stimTrain,2);
w_k = ones(nStimTrain,nCat)./nDim; %equally weight for now
specificity = parms(1);
tradeoff = parms(2);
determinism = parms(3);

softmax = true;
normsim = false;

if numel(parms)<4
    normsim = false;
else
    normsteep = parms(4);
end



if nCat~=2
    error('Fix generation of fx vector in the code before proceeding')
else
    %testing as of 110418
    fx = ones(nStimTrain,nCat);
    for k = 1:nCat
        fx(categories ~= k,k) = -tradeoff; %contrast category
    end
    %end test.
    
    %original code before 110418
%     %This will need to be fixed if nCat>2
%     fx = repmat(tradeoff-1,nStimTrain,nCat); %gammas
%     for k = 1:nCat       
%         fx(categories==k,k) = tradeoff; %target category
%     end
    %End original code 110418
end
if numel(categories)~=nStimTrain
    error('Size of categories vector doesn''nt match size of stimTrain.')
end

r = 1;

distance = zeros(nStimTrain,nStimTest);
similarity = zeros(nStimTrain,nStimTest);
similarity_tradeoff = zeros(nStimTest,nCat);

for i = 1:nStimTest
    currStimTest = stimTest(i,:);
    for j = 1:nStimTrain         
        currStimTrain = stimTrain(j,:);
        diff = currStimTest-currStimTrain; %x-y
        weighted_diff = diff.^r .* w_k(j); %(x-y)^r
        distance(j,i) = sum(abs(weighted_diff),2).^(1/r); %sum((x-y)^r)^1/r
        similarity(j,i) = exp(-specificity*distance(j,i));
    end
    for k = 1:nCat
        similarity_tradeoff(i,k) = sum(fx(:,k) .* similarity(:,i));
    end    
end

%normalise similarities?
if normsim
    %Try logit - hmm... seems difficult to generate probabilities close to
    %1 and 0.
%         similarity_tradeoff = logit(similarity_tradeoff,-1,normsteep);

    %Or how about simply adding a constant to prevent negatives?
        similarity_tradeoff = similarity_tradeoff+normsteep;
        %Ok but there's the problem that this prevents GCM from making any
        %good predictions, since tradeoff==1 forces ps to .5. Maybe try
        %making a lower bound on logit
    
    %How about hyperbolic tangent? One that is scaled to between 0-1?
%     similarity_tradeoff = (tanh(similarity_tradeoff)+1)/2;    
    %             maxsim = max(similarity_tradeoff,[],1);
    %             minsim = min(similarity_tradeoff,[],1);
    %             sizeadj = size(similarity_tradeoff,1);
    %             simrange = repmat(maxsim-minsim,sizeadj,1);
    %             similarity_tradeoff = (similarity_tradeoff-repmat(minsim,sizeadj,1))./simrange;
end
   

if softmax
    exp_sim = exp(determinism*similarity_tradeoff);
else %use Luce's regular rule   
    exp_sim = determinism*similarity_tradeoff; %for consistency I'm leaving the exp in, but note there's no exp actually happening
end
% similarity_tradeoff
% exp_sim
switch task
    case 'generate'
        sum_sim = sum(exp_sim,1); %across all stim
        sum_sim = repmat(sum_sim,nStimTest,1);
        p = exp_sim ./ sum_sim;
    case 'assign'
        sum_sim = sum(exp_sim,2); %across all dim
        sum_sim = repmat(sum_sim,1,nCat);
        p = exp_sim ./ sum_sim;
    case 'error'
        sum_sim = sum(exp_sim,2); %across all dim
        sum_sim = repmat(sum_sim,1,nCat);
        p = exp_sim ./ sum_sim; %error
end

% Some good variables to print when debugging
% fx
% similarity
% similarity_tradeoff
%  exp_sim
% sum_sim
% exp_sim(1)/sum_sim(1)

% sum_sim2 = sum(exp_sim,1);
% sum_sim2 = repmat(sum_sim2,nStimTest,1)
% p2 = exp_sim./sum_sim2

p = p(:,1); %only take out category 1 (for now?) 010318





