import numpy as np


def initialise_markov_chains(chain_index, chain_seeds, chain_g):

    #print(f"initialise_chains: chain_index = {chain_index!r}")
    #print(f"initialise_chains: chain_seeds = {chain_seeds!r}")
    #print(f"initialise_chains: chain_g = {chain_g!r}")
    x = chain_seeds[chain_index]
    g = chain_g[chain_index]
    #print(f"initialise_chains: x = {x!r}")
    #print(f"initialise_chains: g = {g!r}")
    all_x = np.array(x)[None]
    all_g = np.array([g])
    #print(f"initialise_chains: all_x = {all_x!r}")
    #print(f"initialise_chains: all_g = {all_g!r}")
    return {"x": x, "g": g, "all_x": all_x, "all_g": all_g}
