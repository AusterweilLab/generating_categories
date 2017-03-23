import sqlite3, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

execfile('Imports.py')
import Modules.Funcs as funcs

pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()

con.close()

textsettings = dict(fontsize = 6)

# ASSIGN SUBPLOTS TO CONDITIONS
#  		 CLUSTER   		 #      	  ROW      		 #      	  XOR         #
#  0		 1		 2  	 3     4     5  	 6 	 	 7     8     9  	 10
# 11		12		13		14		15		16		17		18		19		20		 21
# 22		23		24		25		26		27		28		29		30		31		 32


P, E = 2, 0.2
gridspec_kw = {'width_ratios':[P,P,P, E, P,P,P, E, P,P,P]}
assignments = dict(
	empty = np.array([3, 14, 25, 7, 18, 29]),
	Cluster = np.array([0, 1, 2, 11, 12, 13, 22, 23, 24]))
assignments['Row'] = assignments['Cluster'] + 4
assignments['XOR'] = assignments['Row'] + 4


# plotting
fig, ax= plt.subplots(3,11, figsize=np.array([7.,2.3]) , gridspec_kw = gridspec_kw)
ax_flat = ax.flatten()
for i, h in enumerate(ax_flat):

	if i in assignments['empty']: 
		h.axis('off')
		continue
	
	# get condition
	for k, v in assignments.items():
		if i in v: curr_cond = k

	As = alphas[curr_cond].as_matrix()

	# pick a random participant, get the betas
	while True: # AT least make sure the participant was *trying*
		pid = np.random.choice(info.loc[info.condition==curr_cond, 'participant'])
		Bs = generation.loc[generation.participant==pid, 'stimulus'].as_matrix()
		if np.intersect1d(As,Bs).tolist() == []: break

	# drop participant so they cannot be chosen again
	idx = info.loc[info.participant ==  pid]
	info.drop(idx.index, inplace=True)

	funcs.plotclasses(h, stimuli, As, Bs, textsettings = textsettings)

	if i in [1, 5, 9]:
		h.set_title(curr_cond)

fig.subplots_adjust(wspace = 0.09, hspace = 0.01)
fig.savefig('samples.png', bbox_inches='tight', transparent=False)


path = '../../../Manuscripts/cog-psych/figs/e1-samples.pgf'
funcs.save_as_pgf(fig, path)

