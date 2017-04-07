import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

import colorsys

execfile('Imports.py')
import Modules.Funcs as funcs
from JK13 import JK13

# import data
con = sqlite3.connect('experiment.db')
distances = pd.read_sql_query("SELECT * from distances", con)
training = pd.read_sql_query("SELECT * from training", con)
generation = pd.read_sql_query("SELECT * from generation", con)
con.close()


# get all pairwise distances
distinct_items = dict( (i,np.array([])) for i in JK13.conditions)

print JK13.features

def dummycode_colors(X):
	# hue_categories = np.array([[0,60,120,180,240,300,360]]).T / 360.0
	hue_categories = np.array([[0,60,120,180,240,300,360]]).T / 360.0
	k = len(hue_categories)
	D = np.abs(hue_categories - np.atleast_2d(np.array(X)))
	assignment = np.argmin(D, axis=0)
	assignment[assignment==(k-1)] = 0
	return assignment

for (i, c), rows in generation.groupby(['participant','condition']):
	idx = (training.participant == i) & (training.condition == c)
	As = dummycode_colors(training.loc[idx].Hue.as_matrix())
	Bs = dummycode_colors(rows.Hue.as_matrix())
	num_distinct = np.sum(np.in1d(Bs,As)==0)
	distinct_items[c] = np.append(distinct_items[c],num_distinct)

fh = plt.figure(figsize = (2.7,2.7))

x = range(0,7)

for i, k in enumerate(['Positive','Neutral','Negative']):
	v = distinct_items[k]
	y = funcs.histvec(v, x, density = False)
	plt.plot(x, y, '-o', alpha = 0.7, label = k)

plt.axis([-0.5,6.5,-0.05,22])
plt.gca().xaxis.grid(False)
plt.xticks(range(7))
plt.legend()
plt.xlabel('Distinct Hues',fontsize = 12)
plt.yticks(np.linspace(0,22,12))
plt.ylabel('Participants', fontsize = 12)

fname = 'distinct-hues'
fh.savefig(fname + '.png', bbox_inches = 'tight', pad_inches=0.0)

# path = '../../../Manuscripts/cog-psych/figs/e2-distanceplots.pgf'
# funcs.save_as_pgf(fh, path)

		