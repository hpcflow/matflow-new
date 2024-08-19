import numpy as np


def collate_results(g, x, p_0, all_g, all_x):

    # all iterations of g are passed just to get the level index:
    # TODO: in future set and read loop_idx from environment variable?
    level_idx = sorted(g.items(), key=lambda x: x[0])[-1][1]["loop_idx"]["levels"]

    g = g["iteration_0"]["value"]
    num_samples = len(g)

    if all_g:
        # from multiple Markov chains:
        g = np.concatenate([i[:] for i in all_g])
        x = np.vstack([i[:] for i in all_x])
    else:
        # from initial direct Monte Carlo samples:
        g = np.array(g)
        x = np.vstack([i[:] for i in x])

    num_failed = int(np.sum(g > 0))
    num_chains = int(len(g) * p_0)

    # sort responses
    srt_idx = np.argsort(g)[::-1]  # sort by closest-to-failure first
    g = g[srt_idx]
    x = x[srt_idx, :]

    threshold = (g[num_chains - 1] + g[num_chains]) / 2

    # failure probability at this level:
    fail_bool = g > 0
    level_pf = np.mean(fail_bool) if threshold > 0 else p_0

    chain_seeds = x[:num_chains]
    chain_g = g[:num_chains]

    is_finished = (num_failed / num_samples) >= p_0

    pf = p_0**level_idx * num_failed / num_samples

    return {
        "chain_seeds": chain_seeds,
        "chain_g": chain_g,
        "threshold": threshold,
        "num_chains": num_chains,
        "num_failed": num_failed,
        "level_pf": level_pf,
        "pf": pf,
        "is_finished": is_finished,
    }
