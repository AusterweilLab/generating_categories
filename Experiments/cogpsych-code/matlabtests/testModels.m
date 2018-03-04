%Load data

%Nosofsky1986
assignCat1raw = load('n86cat1.txt'); %ordered as stimuli, then conditions, then participants
assignCat2raw = load('n86cat2.txt');
task = 'assign';
%p_observed = assignCat1/(assignCat1 + assignCat2);

%pool data across participants
assignCat1pPpt = reshape(assignCat1raw,64,2);%cat 1 assignments per participant
assignCat1Pool = sum(assignCat1pPpt,2); 
assignCat1 = reshape(assignCat1Pool,16,4)'; %note the transposition

assignCat2pPpt = reshape(assignCat2raw,64,2);%cat 2 assignments per participant
assignCat2Pool = sum(assignCat2pPpt,2); 
assignCat2 = reshape(assignCat2Pool,16,4)'; %note the transposition

%Define stimulus space
nstim = 16;
nconditions = 4;
stimIdx = 1:nstim;
categoriesSet = repmat([ones(1,4),ones(1,4)*2],nconditions,1);

stimTrainIdxAll = [     
   %|-------cat 1-------|   |-------cat 2-------|
     0     3     5     6     9    10    12    15 %dimensional
     3     6     9    12     0     5    10    15 %crisscross
     5     6     9    10     2     4    11    13 %intext
     2     5     8    12     3     7    10    13] ; %diagonal
stimTrainIdxAll = stimTrainIdxAll + 1; %Adjust indexing from 1 (instead of 0)


data_k = assignCat1;
data_total = assignCat1+assignCat2;
stimCoords = ndspace(4,2);%entire stimulus space
stimTestIdx = 1:nstim; %test entire stimulus space

%Get model predictions
parmsInit = [.2,.2,.2];%[specificity,tradeoff,determinism]
stim{1} = stimTestIdx;
stim{2} = stimTrainIdxAll;
stim{3} = categoriesSet;
stim{4} = stimCoords; 
stim{5} = task;

models = {@PACKER};
nmodels = numel(models);

opt = optimset('Display','iter');
for i = 1:nmodels
    model = models{i};
    parmsFinal = fminsearch(@(x) loglike(x,model,data_k,data_total,stim),parmsInit,opt);
end



