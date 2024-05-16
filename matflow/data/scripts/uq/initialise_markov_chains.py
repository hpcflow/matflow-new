import numpy as np


def initialise_markov_chains(chain_index, seeds, evals):

    print(f"initialise_chains: chain_index = {chain_index!r}")
    print(f"initialise_chains: seeds = {seeds!r}")
    print(f"initialise_chains: evals = {evals!r}")

    seed_i = seeds[chain_index]
    eval_i = evals[chain_index]

    return {"MC_state": seed_i, "g": eval_i}
