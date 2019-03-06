from warnings import filterwarnings
from matplotlib.patches import Ellipse
from matplotlib import pyplot as plt
import numpy as np
import pymc3 as pm
import seaborn as sns
filterwarnings('ignore', message='findfont')

SEED = 3264602 # from random.org

np.random.seed(SEED)

N = 10000

mu_actual = [np.array([1, -2]),np.array([0,2])]
sigma_actual = [np.array([[0.5, -0.3],
                          [-0.3, 1.]]),
                np.array([[.8,.6],
                          [.6,.6]])]

x = [np.random.multivariate_normal(mu_actual[i], sigma_actual[i], size=N) for i in range(len(mu_actual))]


fig, ax = plt.subplots(figsize=(8, 6))

blue,red = sns.color_palette()
colors = [blue,red]

for i in range(len(sigma_actual)):
    var, U = np.linalg.eig(sigma_actual[i])
    angle = 180. / np.pi * np.arccos(np.abs(U[0, 0]))
    e = Ellipse(mu_actual[i], 2 * np.sqrt(5.991 * var[0]),
                2 * np.sqrt(5.991 * var[1]),
                angle=angle)

    e.set_alpha(0.5)
    e.set_facecolor(colors[i])
    e.set_zorder(10);
    ax.add_artist(e);
    #Plot the data
    ax.scatter(x[i][:, 0], x[i][:, 1], c='k', alpha=0.05, zorder=11);

rect = plt.Rectangle((0, 0), 1, 1, fc=blue, alpha=0.5)
    
ax.legend([rect], ['95% density region'], loc=2);

#Specify model
with pm.Model() as model:
    packed_L = pm.LKJCholeskyCov('packed_L', n=2,
                                 eta=2., sd_dist=pm.HalfCauchy.dist(2.5))

packed_L.tag.test_value.shape

with model:
    L = pm.expand_packed_triangular(2, packed_L)
    sigma = pm.Deterministic('sigma', L.dot(L.T))

L.tag.test_value.shape

with model:
    mu = pm.Normal('mu', 0., 10., shape=2,
                  testval=x.mean(axis=0))
    obs = pm.MvNormal('obs', mu, chol=L, observed=x)

#Finally, sample.
with model:
    trace = pm.sample(random_seed=SEED, cores=12)
