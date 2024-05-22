import numpy as np
from scipy.stats import multivariate_normal


def sample_direct_MC(dimension):
    pi = multivariate_normal(mean=np.zeros(dimension))
    x = np.atleast_1d(pi.rvs())
    return {"x": x}
