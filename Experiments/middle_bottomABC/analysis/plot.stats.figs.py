import sqlite3, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.multicomp import pairwise_tukeyhsd as tukey
from statsmodels.stats.libqsturng import psturng
sns.set_style("whitegrid")
colors = ["#34495e", "#e74c3c"]
sns.set_palette(colors)

gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma


pd.set_option('display.width', 1000, 'display.precision', 2, 'display.max_rows', 999)
os.chdir(sys.path[0])


exec(open('Imports.py').read())
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition, gentype from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

stats = pd.merge(stats, info, on = 'participant')

#Create and add new stats column so it's easier for sns.factorplot?
condcomb = [str(row.condition[0])+str(gentypeStr[row.gentype]) for idx,row in stats.iterrows()]
stats['condcomb'] = condcomb

print(stats[['condcomb','yrange','correlation']])

order = {}
order['condition'] = ['Bottom','Middle']
order['gentype'] = [0,1,2]
order['condcomb'] = ['BN','BB','BC','MN','MB','MC']
fh, axes = plt.subplots(3,3,figsize = (7.5,8.5))
for i, col in enumerate(['xrange','yrange','correlation']):
    for ii,conditions in enumerate(['condition','gentype','condcomb']):        
        ax = axes[ii,i]
        hs = sns.catplot(x = conditions, y = col, data= stats, ax = ax, kind = 'box',
                            order = order[conditions])
        #order = sorted(stats[conditions].unique()))               
            #order = ['BN','BB','BC','MN','MB','MC'])
            #order = ['BottomN','BottomB','BottomC','MiddleN','MiddleB','MiddleC'])


        ax.set_title(col, fontsize = 12)
        ax.set_ylabel('')
        if conditions == 'gentype':
            ax.set_xticklabels(['N','B','C'])
        if 'range' in col:
            ax.set_title(col[0].upper() + ' Range', fontsize = 12)

            ax.set_yticks([0,2])
            ax.set_yticklabels(['Min','Max'])

        else:
            ax.set_title('Correlation', fontsize = 12)
            ax.set_yticks([-1,-0.5,0,0.5,1])
            ax.set_yticklabels(['-1','-0.5','0','0.5','1'])
        ax.tick_params(labelsize = 11)
        ax.set_xlabel('')
        ax.xaxis.grid(False)

fh.subplots_adjust(wspace=0.4)
fh.savefig('statsboxes.png', bbox_inches = 'tight')

#path = '../../../Manuscripts/cog-psych/figs/e2-statsboxes.pgf'
#funcs.save_as_pgf(fh, path)

# hypothesis tests
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp, wilcoxon, ranksums, f_oneway
from itertools import combinations

def print_ttest(g1, g2, fun):
    res = fun(g1,g2)
    S = 'T = ' + str(round(res.statistic, 4))
    S+= ', p = ' + str(round(res.pvalue, 10))
    S+= '\tMeans:'
    for j in [g1, g2]:
        S += ' ' + str(round(np.mean(j), 4))
        S +=  ' (' + str(round(np.std(j), 4)) + '),'
    print(S)


print('\n---- Bottom X vs. Y:')
g1 = stats.loc[stats.condition == 'Bottom', 'xrange']
g2 = stats.loc[stats.condition == 'Bottom', 'yrange']
print_ttest(g1,g2, ttest_rel)

print('\n---- Middle X vs. Y:')
g1 = stats.loc[stats.condition == 'Middle', 'xrange']
g2 = stats.loc[stats.condition == 'Middle', 'yrange']
print_ttest(g1,g2, ttest_rel)

print('\n---- Bottom positive correlation?')
g1 = stats.loc[stats.condition == 'Bottom', 'correlation']
print(ttest_1samp(g1, 0).pvalue)
print(wilcoxon(g1).pvalue)

print('\n---- within vs. between?')
for n, rows in stats.groupby('condcomb'):
    print('\t'+n+':')
    g1 = rows.loc[:,'between']
    g2 = rows.loc[:,'within']
    print_ttest(g1,g2, ttest_rel)

# between conditions
print('\n---- Between conditions')
stats_interest = stats.gentype
for j in ['xrange','yrange','correlation']:
    print('Variable: ' + j)
    print('Omnibus test')
    d = [stats.loc[stats_interest==statsi,j] for statsi in pd.unique(stats_interest)]
    f,p = f_oneway(d[0],d[1],d[2])
    print('F = {}, p = {}'.format(f,p))
    res = tukey(stats[j],stats_interest)
    pvals = psturng(np.abs(res.meandiffs / res.std_pairs), len(res.groupsunique), res.df_total)
    print(res)
    print('p = ' + str(pvals))
    print('----------------------------------------------')
    # for a, b in combinations(pd.unique(stats_interest), r=2):
    #     g1 = stats.loc[stats_interest == a, j]
    #     g2 = stats.loc[stats_interest == b, j]
    #     print gentypeStr[a] + ', ' + gentypeStr[b]        
    #     print_ttest(g1,g2, ttest_ind)

cols = ['condition', 'between', 'correlation', 'within', 'xrange', 'yrange']
print(stats[cols].groupby('condition').describe())
