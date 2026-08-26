import os

import numpy as np


def coarse_weight(g_coarse, threshold, temperature):
    z = (g_coarse - threshold) / temperature
    return 1.0 / (1.0 + np.exp(-z))


def increment_chain_RST(
    endpoint_moved,
    x,
    g,
    gc,
    all_x,
    all_g,
    all_gc,
    all_accept,
    threshold,
    temperature,
    rng,
):
    """
    Increment the outer Markov chain with either the proposal from the end of the coarse
    model sub-chain, or with the current outer state.

    Parameters
    ----------
    x
        New proposed state; the final proposed state of the sub-chain.
    g
        Fine model evaluation of the new proposed state.
    gc
        Coarse model evaluation of the new proposed state.
    all_x
        Markov chain states so far.
    all_g
        Fine model evaluations for each of the Markov chain states so far.

    """

    loop_idx = {
        loop_name: int(loop_idx)
        for loop_name, loop_idx in (
            item.split("=")
            for item in os.environ["MATFLOW_ELEMENT_ITER_LOOP_IDX"].split(";")
        )
    }

    if loop_idx["markov_chain_state"] == 0:
        # initial iteration of the outer Markov chain
        all_gc = np.array([g["coarse_initial"]])

    current_gc = all_gc[-1]
    current_x = all_x[-1]
    current_g = all_g[-1]
    fine_accept = False

    if not endpoint_moved:
        new_x = current_x
        new_g = current_g
        new_gc = current_gc

    else:
        g_fine = g["fine"]
        g = g_fine

        fine_subset_pass = g > threshold

        if not fine_subset_pass:

            # fine target is zero here
            new_x = current_x
            new_g = current_g
            new_gc = current_gc

        else:

            # ------------------------------------------------
            # Final RST correction
            #
            # alpha_F =
            # min(1, pi_C(current_x) / pi_C(psi))
            #
            # The phi terms cancel, leaving:
            #
            # alpha_F =
            # min(1, s(current_x) / s(psi))
            # ------------------------------------------------

            s_current = coarse_weight(current_gc, threshold, temperature)
            s_psi = coarse_weight(gc, threshold, temperature)

            alpha_fine = min(1.0, s_current / s_psi)

            random_num = rng.random()
            fine_accept = random_num < alpha_fine

            if fine_accept:
                new_x = x[:]  # convert to Numpy array
                new_g = g
                new_gc = gc
            else:
                new_x = current_x
                new_g = current_g
                new_gc = current_gc

    all_x = np.vstack([all_x, new_x[None]])
    all_g = np.append(all_g, np.array(new_g))
    all_gc = np.append(all_gc, np.array(new_gc))
    all_accept = np.append(all_accept, np.array(fine_accept))

    return {
        "x": new_x,
        "g": new_g,
        "gc": new_gc,
        "all_x": all_x,
        "all_g": all_g,
        "all_gc": all_gc,
        "all_accept": all_accept,
        "rng": rng,
    }
