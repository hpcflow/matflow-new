import logging
import pprint

import numpy as np
from numpy.typing import NDArray
from scipy.stats import norm


def modified_metropolis_generate_candidate(MC_state: NDArray, g):
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

    print(f"generate_next_state: A MC_state")
    pprint.pp(MC_state)

    print(f"generate_next_state: A g")
    pprint.pp(g)

    if MC_state.ndim == 1:
        MC_state = MC_state[:][None]

    if isinstance(g, float):
        g = np.array([g])
    else:
        g = g[:]

    print(f"generate_next_state: B MC_state")
    pprint.pp(MC_state)

    print(f"generate_next_state: B g")
    pprint.pp(g)

    # TODO: add marginals as parameter

    current_state = MC_state[-1]  # final row

    print(f"generate_next_state: current_state")
    pprint.pp(current_state)

    rng = np.random.default_rng()
    dim = len(current_state)

    marginals = [norm() for _ in range(dim)]

    xi = np.empty(dim)

    for k in range(dim):

        proposal = norm(loc=current_state[k])  # TODO: parametrise spread?

        xi_hat_k = proposal.rvs()
        logging.debug(
            f"MMA: markov chain state: trial component {k}: xi_hat_k = {xi_hat_k}"
        )

        # acceptance ratio:
        r = marginals[k].pdf(xi_hat_k) / marginals[k].pdf(current_state[k])

        logging.debug(f"MMA: markov chain state: trial component {k}: r = {r}")

        if rng.random() < min(1, r):
            # accept candidate:
            xi[k] = xi_hat_k
        else:
            # reject candidate, use previous for this component:
            xi[k] = current_state[k]

    MC_state = np.vstack([MC_state, xi[None]])
    print(f"generate_next_state: C MC_state")
    pprint.pp(MC_state)

    return {"MC_state": MC_state, "g": g}
