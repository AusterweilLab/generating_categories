import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from BF import BFtt #bayes factor from bayesian t-test
from statsmodels.stats.multicomp import pairwise_tukeyhsd as tukey
from statsmodels.stats.libqsturng import psturng
sns.set_style("whitegrid")
#colors = ["#000000", "#222222"]#["#34495e", "#e74c3c"]
#sns.set_palette('binary')
#Colormap is now set to grayscale and is determined once the number of conditions per plot is known



#count only first 4 trials?
testconds = ['gentype']#['condition','gentype','condcomb']
trialsplit = 'splitgamma' #first4 splitgamma splitall
first4str = ''
savestr = ''
plot_alpha = False #plot alpha scatterplots

if 'gentype' in testconds:
    savestr += 'instr'
if 'condition' in testconds:
    savestr += 'cond'
if 'condcomb' in testconds:
    savestr += 'comb'
    
pd.set_option('display.width', 1000, 'precision', 2, 'display.max_rows', 999)


execfile('Imports.py')
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition, gentype from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).values

con.close()


gentypebase = range(3)
gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma

if trialsplit=='first4':
    first4str = 'first4'
    stats = []
    #Build new stats battery only looking at first 4 trials
    for i,row in info.iterrows():
        pid,condition,gentype = int(row.participant), row.condition, row.gentype
        palphas = alphas[condition]
        pbetas_all = df.stimulus[df.participant == pid]
        pbetas  = pbetas_all[0:4]#remove last 4
        statst = funcs.stats_battery(stimuli[pbetas],stimuli[palphas])
        statst.update({'participant':pid})
        stats.append(statst)
    stats = pd.DataFrame(stats)
elif trialsplit=='splitgamma':
    gentypebase = range(4)
    #gentypeStr = ['Not Alpha','Beta Only','Beta and Gamma\n(Beta categories)','Beta and Gamma\n(Gamma categories)'] #not alpha, beta from beta, beta from gamma, gamma from gamma
    gentypeStr = ['A\'','B','BC-B','BC-C'] #not alpha, beta from beta, beta from gamma, gamma from gamma
    first4str = 'splitgamma'
    stats = []
    #Build new stats battery only looking at first 4 trials
    for i,row in info.iterrows():
        pid,condition,gentype = int(row.participant), row.condition, row.gentype
        palphas = alphas[condition]
        pbetas = df.stimulus[df.participant == pid]
        if gentype==2:
            #First round normal
            statst = funcs.stats_battery(stimuli[pbetas[0:4]],stimuli[palphas])
            statst.update({'participant':pid})
            stats.append(statst)
            #Second round add 9000 to pid
            statst = funcs.stats_battery(stimuli[pbetas[4:8]],stimuli[palphas])
            statst.update({'participant':pid+9000}) #Add a dummy participant to indicate different group
            stats.append(statst)
            info = info.append({'participant':pid+9000,'condition':condition,'gentype':3},ignore_index=True)

        else:
            statst = funcs.stats_battery(stimuli[pbetas],stimuli[palphas])
            statst.update({'participant':pid})
            stats.append(statst)

    stats = pd.DataFrame(stats)
elif trialsplit=='splitall':
    gentypebase = [0,3,1,4,2,5]
    gentypeStr = ['N1','N2','B1','B2','BB','BC']

    first4str = 'splitall'
    stats = []
    #Build new stats battery only looking at first 4 trials
    for i,row in info.iterrows():
        pid,condition,gentype = int(row.participant), row.condition, row.gentype
        palphas = alphas[condition]
        pbetas = df.stimulus[df.participant == pid]
        #First round normal
        statst = funcs.stats_battery(stimuli[pbetas[0:4]],stimuli[palphas])
        statst.update({'participant':pid})
        stats.append(statst)
        #Second round add 9000 to pid
        statst = funcs.stats_battery(stimuli[pbetas[4:8]],stimuli[palphas])
        statst.update({'participant':pid+9000}) #Add a dummy participant to indicate different group
        stats.append(statst)
        info = info.append({'participant':pid+9000,'condition':condition,'gentype':gentype+3},ignore_index=True)
    stats = pd.DataFrame(stats)

stats = pd.merge(info, stats, on = 'participant')

#Create and add new stats column so it's easier for sns.factorplot?
condcomb = [str(row.condition[0])+str(gentypeStr[row.gentype]) for idx,row in stats.iterrows()]
stats['condcomb'] = condcomb



#print stats[['condcomb','yrange','correlation']]

order = {}
order['condition'] = ['Cluster','Row','XOR']
order['gentype'] = gentypebase
order['condcomb'] = ['CN','CB','CC','RN','RB','RC','XN','XB','XC']
conditionticks = ['Cluster','Row','Diagonal'] #Special ticks for the alpha conditions
#Get alpha stats for comparison
stats_alpha = []
for condition in order['condition']:
    palphas = alphas[condition]
    stats_alpha += [funcs.stats_battery(stimuli[palphas],stimuli[palphas])]



fh, axes = plt.subplots(len(testconds),4,figsize = (12,3*len(testconds)))
#fh, axes = plt.subplots(2,2,figsize = (12,12))
for i, col in enumerate(['xrange','yrange','correlation','area']):
    for ii,conditions in enumerate(testconds):
        #Set colormap
        csteps = len(order[conditions])
        palette = [[1-float(rc)/csteps for rrc in range(3)] for rc in range(csteps)]
        sns.set_palette(palette)
        #print(sns.color_palette())

        if len(testconds)>1:#len(axes.shape)>1:
            ax = axes[ii,i]
        else:
            ax = axes.flat[i]
        hs = sns.catplot(x = conditions, y = col, data= stats, ax = ax, kind = 'box',
                        order = order[conditions])
        ax.set_title(col, fontsize = 12)
        ax.set_ylabel('')
        xvals = ax.get_xticks()
        if plot_alpha and not conditions=='gentype':
            #build stats alpha
            yvals = []                
            for sa in stats_alpha:
                if conditions=='condition':
                    yvals += [sa[col]]
                elif conditions=='condcomb':
                    yvals += [sa[col]]*3

            ax.scatter(xvals, yvals,marker='x')
        if conditions == 'gentype':
            ax.set_xticklabels(gentypeStr)
        elif conditions == 'condition':
            ax.set_xticklabels(conditionticks)
        if 'range' in col:
            ax.set_title(col[0].upper() + ' Range', fontsize = 12)

            ax.set_yticks([0,2])
            ax.set_yticklabels(['Min','Max'])
        elif col=='correlation':
            ax.set_title('Correlation', fontsize = 12)
            ax.set_yticks([-1,-0.5,0,0.5,1])
            ax.set_yticklabels(['-1','-0.5','0','0.5','1'])
        else:
            ax.set_title('Area', fontsize = 12)
            #ax.set_yticks([-1,-0.5,0,0.5,1])
            #ax.set_yticklabels(['-1','-0.5','0','0.5','1'])
            
        ax.tick_params(labelsize = 11)
        ax.set_xlabel('')
        ax.xaxis.grid(False)

fh.subplots_adjust(wspace=0.4)
fh.savefig('stats/statsboxes_{}{}.pdf'.format(savestr,first4str), bbox_inches = 'tight')
savetext = 'stats/report_{}{}.txt'.format(savestr,first4str)
#path = '../../../Manuscripts/cog-psych/figs/e2-statsboxes.pgf'
#funcs.save_as_pgf(fh, path)

# hypothesis tests
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp, wilcoxon, ranksums, f_oneway
from itertools import combinations

#Initialise report
with open(savetext,'w') as f:
    f.write('')

def print_ttest(g1, g2, fun):
    res = fun(g1,g2)
    S = 'T = ' + str(round(res.statistic, 4))
    S+= ', p = ' + str(round(res.pvalue, 10))
    S+= '\tMeans:'
    for j in [g1, g2]:
        S += ' ' + str(round(np.mean(j), 4))
        S +=  ' (' + str(round(np.std(j), 4)) + '),'
    print S
    with open(savetext,'a') as f:
        f.write(S+'\n')
    
pstr = '\n---- XOR X vs. Y:'
print pstr
with open(savetext,'a') as f:
    f.write(pstr+'\n')
g1 = stats.loc[stats.condition == 'XOR', 'xrange']
g2 = stats.loc[stats.condition == 'XOR', 'yrange']
print_ttest(g1,g2, ttest_rel)

pstr =  '\n---- Cluster X vs. Y:'
print pstr
with open(savetext,'a') as f:
    f.write(pstr+'\n')
g1 = stats.loc[stats.condition == 'Cluster', 'xrange']
g2 = stats.loc[stats.condition == 'Cluster', 'yrange']
print_ttest(g1,g2, ttest_rel)

pstr =  '\n---- Row X vs. Y:'
print pstr
with open(savetext,'a') as f:
    f.write(pstr+'\n')
g1 = stats.loc[stats.condition == 'Row', 'xrange']
g2 = stats.loc[stats.condition == 'Row', 'yrange']
print_ttest(g1,g2, ttest_rel)

pstr = '\n---- XOR positive correlation?'
print pstr
with open(savetext,'a') as f:
    f.write(pstr+'\n')
g1 = stats.loc[stats.condition == 'XOR', 'correlation']
print ttest_1samp(g1, 0).pvalue
print wilcoxon(g1).pvalue

pstr = '\n---- within vs. between?'
print pstr
with open(savetext,'a') as f:
    f.write(pstr+'\n')
for n, rows in stats.groupby('condcomb'):
    print '\t'+n+':'
    g1 = rows.loc[:,'between']
    g2 = rows.loc[:,'within']
    print_ttest(g1,g2, ttest_rel)

# between conditions
stats_interests = [stats.condition,stats.gentype]
for stats_interest in stats_interests:
    pstr = '\n---- Between conditions-{}'.format(stats_interest.name)
    print pstr
    with open(savetext,'a') as f:
        f.write(pstr+'\n')
    for j in ['xrange','yrange','correlation','area']:
        pstr = 'Variable: ' + j + '\n' + 'Omnibus test'
        print pstr
        with open(savetext,'a') as f:
            f.write(pstr+'\n')
        d = [stats.loc[stats_interest==statsi,j] for statsi in pd.unique(stats_interest)]
        f,p = f_oneway(d[0],d[1],d[2])#Note this needs to account for number of levels, not fix it at 3. 
        pstr =  'F = {}, p = {}'.format(f,p)
        print pstr
        with open(savetext,'a') as f:
            f.write(pstr+'\n')
        res = tukey(stats[j],stats_interest)
        pvals = psturng(np.abs(res.meandiffs / res.std_pairs), len(res.groupsunique), res.df_total)

        #Generate pairwise comparison array and then Bayesian t test
        aa = range(len(res.groupsunique))
        compareidx = [[x,y] for i,x in enumerate(aa) for h,y in enumerate(aa) if h > i]
        BF01s = []
        ts = []
        dfs = []
        for compair in compareidx:
            g1 = res.groupsunique[compair[0]]
            g2 = res.groupsunique[compair[1]]
            data1 = stats.loc[stats_interest==g1,j]
            data2 = stats.loc[stats_interest==g2,j]
            ttest_res = ttest_ind(data1,data2)
            N = len(data1) + len(data2)            
            ts += [ttest_res.statistic]
            dfs += [N-2] #2 groups
            BF01s += [BFtt(N,ttest_res.statistic)]
            
        resstr = str(res)
        #add p-values and Bayes Factors to print
        resstr = resstr.replace('reject', 'reject   p     t(df)    BF01   BF10') 
        for ri in range(len(pvals)):
            if 'True \n' in resstr:
                idxt = resstr.index('True \n')
            else:
                idxt = len(resstr)+1
            if 'False \n' in resstr:
                idxf = resstr.index('False \n')
            else:
                idxf = len(resstr)+1
            if idxt < idxf:
                resstr = resstr.replace('True \n', 'True {0:.4f} {1:.2f}({2:d}) {3:.2E} {4:.2E} \n'.format(pvals[ri],ts[ri],dfs[ri],BF01s[ri],1/BF01s[ri]),1)
            else:
                resstr = resstr.replace('False \n', 'False {0:.4f} {1:.2f}({2:d}) {3:.2E} {4:.2E} \n'.format(pvals[ri],ts[ri],dfs[ri],BF01s[ri],1/BF01s[ri]),1)

        pstr = resstr + '\n p = ' + str(pvals) + '\n ---------------------------------------------'
        print pstr
        with open(savetext,'a') as f:
            f.write(pstr+'\n')

    # print 'p = ' + str(pvals)
    # print '-

cols = ['condition', 'between', 'correlation', 'within', 'xrange', 'yrange']
print stats[cols].groupby('condition').describe()
