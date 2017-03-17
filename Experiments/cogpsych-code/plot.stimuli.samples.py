import matplotlib.pyplot as plt

execfile('Imports.py')
import Modules.Funcs as funcs

# params
linewidth = 1
colors = [25, 230]
sizes = [3.0, 5.8]

combos = [(i,j) for i in colors for j in sizes]

f, ax = plt.subplots(1,4, figsize = (3,1))
for i, (color, size) in enumerate(combos):

	offset = (5.8 - size)/2
	x = [offset, offset+size, offset+size, offset, offset]
	y = [offset, offset, offset+size, offset+size, offset]
	rgb = [color/255.0 for k in range(3)]

	h = ax[i]
	h.fill(x,y,facecolor = rgb, edgecolor='k')
	h.axis([-0.1, 5.9, -0.1, 5.9])
	h.set_yticks([])
	h.set_xticks([])
	for k in ['top','right','bottom','left']:
		h.spines[k].set_visible(False)
	h.set_aspect('equal', adjustable='box')

plt.tight_layout(pad=-0.0, w_pad=-0.0)
f.savefig('stimuli.samples.png', bbox_inches = 'tight')

path = '../../Manuscripts/cog-psych/figs/stimuli-samples.pgf'
funcs.save_as_pgf(f, path)