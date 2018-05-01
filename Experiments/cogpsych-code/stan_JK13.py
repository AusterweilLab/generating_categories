import pystan
import os
import numpy as np
import matplotlib.pyplot as plt
#Initialise the saveload functions so I won't need to compile the model everytime
import init_stan as ist

if not 'force_recompile' in locals():
    force_recompile = False;

modeldir = 'models'
import os
if not os.path.isdir(modeldir):
    os.system('mkdir ' + modeldir)

model_code = 'stan_JK13.stan'
model_file = os.path.join(modeldir,'stan_JK13.pic') #modeldir comes from init_stan.py


#Define data as draws from some mvGaussian
mu_gen = np.array([0,0]) #+ np.array([10,10])
ndim = len(mu_gen)
cov_gen = np.identity(ndim) 
nx = [4,1]
nx_total = sum(nx)
x1 = np.random.multivariate_normal(mu_gen+np.array([0,0]), cov_gen*1, nx[0])
x2 = np.random.multivariate_normal(mu_gen+np.array([5,5]), cov_gen*4,nx[1])


#x = np.concatenate((np.expand_dims(x1,2),np.expand_dims(x2,2),np.expand_dims(x3,2)),2)
#x = np.transpose(x,(0,2,1))

#Combine into a list of vectors and segment it in Stan (see pg 231 of Stan Manual)
x = np.concatenate((x1,x2),0)

nu = 2.0
nk = len(nx)
dat = {
    'nu': nu,
    'nx': nx,
    'nxs': nx_total,
    'nk': nk,
    'ndim': ndim,
    'sigma_0': np.identity(ndim),
    'mu_0': np.array([0,0]),
    'x': x
    }

#Check if model exists
if os.path.exists(model_file) and not force_recompile:
    #If so, load model to avoid recompiling
    print('Model file {} found, not re-compiling.'.format(model_file))
    model = ist.load(model_file)
else:    
    #Compile and Save model
    model = pystan.StanModel(file=model_code)
    ist.save(model,model_file)

fit = model.sampling(data=dat,iter=1000, chains=1)
print fit

#Find MAP
op = model.optimizing(data=dat)
