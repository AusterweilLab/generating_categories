#for some reason, the individual data in pickles/catassign.p don't have parmnames attached to each individual's fit. This is a little annoying for the code, and so this script just fixes that.
import pickle
tofix = 'pickles/private/chtc_ind_gs_best_params_catassign.p'

with open(tofix,'rb') as f:
    fits  = pickle.load(f)

for modelname in fits.keys():
    parmnames = []
    for ppt in fits[modelname].keys():
        if ppt==0:
            parmnames = fits[modelname][ppt]['parmnames']
        else:
            fits[modelname][ppt]['parmnames'] = parmnames

with open(tofix,'wb') as f:
    pickle.dump(fits,f)
        
            
print 'Done.'
