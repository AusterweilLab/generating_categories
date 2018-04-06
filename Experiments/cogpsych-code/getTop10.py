#For each model, get top 10 best and worst fits

models = ['PACKER','Copy and Tweak', 'Hierarchical Sampling']

#check gs pickle
#pickledir = '/pickles'
with open('pickles/gs_best_params_NGPMG1994.p','rb') as f:
        ...:     fits = pickle.load(f)

