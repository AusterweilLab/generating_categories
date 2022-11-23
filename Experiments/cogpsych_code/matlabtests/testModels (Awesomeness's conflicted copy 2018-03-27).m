%Load data
dataSet = {'nosofsky1986','NGPMG1994'};
data = 1;
[data_k,data_total,data_p,nstim_axes] = getData(dataSet{data});
%Nosofsky1986
% assignCat1raw = load('n86cat1.txt'); %ordered as stimuli, then conditions, then participants
% assignCat2raw = load('n86cat2.txt');
% task = 'assign';
% %p_observed = assignCat1/(assignCat1 + assignCat2);
% 
% %pool data across participants
% assignCat1pPpt = reshape(assignCat1raw,64,2);%cat 1 assignments per participant
% assignCat1Pool = sum(assignCat1pPpt,2); 
% assignCat1 = reshape(assignCat1Pool,16,4)'; %note the transposition
% 
% assignCat2pPpt = reshape(assignCat2raw,64,2);%cat 2 assignments per participant
% assignCat2Pool = sum(assignCat2pPpt,2); 
% assignCat2 = reshape(assignCat2Pool,16,4)'; %note the transposition
% 
% %Define stimulus space
% nstim_axes = [4,4]; %This tells us that the stimulis are organised as a 4 by 4 array
% nstim = prod(nstim_axes);
% 
% 
% nconditions = 4;
% stimIdx = 1:nstim;
% categoriesSet = repmat([ones(1,4),ones(1,4)*2],nconditions,1);
% 
% stimTrainIdxAll = [     
%    %|-------cat 1-------|   |-------cat 2-------|
%      0     3     5     6     9    10    12    15 %dimensional
%      3     6     9    12     0     5    10    15 %crisscross
%      5     6     9    10     2     4    11    13 %intext
%      2     5     8    12     3     7    10    13] ; %diagonal
% stimTrainIdxAll = stimTrainIdxAll + 1; %Adjust indexing from 1 (instead of 0)
% 
% 
% data_k = assignCat1;
% data_total = assignCat1+assignCat2;
% data_p = data_k./data_total;
nstim = prod(nstim_axes);
stimCoords = ndspace(nstim_axes(1),numel(nstim_axes));%entire stimulus space
stimTestIdx = 1:nstim; %test entire stimulus space
normsteep_toggle = true;

%Prepare startparms for each model    
parmsInitAll = {[4.3, .8, .5, 1e-100],... %[specificity,tradeoff,determinism] - PACKER
                [4.3,       .5, 1e-100]}; %[specificity,determinism] - CopyTweak  
% parmsInitAll = {[rand, rand, rand, 1e-100],... %[specificity,tradeoff,determinism] - PACKER
%                 [rand,       rand, 1e-100]}; %[specificity,determinism] - CopyTweak
            %force CopyTweak parms to be same as PACKER
            parmsInitAll{2} = [parmsInitAll{1}(1),parmsInitAll{1}(3),parmsInitAll{1}(4)];
parmRulesAll = {[1e-10, 0, 0, 0; NaN, 1, NaN, NaN],...
                [1e-10,    0, 0; NaN,    NaN, NaN]};
parmNamesAll = {{'Specifty', 'Tradeoff', 'Detrmnsm','NrmSteep'};
                {'Specifty', 'Detrmnsm', 'NrmSteep'}};
             
if ~normsteep_toggle
    for i = 1:numel(parmsInitAll)
        parmsInitAll{i}(:,end) = [];
        parmRulesAll{i}(:,end) = [];
%         parmNamesAll{i}{:,end} = [];
    end
end
    
%Transform parms according to rules
stim{1} = stimTestIdx;
stim{2} = stimTrainIdxAll;
stim{3} = categoriesSet;
stim{4} = stimCoords; 
stim{5} = task;

ndata = numel(data_k);
nConditions = size(data_k,1);

models = {@PACKER,@CopyTweak};
nmodels = numel(models);
parmsFinal = cell(nmodels,1);
llFinal = zeros(nmodels,1);
predsFinal = zeros(nmodels,ndata);
SSE = zeros(nmodels,1);
opt = optimset('Display','none');

%Print data
datatt = [];
for j = 1:nConditions
    datatt = [datatt, reshape(data_p(j,:),nstim_axes)'];
end
dataf = flipud(datatt); % only take first layer of stim
fprintf('\tObserved Data : \n')
dataStr = repmat([repmat('%5.2f ',1, nstim_axes(1)), '|'],1,nConditions);
for j = 1:nstim_axes(1)
    fprintf(['\t    ',dataStr,'\n'],dataf(j,:));
end
if numel(nstim_axes)>2
    fprintf('\t           Note: only first layer of data printed.\n')
end
fprintf('\n')

for i = 1:nmodels
    model = models{i};
    parmsMin = parmRulesAll{i}(1,:);
    parmsMax = parmRulesAll{i}(2,:);    
    parmsInit = parmsxform(parmsInitAll{i},parmsMin,parmsMax,1);
    parmsFinalt = fminsearch(@(x) loglike(x,model,data_k,data_total,stim,parmRulesAll{i}),parmsInit,opt);
    %Get final predictions
    [llFinal(i),predsFinalt] = loglike(parmsFinalt,model,data_k,data_total,stim,parmRulesAll{i});
    predsFinal(i,:) = predsFinalt(:)';%reshape(predsFinalt',ndata,1)';
    %Transform final parms
    parmsFinal{i} = parmsxform(parmsFinalt,parmsMin,parmsMax,-1);
    SSE(i) = sum((predsFinal(i,:) - data_p(:)').^2);
    
    %Print them out nicely    
    nparms = numel(parmsInitAll{i});    
    fprintf('%s:\n',func2str(model)) %Model name
    
    fprintf('\tParm names:  [');
    for j = 1:nparms
        fprintf('%s, ',parmNamesAll{i}{j})
    end
    fprintf(']\n') 
    fprintf('\tStart parms: [');
    for j = 1:nparms
        fprintf('%8.4f, ',parmsInitAll{i}(j))
    end
    fprintf(']\n') 
    
    fprintf('\tnLL = %8.4f\n',llFinal(i))
    fprintf('\tSSE = %8.4f\n',SSE(i))
    
    fprintf('\tFinal parms: [')
    for j = 1:nparms
        fprintf('%8.4f, ',parmsFinal{i}(j))
    end
    fprintf(']\n')    
    
    %Format preds
    predsFinaltt = [];
    for j = 1:nConditions
        predsFinaltt = [predsFinaltt, reshape(predsFinalt(j,:),nstim_axes)'];
    end
    predsFinalf = flipud(predsFinaltt); % only take first layer of stim
    fprintf('\tPreds : \n')    
    predsStr = repmat([repmat('%5.2f ',1, nstim_axes(1)), '|'],1,nConditions);
    for j = 1:nstim_axes(1)
        fprintf(['\t    ',predsStr,'\n'],predsFinalf(j,:));
    end    
    if numel(nstim_axes)>2
        fprintf('\t           Note: only first layer of predictions printed.\n')
    end
    fprintf('\n')
end

%Present plots






