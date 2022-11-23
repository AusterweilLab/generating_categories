import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
import pymc3 as pm, theano.tensor as tt
sns.set_context('paper')
sns.set_style('darkgrid')

# simulate data from a known mixture distribution
np.random.seed(12345) # set random seed for reproducibility

k = 3
ndata = 500
spread = 5
centersX = np.array([-spread, 0, spread])
centersY = np.array([-spread+2,1,spread-1.4])
#centers = np.array([[-5,2],[3,5],[1,1]])
# simulate data from mixture distribution
v = np.random.randint(0, k, ndata)
dataX = centersX[v] + np.random.randn(ndata)
dataY = centersY[v] + np.random.randn(ndata)
#data = centers[v] + np.reshape(np.random.randn(ndata*2),(ndata,2))
data = np.concatenate([np.atleast_2d(dataX),np.atleast_2d(dataY)],0)
data = data.transpose()
plt.hist2d(dataX,dataY,bins=20);

# setup model
model = pm.Model()
with model:
    # cluster sizes
    p = pm.Dirichlet('p', a=pm.floatX(0.1 * np.ones(2)),shape = (2,))
    #p = pm.Dirichlet('p', a=np.array([1., 1., 1.]), shape=k)
    # ensure all clusters have some points
    p_min_potential = pm.Potential('p_min_potential', tt.switch(tt.min(p) < .1, -np.inf, 0))
    # cluster centers
    means = [pm.MvNormal('mu_%d'%i,
                         pm.floatX(np.zeros(2)),
                         tau=pm.floatX(.1*np.eye(2)),
                         shape=(2,))
             for i in range(2)]
                         #mu=[0, 0, 0], sd=15, shape=k)
    # break symmetry
    #order_means_potential = pm.Potential('order_means_potential',
    #                        tt.switch(means[1]-means[0] < 0, -np.inf, 0)
    #                        + tt.switch(means[2]-means[1] < 0, -np.inf, 0))
    # measurement error
    sigma = pm.LKJCholeskyCov('packed_L', n=2,
                              eta=2., sd_dist=pm.HalfCauchy.dist(2.5))
    L = pm.expand_packed_triangular(2, sigma)
    #sd = pm.Uniform('sd', lower=0, upper=20)
    # latent cluster of each observation
    category = pm.Categorical('category',
                              p=p,
                              shape=ndata)
    
    # likelihood for each observed value
    points = pm.MvNormal('obs',
                       mu=means[category],
                       chol=L,
                       observed = data)

#fit model
with model:
    step1 = pm.Metropolis()
    step2 = pm.ElemwiseCategorical(vars=[category], values=[0, 1, 2])
    tr = pm.sample(10000, step=[step1, step2])

pm.plots.traceplot(tr, ['p', 'sd', 'means']);
plt.show()
plt.close()
