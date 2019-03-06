import pymc3 as pm
import numpy as np
import sqlite3, os
import scipy.stats as stats
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import theano.tensor as tt
from theano.tensor.nlinalg import det, matrix_inverse
#Gaussian Mixture Model! Now to multivariateness!
#Fetch pooled data
execfile('Imports.py')
import Modules.Funcs as funcs

pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()

con.close()

savedir = './'
gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma
gentypeStrDisp = ['A\'','B','C'] #not alpha, only beta, beta-gamma
gentypeCols = [[.3,0,.5],[0,0,.5],[0,.5,0]]
f, ax= plt.subplots(1,1, figsize=(1.6, 1.6))
for i, row in info.iterrows():
    pid, condition, gentype = int(row.participant), row.condition, row.gentype
    gentypeStr_p = gentypeStr[gentype]

    palphas = alphas[condition]    
    pbetas = df.stimulus[df.participant == pid]
    if gentype==2:
        pdf = df.loc[df.participant==pid]
        betastr = [gentypeStrDisp[1] if pdf_row.category=='Beta' else gentypeStrDisp[2] for ii,pdf_row in pdf.iterrows() ]
        betacol = [gentypeCols[1] if pdf_row.category=='Beta' else gentypeCols[2] for ii,pdf_row in pdf.iterrows() ]
    else:
        betastr = gentypeStrDisp[gentype]
        betacol = gentypeCols[gentype]
    funcs.plotclasses(ax, stimuli, palphas, pbetas, betastr=betastr,betacol = betacol)
    
    fname = os.path.join(savedir,condition + '-' + gentypeStr_p + '-' + str(pid) + '.png')
    ax.text(.9,1.25,str(pid))
    f.savefig(fname, bbox_inches='tight', transparent=False)
    plt.cla()

#Number of groups
k = 3
#Number of iterations for sampler
niter = 1000


#Let's generate some data. Three groups.
rng = np.random.RandomState(2232)
n = 1000
ms = np.array([[-6,2],[0,1],[4,1]])
ps = np.array([0.2, 0.5, 0.3])
variances = [1,.4,1.5]
covariances = [.5,0,-1]
ss = [np.array([[variances[i],covariances[i]],[covariances[i],variances[i]]]) for i in range(k)]
zs = np.array([rng.multinomial(1, ps) for _ in range(n)]).T

#temp
# ss = [np.eye(2) for i in range(k)]

xs = [z[:, np.newaxis] * rng.multivariate_normal(m, s, size=n)
      for z, m, s in zip(zs, ms, ss)]
data = np.sum(np.dstack(xs), axis=2)

#Plot them nicely
# plt.figure(figsize=(5, 5))
fig, ax = plt.subplots(figsize=(8, 6))
plt.scatter(data[:, 0], data[:, 1], c='g', alpha=0.5)
plt.scatter(ms[0, 0], ms[0, 1], c='r', s=100)
plt.scatter(ms[1, 0], ms[1, 1], c='b', s=100)
plt.scatter(ms[2, 0], ms[2, 1], c='y', s=100)

colors = sns.color_palette()
for i in range(k):
    colr = colors[i]
    var, U = np.linalg.eig(ss[i])
    angle = 180. / np.pi * np.arccos(np.abs(U[0, 0])) * np.sign(ss[i][0,1])
    e = Ellipse(ms[i,:], 2 * np.sqrt(5.991 * var[0]),
                2 * np.sqrt(5.991 * var[1]),
                angle=angle)
    e.set_alpha(0.25)
    e.set_facecolor(colr)
    e.set_zorder(10);
    ax.add_artist(e);

from pymc3.math import logsumexp

# Log likelihood of normal distribution
def logp_normal(mu, tau, value):
        #     dist = pm.Normal.dist(mu,tau=tau).logp(value)
        #     return dist
        # log probability of individual samples
    k = tau.shape[0]
    delta = lambda mu: value - mu
    return (-1 / 2.) * (k * tt.log(2 * np.pi) + tt.log(1./det(tau)) + (delta(mu).dot(tau) * delta(mu)).sum(axis=1))

# Log likelihood of Gaussian mixture distribution
def logp_gmix(mus, pi, tau):
    def logp_(value):
        logps = [tt.log(pi[i]) + logp_normal(mu, tau[i], value) for i, mu in enumerate(mus)]
        return tt.sum(logsumexp(tt.stacklists(logps)[:, :n], axis=0))

    return logp_

with pm.Model() as gmm:
    #Prior for categorical
    p = pm.Dirichlet('p', a=np.array([1.]*k), testval=np.ones(k)/k)
    #z is the probability of being assigned a certain cluster
    z = pm.Categorical('z', p=p, shape=n)
    
    #Now set up the prior over the means and standard deviations
    #The mean of each cluster is a sample from a normal
    #  the 'mu' and 'sd' arguments here don't matter too much - they're the hyperparameters for the prior
    # 'shape' argument tells pymc3 how many means we need - here we need k number of means
    #
    #mu = pm.Normal('mu', mu=np.array([0.]*k), sd=np.array([15.]*k), shape=k)
    mus = [pm.MvNormal('mu_%d' % i,
                        mu=pm.floatX(np.zeros(2)),
                        tau=pm.floatX(0.1 * np.eye(2)),
                        shape=(2,))
           for i in range(k)]    
    packed_L = [pm.LKJCholeskyCov('packed_L_%d' % i,n=2,eta=2.,sd_dist=pm.HalfCauchy.dist(2.5)) for i in range(k)]
    L = [pm.expand_packed_triangular(2, packed_L[i]) for i in range(k)]         
    sigma = [pm.Deterministic('sigma_%d' % i ,L[i].dot(L[i].T)) for i in range(k)]
    tau = [pm.Deterministic('tau_%d' % i,matrix_inverse(sigma[i])) for i in range(k)]
    Y_obs = pm.DensityDist('Y_obs', logp_gmix(mus, p, tau), observed=data)
    step1 = pm.ElemwiseCategorical(vars=[z], values=range(k))
    step2 = pm.NUTS(vars=[p, mus[0],mus[1],mus[2],
                      packed_L[0],packed_L[1],packed_L[2]])
    trace = pm.sample(niter, step=[step1, step2],chains=10)

    


                          
    
    
