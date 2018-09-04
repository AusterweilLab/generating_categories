import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
sns.set_palette("cubehelix")

from scipy.stats import binom, chisquare

execfile('Imports.py')
import Modules.Funcs as funcs
from JK13 import JK13, JKFuncs

# import data
con = sqlite3.connect('experiment.db')
distances = pd.read_sql_query("SELECT * from distances", con)
training = pd.read_sql_query("SELECT * from training", con)
generation = pd.read_sql_query("SELECT * from generation", con)
con.close()

# set hue categories
# hues = np.array([[0,30,60,90,120,150,180,210,240,270,300,330,360]]).T / 360.0
hues = np.array([[0, 45, 90, 135, 180, 225, 270, 315, 360]]).T / 360.0

for i in range(1,len(hues)):
	print hues[i-1][0], (hues[i][0] + hues[i-1][0])/2.0, hues[i][0]

# get number of distinct items for each participant
shared_hues = dict( (i,np.array([])) for i in JK13.conditions)
for (i, c), rows in generation.groupby(['participant','condition']):
	idx = (training.participant == i) & (training.condition == c)
	As = JKFuncs.dummycode_colors(training.loc[idx].Hue.as_matrix(), hues=hues)
	Bs = JKFuncs.dummycode_colors(rows.Hue.as_matrix(), hues=hues)
	num_distinct = np.sum(np.in1d(Bs,As)==1)
	shared_hues[c] = np.append(shared_hues[c],num_distinct)

linestyles = dict(
	Positive = '-^',
	Neutral = '-o',
	Negative = '-v',
	)


fh = plt.figure(figsize = (4.5,3))

# compute expected values
n = 6 # number of trials
p = 2.0/(len(hues)-1) # baserate of overlap (2 categories, N bins)
expected = binom.pmf(range(n+1), n, p) * 22

x = range(0,7)
#chi-sq test with binomial
for i, k in enumerate(['Positive','Neutral','Negative']):
	v = shared_hues[k]
	y = funcs.histvec(v, x, density = False)
	print k, chisquare(y, expected)
	plt.plot(x, y, linestyles[k], lw = 1, label = k)

# set binomial line
plt.bar(x, expected + 0.75, 1, # added 0.75 to adjust for bottom of bar at -0.75
	facecolor = [0.7,0.7,0.7], edgecolor = 'k', linewidth = 0.75,
	label = 'Expected (Binomial)', bottom = -0.75)

#chi-sq test assuming regularity
expected_reg = [16.5,0,0,0,0,0,5.5]
for i, k in enumerate(['Positive','Neutral','Negative']):
	v = shared_hues[k]
	y = funcs.histvec(v, x, density = False)
	print k, chisquare(y, expected_reg)
	#plt.plot(x, y, linestyles[k], lw = 1, label = k)


plt.axis([-0.6,6.6,-0.75,22.75])
plt.gca().xaxis.grid(False)
plt.xticks(range(7))
plt.legend(frameon = True, edgecolor = 'k')
plt.xlabel('Items Sharing Hue with Known Categories',fontsize = 12)
plt.yticks(np.linspace(0,22,12))
plt.ylabel('Participants', fontsize = 12)

fname = 'distinct-hues'
fh.savefig(fname + '.png', bbox_inches = 'tight', pad_inches=0.0)

#path = '../../Manuscripts/cog-psych/figs/jk13-huecontrast.pgf'
#funcs.save_as_pgf(fh, path)

		
