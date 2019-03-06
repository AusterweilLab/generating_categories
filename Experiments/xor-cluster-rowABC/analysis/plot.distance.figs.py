import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

colors = ["#34495e", "#e74c3c"]
sns.set_palette(colors)

execfile('Imports.py')
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition, gentype from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

stats = pd.merge(stats, info, on = 'participant')
generation = pd.merge(generation, info, on = 'participant')

gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma

ngenerations = pd.DataFrame(dict(
    condition = [],
    stimulus = [],
    count = []
))


for c in pd.unique(info.condition):
    for g in pd.unique(info.gentype):
        gstr = gentypeStr[g]
        for i in range(stimuli.shape[0]):
            count = sum((generation.condition == c) & (generation.stimulus ==i) & (generation.gentype == g))
            row = dict(condition = c+gstr, stimulus = i, count = count)
            ngenerations = ngenerations.append(row, ignore_index = True)


# fh, ax = plt.subplots(1,2,figsize = (6,2.7))
fh, ax = plt.subplots(2,1,figsize = (2.7,6))


styles = dict(XORN = '-or', XORB = '-og', XORC = '-ob',
              ClusterN = '-sr', ClusterB = '-sg', ClusterC = '-sb',
              RowN = '-+r', RowB = '-+g', RowC = '-+b',)
main_font = 13
sub_font = 11
small_font = 8
h = ax[0]
for i, (c, rows) in enumerate(ngenerations.groupby('condition')):
    alphacond = c[:-1]
    gentype = c[-1]
    As = stimuli[alphas[alphacond],:]
    D = funcs.pdist(stimuli, As)
    D = np.mean(D, axis = 1)
    x = np.unique(D)
    y = []
    for j in x:
        nums = np.where(D == j)[0]
        curr_rows = rows.loc[rows.stimulus.isin(nums)]
        counts = curr_rows['count'].as_matrix()
        y.append(np.mean(counts))
    #print y

    x = x - min(x)
    x = x / max(x)
    h.plot(x, y, styles[c], alpha = 1, label = c)

h.xaxis.grid(False)
h.set_xticks([])
h.legend(loc = 'upper left', frameon = True, framealpha = 1, fontsize = sub_font)
styles = dict(XORN = '-or', XORB = '-og', XORC = '-ob',
              ClusterN = '-sr', ClusterB = '-sg', ClusterC = '-sb',
              RowN = '-+r', RowB = '-+g', RowC = '-+b',)


xax = h.axis()
h.text(xax[0],xax[2] -1, 'Min', fontsize = sub_font, va = 'top')
h.text(xax[1],xax[2] -1, 'Max', fontsize = sub_font, va = 'top', ha = 'right')
h.set_xlabel('Distance',fontsize = main_font)
h.set_yticks(np.arange(0,35, 5))
h.set_yticklabels(np.arange(0,35, 5),fontsize = sub_font)
h.set_ylabel('Generations Per Stimulus', fontsize = main_font)
h.set_ylim(0,15)
h = ax[1]


#diagline = 'Within $=$ Between'
diagline = ''
h.plot([0,2],[0,2], '--', color = 'gray', linewidth = 0.5, label = diagline)

for c, rows in stats.groupby(['condition','gentype']):
    cond = c[0]+str(c[1])    
    condStr = c[0]+gentypeStr[c[1]]
    marker = styles[condStr][0]
    color = styles[condStr][1]
    h.plot(rows.within, rows.between,marker = marker, color = color,linestyle='',alpha = 0.5, label = condStr)
    #Add means?
    marker = 'd'
    xmean = rows.within.mean()
    ymean = rows.between.mean()
    #h.plot(xmean, ymean,marker = marker, color = color,linestyle='',alpha = 1, label = '')
    #Remember that my main goal here is to think about ways to detect differences btween the groups - Joe mentioned chi sq bu would that work? 280918
    #not chi-sq but anova with post hoc tests? hrm. 
h.grid(False)


h.set_xticks([])
h.set_yticks([])

h.axis([0, 1.5, 0, 1.5])
h.legend(loc = 'lower right', frameon = True, framealpha = 1, 
         ncol = 2, columnspacing = 0.1, labelspacing = 0.1, fontsize = small_font)
h.set_xlabel('Within-Category Distance',fontsize = main_font)
h.set_ylabel('Between-Category Distance',fontsize = main_font)


fh.subplots_adjust(wspace=0.3)


fname = 'distance.figs'
fh.savefig(fname + '.pdf', bbox_inches = 'tight', pad_inches=0.0, transparent = True)
#fh.savefig(fname + '.png', bbox_inches = 'tight', pad_inches=0.0, transparent = True)

path = '../../../Manuscripts/cog-psych/figs/e2-distanceplots.pgf'
# funcs.save_as_pgf(fh, path)
