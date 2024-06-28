import logging
import pprint

import numpy as np
from numpy.typing import NDArray
from scipy.stats import norm


def set_up_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)
    fh = logging.FileHandler("script.log")
    fh_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s:%(filename)s: %(message)s"
    )
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    return logger


def generate_next_state(x):
    """Generate the next candidate state in a modified Metropolis algorithm.

    Parameters
    ----------
    MC_state
        Current state on which the candidate state will depend.

    Returns
    -------
    dict:
        MC_state:
            Generated candidate state.
    """

    #logger = set_up_logger()

    #print(f"generate_next_state: A x")
    #pprint.pp(x)

    x = x[:]  # convert to numpy array

    #print(f"generate_next_state: B x")
    #pprint.pp(x)

    # TODO: add marginals as parameter

    current_state = x

    #print(f"generate_next_state: current_state")
    #pprint.pp(current_state)

    rng = np.random.default_rng()
    dim = len(current_state)

    marginals = [norm() for _ in range(dim)]

    xi = np.empty(dim)

    for k in range(dim):

        proposal = norm(loc=current_state[k])  # TODO: parametrise spread?

        xi_hat_k = proposal.rvs()
        #logger.debug(
        #    f"MMA: markov chain state: trial component {k}: xi_hat_k = {xi_hat_k}"
        #)

        # acceptance ratio:
        r = marginals[k].pdf(xi_hat_k) / marginals[k].pdf(current_state[k])

        #logger.debug(f"MMA: markov chain state: trial component {k}: r = {r}")

        if rng.random() < min(1, r):
            # accept candidate:
            xi[k] = xi_hat_k
        else:
            # reject candidate, use previous for this component:
            xi[k] = current_state[k]

    x = xi

    # MC_state = np.vstack([MC_state, xi[None]])
    #print(f"generate_next_state: C x")
    #pprint.pp(x)

    return {"x": x}
