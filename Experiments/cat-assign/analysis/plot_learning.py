import sqlite3, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

savedir = 'individual_learn'

colors = ["#34495e", "#e74c3c"]
sns.set_palette(colors)

execfile('Imports.py')
import Modules.Funcs as funcs

#Import data
con = sqlite3.connect('../data_utilities/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * from assignment", con)
goodnessE = pd.read_sql_query("SELECT * from goodnessExemplars", con)
goodnessC = pd.read_sql_query("SELECT * from goodnessCategories", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
#stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

#Import matched data
matchdata = '../data_utilities/midbot/experiment.db'
con_m = sqlite3.connect(matchdata)
info_m = pd.read_sql_query("SELECT * from participants", con_m)
df_m = pd.read_sql_query("SELECT * from generation", con_m)
alphas_m = pd.read_sql_query("SELECT * from alphas", con_m)
stimuli_m = pd.read_sql_query("SELECT * from stimuli", con_m).as_matrix()
con_m.close()

#fh, ax = plt.subplots(2,1,figsize = (2.7,6))
#fh, ax = plt.subplots(1,1,figsize = (2.7,6))

styles = dict(Middle = '-o', Bottom = '-s')
main_font = 13
sub_font = 11


#Compute learning curves, averaged within each block
for i, row in info.iterrows():
    fh, ax = plt.subplots(1,2,figsize = (12,6))
    ppt  = row.participant
    pptAssign = assignment.loc[assignment['participant']==ppt].sort_values('trial')
    nBaseStim = len(eval(row.categories))
    nTrials = len(pptAssign)
    nBlocks = nTrials / nBaseStim
    blockIdx = np.array(range(nBlocks)).repeat(nBaseStim)
    error = [];
    for j in range(nBlocks):
        blockAssign = pptAssign.iloc[blockIdx==j]
        accuracyEl = float(sum(blockAssign.correctcat == blockAssign.response))/nBaseStim
        error.append(1-accuracyEl)
        
    #Prepare to plot configuration
    #get matched data
    matchdb='../data_utilities/cmp_midbot.db'
    matched = funcs.getMatch(ppt,matchdb)

    condition = row.condition
    palphas = alphas_m[condition]
    pbetas = df_m.stimulus[df_m.participant == matched]
    #Plot learning curves
    x = range(nBlocks)
    y = error
    ax[0].plot(x, y, '-s', alpha = 1)
    # plt.ylim((0,1))
    # plt.xlabel('Block')
    # plt.xticks(range(nBlocks))
    axes = plt.gca()
    #ax[0].set_xlim([xmin,xmax])
    ax[0].set_ylim([0,1])
    ax[0].set_xlabel('Block')
    ax[0].set_ylabel('p(error)')
    ax[0].xaxis.set_ticks(range(nBlocks))
    ax[0].set_title('Learning curve')
    #Plot condigurations
    funcs.plotclasses(ax[1], stimuli_m, palphas, pbetas)
    ax[1].set_title('Stimulus Configuration\n ID Old: {} ID Current:{}'.format(matched,ppt))
    
    fname = os.path.join(savedir,str(ppt) + '.png')
    fh.savefig(fname, bbox_inches='tight', transparent=False)
    plt.cla()
    
   

#funcs.save_as_pgf(fh, path)

    
# for i, (c, rows) in enumerate(ngenerations.groupby('condition')):

# 	As = stimuli[alphas[c],:]
# 	D = funcs.pdist(stimuli, As)
# 	D = np.mean(D, axis = 1)
# 	x = np.unique(D)
# 	y = []
# 	for j in x:
# 		nums = np.where(D == j)[0]
# 		curr_rows = rows.loc[rows.stimulus.isin(nums)]
# 		counts = curr_rows['count'].as_matrix()
# 		y.append(np.mean(counts))
# 	print y

# 	x = x - min(x)
# 	x = x / max(x)
# 	h.plot(x, y, styles[c], alpha = 1, label = c)




