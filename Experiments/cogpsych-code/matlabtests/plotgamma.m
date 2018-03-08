%Plot a figure showing how changing gamma (tradeoff) affects the order of SHJ types

%These are the best spec and determinism fits to NGPMG1994
specificity = .5;%56.68699728478552;
tradeoff_list = 0:.1:1; %0.25750159353896424
determinism = 4 ;%2.751535314273929;




                 %|---cat1---||---cat2---|
stimTrainIdxAll = [0, 1, 2, 3, 4, 5, 6, 7;    %Type I
                2, 3, 4, 5, 0, 1, 6, 7;    %Type II
                0, 2, 3, 7, 1, 4, 5, 6;    %Type III
                0, 2, 3, 6, 1, 4, 5, 7;    %Type IV
                0, 2, 3, 5, 1, 4, 6, 7;    %Type V
                1, 2, 4, 7, 0, 3, 5, 6]+1; %Type VI
            
stimTrainIdxAll = stimTrainIdxAll(1,:); %test one condition for now 060318
nConditions = size(stimTrainIdxAll,1);
categoriesSet = repmat([ones(1,4),ones(1,4)*2],nConditions,1);
stimTestIdx = stimTrainIdxAll(:,1:4);

task = 'error';

stimCoords = ndspace(2,3);%entire stimulus space
p = zeros(numel(tradeoff_list),nConditions);
dAll = zeros(size(stimTrainIdxAll,2),size(stimTestIdx,2),nConditions);
for i = 1:numel(tradeoff_list)
    tradeoff = tradeoff_list(i);
    parms = [specificity,tradeoff,determinism];
    for j = 1:nConditions
        stimTest = stimCoords(stimTestIdx(j,:),:);
        stimTrain = stimCoords(stimTrainIdxAll(j,:),:);
        categories = categoriesSet(j,:);
        [ptemp,dAll(:,:,j)] = PACKER(parms,stimTest,stimTrain,categories,task);
        p(i,j) = mean(ptemp);
        %d(:,j) = mean(dAll,2);       
    end
    catd_mean = squeeze(mean(mean(dAll(5:8,:,:))));
    temp = [];
end

p



figure
hold on
for i = 1:nConditions
    plot(tradeoff_list,p(:,i))
end
legend('Type I','Type II','Type III','Type IV','Type V', 'Type VI')
xlabel('gamma')
ylabel('p(error)')