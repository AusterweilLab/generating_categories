
# plotting
f, ax = plt.subplots(5,len(name_2_object)+1,figsize = (10, 10))
for rownum, c in enumerate(row_order):
    A = stimuli[alphas[c],:]
    
    for colnum, lab, in enumerate(col_order):
        data = all_data[lab]
        h = ax[rownum][colnum]
        df = data.loc[data.condition == c]

        # get x/y pos of examples
        x, y = stimuli[:,0], stimuli[:,1]
    
        # compute color value of each example
        vals = np.zeros(stimuli.shape[0])
        for i, row in df.groupby('stimulus'):
            n = row['size'].as_matrix()
            sumx = row['mean'].as_matrix() * n
            vals[int(i)] = (PRIOR_NU * PRIOR_MU +  sumx) / (PRIOR_NU + n)

        print c, colnum, min(vals), max(vals)

        # smoothing
        g = funcs.gradientroll(vals,'roll')[:,:,0]
        g = gaussian_filter(g, SMOOTHING_PARAM)
        vals = funcs.gradientroll(g,'unroll')
        
        im = funcs.plotgradient(h, g, A, [], clim = STAT_LIMS, cmap = 'PuOr')

        # axis labeling
        if rownum == 0:
            h.set_title(col_names_short[colnum], **fontsettings)

        if colnum == 0:
            h.set_ylabel(c, **fontsettings)

        # experiment 1 and 2 markers
        if rownum == 1 and colnum == 0:
            h.text(-3.5, np.mean(h.get_ylim()), 'Experiment 1', 
                ha = 'center', va = 'center', rotation = 90, fontsize = fontsettings['fontsize'] + 1)
            h.plot([-2.7,-2.7],[-9,17],'-', color='gray', linewidth = 1, clip_on=False)

        if rownum == 3 and colnum == 0:
            h.text(-3.5, -0.5, 'Experiment 2', 
                ha = 'center', va = 'center', rotation = 90, fontsize = fontsettings['fontsize'] + 1)
            h.plot([-2.7,-2.7],[-9,8],'-', color='gray', linewidth = 1, clip_on=False)


# add colorbar
cbar = f.add_axes([0.21, -0.02, 0.55, 0.03])
f.colorbar(im, cax=cbar, ticks=[-2, 2], orientation='horizontal')
cbar.set_xticklabels([
    'Vertically Aligned\nCategory', 
    'Horizontally Aligned\nCategory', 
],**fontsettings)
cbar.tick_params(length = 0)

plt.tight_layout(w_pad=-2.0, h_pad= .5)

fname = 'gradients-' + STAT_OF_INTEREST
f.savefig(fname + '.pdf', bbox_inches='tight', transparent=False)
#f.savefig(fname + '.png', bbox_inches='tight', transparent=False)

path = '../../Manuscripts/cog-psych/revision/figs/range-diff-gradients.pgf'
funcs.save_as_pgf(f, path)
