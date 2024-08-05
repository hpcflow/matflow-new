import numpy as np


def collate_results(g, x, p_0, all_g, all_x):

    # print(f"collate_results: g = {g}")
    # all iterations of g are passed just to get the level index:
    # TODO: in future set and read loop_idx from environment variable?
    level_idx = sorted(g.items(), key=lambda x: x[0])[-1][1]["loop_idx"]["levels"]
    # print(f"collate_results: level_idx = {level_idx}")

    g = g["iteration_0"]["value"]
    num_samples = len(g)

    # print(f"collate_results: p_0 = {p_0}")
    # print(f"collate_results: g = {g}")
    # print(f"collate_results: x = {x}")
    # print(f"collate_results: all_g = {all_g}")
    # print(f"collate_results: all_x = {all_x}")

    if all_g:
        # from multiple Markov chains:
        g = np.concatenate([i[:] for i in all_g])
        x = np.vstack([i[:] for i in all_x])
    else:
        # from initial direct Monte Carlo samples:
        g = np.array(g)
        x = np.vstack([i[:] for i in x])

    # print(f"collate_results: B g = {g}")
    # print(f"collate_results: B x = {x}")

    num_failed = int(np.sum(g > 0))
    # print(f"collate_results: num_failed = {num_failed}")

    pf = p_0**level_idx * num_failed / num_samples
    # print(f"collate_results: pf = {pf}")

    num_chains = int(len(g) * p_0)
    # print(f"collate_results: num_chains = {num_chains!r}")

    # sort responses
    srt_idx = np.argsort(g)[::-1]  # sort by closest-to-failure first
    g = g[srt_idx]
    x = x[srt_idx, :]

    threshold = (g[num_chains - 1] + g[num_chains]) / 2

    chain_seeds = x[:num_chains]
    chain_g = g[:num_chains]

    is_finished = (num_failed / num_samples) >= p_0

    return {
        "chain_seeds": chain_seeds,
        "chain_g": chain_g,
        "threshold": threshold,
        "num_chains": num_chains,
        "num_failed": num_failed,
        "pf": pf,
        "is_finished": is_finished,
    }
