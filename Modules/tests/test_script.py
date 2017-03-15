import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(precision = 2, linewidth = 120)


execfile('Imports.py') 
from Modules.Classes import PPOLR, Packer
import Modules.Funcs as funcs

# [[72 73 74 75 76 77 78 79 80]
#  [63 64 65 66 67 68 69 70 71]
#  [54 55 56 57 58 59 60 61 62]
#  [45 46 47 48 49 50 51 52 53]
#  [36 37 38 39 40 41 42 43 44]
#  [27 28 29 30 31 32 33 34 35]
#  [18 19 20 21 22 23 24 25 26]
#  [ 9 10 11 12 13 14 15 16 17]
#  [ 0  1  2  3  4  5  6  7  8]]
stimuli = np.fliplr(funcs.ndspace(9,2))

categories = [
	stimuli[[10, 19, 28],:],
	]

packer_params = dict(
	specificity = 2, 
	between = -2,  
	within = 0, 
	determinism = 10, 
	)

ppolr_params = dict(
	retrieval_determinism = 0,
	weights_determinism = 0
	)
ppolr_params.update(packer_params)

models = [
	[Packer, packer_params],
	[PPOLR, ppolr_params]
]

f, ax = plt.subplots(1,3, figsize = (7, 2))
pd = dict()
for i, (M, params) in enumerate(models):
	ps = M(categories, params).get_generation_ps(stimuli, 1)
	pd[M.model] = ps

	g = funcs.gradientroll(ps,'roll')[:,:,0]
	print g
	print ''

	funcs.plotgradient(ax[i], g, categories[0], [], clim = [0, .1])
	ax[i].set_title(M.model)


h = ax[2]
plt.plot(pd['PACKER'], pd['PPOLR'], 'o')
plt.xticks([])
plt.yticks([])
plt.xlabel('PACKER')
plt.ylabel('PPOLR')


f.savefig('test.png', bbox_inches='tight', transparent=False)
