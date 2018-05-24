%Load data
dataSet = {'nosofsky1986','NGPMG1994'};
data = 1;
[data_k,data_total,data_p,nstim_axes,stimTrainIdxAll,stimTestIdx,task,p2El] = getData(dataSet{data});

nconditions = size(stimTrainIdxAll,1);
categoriesSet = repmat([ones(1,4),ones(1,4)*2],nconditions,1);
nstim = prod(nstim_axes);
stimCoords = ndspace(nstim_axes(1),numel(nstim_axes));%entire stimulus space
% task = 'assign';
normsteep_toggle = false;

%Prepare startparms for each model    
parmsInitAll = {[2, 0.9, .5, 0],... %[specificity,tradeoff,determinism] - PACKER
                [2,     2.2, 0]}; %[specificity,determinism] - CopyTweak  
% parmsInitAll = {[rand, rand, rand, 1],... %[specificity,tradeoff,determinism] - PACKER
%                 [rand,       rand, 1]}; %[specificity,determinism] - CopyTweak
            %force CopyTweak parms to be same as PACKER
parmsInitAll{2} = [parmsInitAll{1}(1),parmsInitAll{1}(3),parmsInitAll{1}(4)];
parmRulesAll = {[1e-10, 0, 0, 0; NaN, NaN, NaN, NaN],...
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

%Pack stim-related vars
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
    datatt = [datatt, permute(reshape(data_p(j,:),nstim_axes),[2,1,3])];
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
        predsFinaltt = [predsFinaltt, permute(reshape(predsFinalt(j,:),nstim_axes),[2, 1, 3])];
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






