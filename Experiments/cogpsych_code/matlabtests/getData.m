function [data_k,data_total,data_p,nstim_axes,stimTrainIdxAll,stimTestIdx,task,p2El] = getData(data)

switch data
    case 'nosofsky1986'
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
        nstim_axes = [4,4]; %This tells us that the stimulis are organised as a 4 by 4 array
        nstim = prod(nstim_axes);

%         categoriesSet = repmat([ones(1,4),ones(1,4)*2],nconditions,1);
        
        stimTrainIdxAll = [
            %|-------cat 1-------|   |-------cat 2-------|
            0     3     5     6     9    10    12    15 %dimensional
            3     6     9    12     0     5    10    15 %crisscross
            5     6     9    10     2     4    11    13 %intext
            2     5     8    12     3     7    10    13] ; %diagonal
        stimTrainIdxAll = stimTrainIdxAll + 1; %Adjust indexing from 1 (instead of 0)
        stimTestIdx = 1:nstim; %test entire stimulus space
        nconditions = size(stimTrainIdxAll,1);
        stimTestIdx = repmat(stimTestIdx,nconditions,1);
        data_k = assignCat1;
        data_total = assignCat1+assignCat2;
        data_p = data_k./data_total;
        p2El = 16;
%         stimCoords = ndspace(4,2);%entire stimulus space
    case 'NGPMG1994'
        nstim_axes = [2,2,2]; %This tells us that the stimuli are organised as a 4 by 4 array
        nstim = prod(nstim_axes);
        ntrials = 200;
        task = 'error';
                          %|---cat1---||---cat2---|
        stimTrainIdxAll = [0, 1, 2, 3, 4, 5, 6, 7;    %Type I
                           2, 3, 4, 5, 0, 1, 6, 7;    %Type II
                           0, 2, 3, 7, 1, 4, 5, 6;    %Type III
                           0, 2, 3, 6, 1, 4, 5, 7;    %Type IV
                           0, 2, 3, 5, 1, 4, 6, 7;    %Type V
                           1, 2, 4, 7, 0, 3, 5, 6]; %Type VI 
        stimTrainIdxAll = stimTrainIdxAll + 1; %Adjust indexing from 1 (instead of 0)                       
        nconditions = size(stimTrainIdxAll,1);
        perror= [.010, .032, .061, .065, .075, .143]'; %
        assignCat1 = repmat(perror,1,nstim);
        catIdx = [ones(1,4),ones(1,4)*2];
        for i = 1:nconditions
           assignOther = stimTrainIdxAll(i,catIdx==1);
           assignCat1(i,assignOther) = 1-assignCat1(i,assignOther);
        end
        assignCat1 = round(assignCat1*ntrials);
        assignCat2 = ntrials-assignCat1;

        data_k = assignCat1;
        data_total = assignCat1+assignCat2;
        data_p = data_k./data_total;
        
        stimTestIdx = stimTrainIdxAll;%stimTrainIdxAll(:,1:4);
        m = {'Type I','Type II','Type III','Type IV','Type V',' Type VI'};
        p2El = 4;

end