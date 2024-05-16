import numpy as np


def collate_results(g, MC_state, p_0):

    print(f"collate_results: p_0 = {p_0}")
    print(f"collate_results: g = {g}")
    print(f"collate_results: MC_state = {MC_state}")

    # retrieve zeroth iteration for now: # TODO: fix for subsequent iterations
    g = g["iteration_0"]["value"]  # list of 1D zarr arrays
    MC_state = MC_state["iteration_0"]["value"]

    num_chains = int(len(g) * p_0)
    print(f"collate_results: num_chains = {num_chains!r}")

    g = np.concatenate([i[:] for i in g])
    MC_state = np.vstack([i[:] for i in MC_state])

    print(f"collate_results: g = {g!r}")
    print(f"collate_results: MC_state = {MC_state!r}")

    # sort responses
    srt_idx = np.argsort(g)[::-1]  # sort by closest-to-failure first
    g = g[srt_idx]
    MC_state = MC_state[srt_idx, :]

    threshold = (g[num_chains - 1] + g[num_chains]) / 2

    seeds = MC_state[:num_chains]
    evals = g[:num_chains]

    return {
        "seeds": seeds,
        "evals": evals,
        "threshold": threshold,
        "num_chains": num_chains,
        "num_failed": int(np.sum(g > 0)),
    }
