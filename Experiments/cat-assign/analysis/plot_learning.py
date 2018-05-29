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
con = sqlite3.connect('../data/experiment.db')
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
errorAll = pd.DataFrame(columns = ['participant','block0','block1','block2','block3'])
for i, row in info.iterrows():
    fh, ax = plt.subplots(1,2,figsize = (12,6))
    ppt  = row.participant
    pptmatch = row.pptmatch
    pptAssign = assignment.loc[assignment['participant']==ppt].sort_values('trial')
    nBaseStim = len(eval(row.categories))
    nTrials = len(pptAssign)
    nBlocks = nTrials / nBaseStim
    blockIdx = np.array(range(nBlocks)).repeat(nBaseStim)
    error = [];
    errordict = {'participant':pptmatch}
    for j in range(nBlocks):
        blockAssign = pptAssign.iloc[blockIdx==j]
        accuracyEl = float(sum(blockAssign.correctcat == blockAssign.response))/nBaseStim
        error.append(1-accuracyEl)
        errordict['block'+str(j)] = 1-accuracyEl
    errorAll = errorAll.append(errordict, ignore_index=True)
    avgerror = np.mean(error)
    #Prepare to plot configuration
    #get matched data
    matchdb='../data_utilities/cmp_midbot.db'
    matched = funcs.getMatch(pptmatch,matchdb)

    condition = row.condition
    palphas = alphas_m[condition]
    pbetas = df_m.stimulus[df_m.participant == matched]
    #Plot learning curves
    x = range(nBlocks)
    y = error
    ax[0].plot(x, y, '-s', alpha = 1)
    #Plot mean
    #ax[0].plot([0,nBlocks-1],[avgerror, avgerror],'--g')
    # plt.ylim((0,1))
    # plt.xlabel('Block')
    # plt.xticks(range(nBlocks))
    axes = plt.gca()
    #ax[0].set_xlim([xmin,xmax])
    ax[0].set_ylim([0,1])
    ax[0].set_xlabel('Block')
    ax[0].set_ylabel('p(error)')
    ax[0].xaxis.set_ticks(range(nBlocks))
    ax[0].set_title('Learning curve\nmean_error = {:.2f}'.format(avgerror))
    #Plot configurations
    funcs.plotclasses(ax[1], stimuli_m, palphas, pbetas)
    ax[1].set_title('Stimulus Configuration\n ID_Old: {}, ID_Current:{}'.format(matched,ppt))

    fname = os.path.join(savedir,str(matched) + '.png')
    fh.savefig(fname, bbox_inches='tight', transparent=False)
    plt.cla()
    
#Plot average
fh, ax = plt.subplots(1,1,figsize = (6,6))
#Plot learning curves
x = range(nBlocks)
y = []
for i in range(nBlocks):
    y.append(errorAll.mean()['block'+str(i)])
ax.plot(x, y, '-s', alpha = 1)
#Plot mean
avgerror = np.mean(y)
ax.plot([0,nBlocks-1],[avgerror, avgerror],'--g')
# plt.ylim((0,1))
# plt.xlabel('Block')
# plt.xticks(range(nBlocks))
axes = plt.gca()
#ax[0].set_xlim([xmin,xmax])
ax.set_ylim([0,1])
ax.set_xlabel('Block')
ax.set_ylabel('p(error)')
ax.xaxis.set_ticks(range(nBlocks))
ax.set_title('Global learning curve\nN = {}, grand_mean_error = {:.2f}'.format(len(info),avgerror))
    
fname = os.path.join(savedir,'All.png')
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




