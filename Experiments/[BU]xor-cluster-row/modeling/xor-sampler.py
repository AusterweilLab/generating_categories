import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

execfile('Imports.py')
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

xor_alphas = stimuli[alphas['XOR'].as_matrix(),:]
nsamples = 10000
nstimuli = stimuli.shape[0]

# get samples
stats = []
for i in range(nsamples):
	betas = np.random.choice(nstimuli, size = 4, replace = False)
	betas = stimuli[betas,:]
	stats.append(funcs.stats_battery(betas, alphas = xor_alphas))

stats = pd.DataFrame(stats)

fh = plt.figure(figsize = (5,5))

print stats.describe()

x = stats.correlation
y = funcs.jitterize(stats.between, sd = 0.0075)
plt.plot(stats.correlation, y, 'o', alpha = 500.0 / nsamples)
plt.xlabel('Correlation')
plt.ylabel('Between Class Distance')
fh.savefig('xor-sampler.png')
