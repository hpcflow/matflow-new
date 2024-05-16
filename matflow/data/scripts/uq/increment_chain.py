import pprint

import numpy as np


def increment_chain(MC_state, g, threshold, chain_index):

    print(f"increment_chain: threshold: {threshold!r}")
    print(f"increment_chain: chain_index: {chain_index!r}")

    print(f"increment_chain: MC_state")
    pprint.pp(MC_state)

    print(f"increment_chain: g")
    pprint.pp(g)

    avail_levels = set()
    avail_chain_states = set()
    for i in g.values():
        avail_chain_states.add(i["loop_idx"]["markov_chain_state"])
        avail_levels.add(i["loop_idx"]["levels"])

    max_chain_state_loop_iter = max(avail_chain_states)
    max_level_loop_iter = max(avail_levels)

    all_MC_state = [
        i["value"]
        for i in MC_state.values()
        if i["loop_idx"]
        == {
            "markov_chain_state": max_chain_state_loop_iter,
            "levels": max_level_loop_iter,
        }
    ][0][:]
    trial_MC_state = all_MC_state[-1]

    all_g = [
        i["value"]
        for i in g.values()
        if i["loop_idx"]
        == {
            "markov_chain_state": max_chain_state_loop_iter,
            "levels": max_level_loop_iter,
        }
    ][0][:]
    trial_g = all_g[-1]

    print(f"{all_MC_state=}")
    print(f"{all_g=}")

    print(f"{trial_MC_state=}")
    print(f"{trial_g=}")

    prev_MC_state = all_MC_state[-2]
    prev_g = all_g[-2]

    print(f"{prev_MC_state=}")
    print(f"{prev_g=}")

    new_MC_state = trial_MC_state if trial_g > threshold else prev_MC_state
    new_g = trial_g if trial_g > threshold else prev_g

    print(f"{new_MC_state=}")
    print(f"{new_g=}")

    all_MC_state[-1] = new_MC_state
    all_g[-1] = new_g

    print(f"out MC_state: {all_MC_state=}")
    print(f"out g: {all_g=}")

    return {"MC_state": all_MC_state, "g": all_g}
