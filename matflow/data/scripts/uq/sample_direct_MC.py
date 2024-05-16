import numpy as np
from scipy.stats import multivariate_normal


def sample_direct_MC(dimension):
    pi = multivariate_normal(mean=np.zeros(dimension))
    MC_state = np.atleast_1d(pi.rvs())
    return {"MC_state": MC_state}
