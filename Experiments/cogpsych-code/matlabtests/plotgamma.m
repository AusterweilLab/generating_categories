%Plot a figure showing how changing gamma (tradeoff) affects the order of SHJ types

%These are the best spec and determinism fits to NGPMG1994
specificity = 1.99;%56.68699728478552;
tradeoff_list = 0:.01:1; %0.25750159353896424
determinism = 2.25 ;%2.751535314273929;
baselinesim = 1;
dataSet = {'nosofsky1986','NGPMG1994'};
data = 1;
plot2 = false; 

[data_k,data_total,data_p,nstim_axes,stimTrainIdxAll,stimTestIdx,task,p2El] = getData(dataSet{data});
nstim = prod(nstim_axes);

models = {@PACKER,@CopyTweak};
% parmsInitAll = {[specificity, NaN, determinism, baselinesim]}; %[specificity,tradeoff,determinism] - PACKER
% parmsInitAll{2} = [parmsInitAll{1}(1),parmsInitAll{1}(3),parmsInitAll{1}(4)];
parmRulesAll = {[1e-10, 0, 0, 0; NaN, NaN, NaN, NaN],...
                [1e-10,    0, 0; NaN,    NaN, NaN]};
switch data
    case 1
%         stimTrainIdxAll = [     
%             %|-------cat 1-------|   |-------cat 2-------|
%              0     3     5     6     9    10    12    15 %dimensional
%              3     6     9    12     0     5    10    15 %crisscross
%              5     6     9    10     2     4    11    13 %intext
%              2     5     8    12     3     7    10    13] ; %diagonal
%         nstim_axes = [4,4]; %This tells us that the stimulis are organised as a 4 by 4 array
%         nstim = prod(nstim_axes);
%         stimTrainIdxAll = stimTrainIdxAll + 1; %Adjust indexing from 1 (instead of 0)
%         stimTestIdx = repmat(1:nstim,size(stimTrainIdxAll,1),1); %test entire stimulus space
        m = {'Dimensional','CrissCross','InterExter','Diagonal'};
%         p2El = 16;
    case 2
%                           %|---cat1---||---cat2---|
%         stimTrainIdxAll = [0, 1, 2, 3, 4, 5, 6, 7;    %Type I
%                            2, 3, 4, 5, 0, 1, 6, 7;    %Type II
%                            0, 2, 3, 7, 1, 4, 5, 6;    %Type III
%                            0, 2, 3, 6, 1, 4, 5, 7;    %Type IV
%                            0, 2, 3, 5, 1, 4, 6, 7;    %Type V
%                            1, 2, 4, 7, 0, 3, 5, 6]; %Type VI 
%         nstim_axes = [2,2,2]; %This tells us that the stimulis are organised as a 4 by 4 array
%         nstim = prod(nstim_axes);
%         stimTrainIdxAll = stimTrainIdxAll + 1; %Adjust indexing from 1 (instead of 0)
%         stimTestIdx = stimTrainIdxAll(:,1:4);
        m = {'Type I','Type II','Type III','Type IV','Type V',' Type VI'};
%         p2El = 4;
end
stimTrainIdxAll = stimTrainIdxAll(:,:); %test one condition for now 060318
nConditions = size(stimTrainIdxAll,1);
categoriesSet = repmat([ones(1,4),ones(1,4)*2],nConditions,1);
stimCoords = ndspace(nstim_axes(1),numel(nstim_axes));%entire stimulus space
% task = 'assign';


%Pack stim-related vars
stim{1} = stimTestIdx;
stim{2} = stimTrainIdxAll;
stim{3} = categoriesSet;
stim{4} = stimCoords; 
stim{5} = task;

p = zeros(numel(tradeoff_list),nConditions);
p2 = p;
dAll = zeros(size(stimTrainIdxAll,2),size(stimTestIdx,2),nConditions);
ll = zeros(numel(tradeoff_list),numel(models));
for i = 1:numel(tradeoff_list)
    tradeoff = tradeoff_list(i);
    parms = [specificity,tradeoff,determinism,baselinesim];
    for j = 1:nConditions
        stimTest = stimCoords(stimTestIdx(j,:),:);
        stimTrain = stimCoords(stimTrainIdxAll(j,:),:);
        categories = categoriesSet(j,:);
        [ptemp,dAll(:,:,j)] = PACKER(parms,stimTest,stimTrain,categories,task);
        p(i,j) = ptemp(1);%mean(ptemp);
        p2(i,j) = ptemp(p2El);
        %d(:,j) = mean(dAll,2);       
    end
    %Get nLL
    for j = 1:numel(models)
        if j == 2
            parmst = parms;
            parmst(2) = []; %remove tradeoff
        else
            parmst = parms;
        end
        model = models{j};
        parmsMin = parmRulesAll{j}(1,:);
        parmsMax = parmRulesAll{j}(2,:);
        parmst = parmsxform(parmst,parmsMin,parmsMax,1);
        ll(i,j) = loglike(parmst,model,data_k,data_total,stim,parmRulesAll{j});
    end
    catd_mean = squeeze(mean(mean(dAll(5:8,:,:))));
    temp = [];
end



figure
hold on
for i = 1:nConditions
    h(i) = plot(tradeoff_list,p(:,i));
    if plot2
        getcolor = get(h(i),'Color');
        h2 = plot(tradeoff_list,p2(:,i),'--');
        set(h2,'Color',getcolor,'LineWidth',2)
    end
end
legend(h,m)
xlabel('gamma')
ylabel(sprintf('p(%s)',task))
ylim([0 1])
%plot grid lines
plot([0 1],[0 0],'--k')
plot([.5 .5],[0 1],'--k')


%plot nLL
figure
hold on
for j = 1:numel(models)
    plot(tradeoff_list,-ll(:,j));
end
legend('PACKER','CopyTweak')