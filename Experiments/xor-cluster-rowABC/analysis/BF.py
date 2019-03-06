import numpy as np
import scipy.integrate as integrate
def BFtt(N,t,r=.707):
    # Calculate Bayes Factor. From Rouder et al. (2009). Outputs BF01 (evidence for the null)
    # N: Sample Size
    # t: t-statistic
    # r: Cauchy prior width
    # Note that while the
    # results seems to match what is shown on Rouder's website (pcl.missouri.edu/bf-one-sample), it doesn't exactly match JASP. Hmm.
    # Possibly JASP uses MCMC so less precise?
    # 090915 - Start coding up, with much trepidation.
    # 010219 - Moved from MATLAB to python
    v = N-1;
    B01numr = (1.+(t**2.)/v)**-((v+1.)/2.);
    
    def B01denmFunc(g):
        out = ((1.+N*g)**(-1./2.)) * ((1. + (t**2.)/((1.+N*g)*v))**-((v+1.)/2.)) * (r*(2.*np.pi)**(-1./2.)) * (g**(-3./2.)) * np.exp(-(r**2.)/(2.*g))
        return out
    
    B01denm = integrate.quad(B01denmFunc,0,np.inf)
    B01 = B01numr/B01denm[0];
    return B01
    
