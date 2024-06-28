import pprint

import numpy as np


def increment_chain(x, g, all_x, all_g, threshold):

    #print(f"increment_chain: threshold: {threshold!r}")

    #print(f"increment_chain: x")
    #pprint.pp(x)

    #print(f"increment_chain: all_x")
    #pprint.pp(all_x)

    #print(f"increment_chain: g")
    #pprint.pp(g)

    #print(f"increment_chain: all_g")
    #pprint.pp(all_g)

    trial_x = x[:]  # convert to numpy array
    trial_g = g

    current_x = all_x[-1]
    current_g = all_g[-1]

    #print(f"increment_chain: {trial_x=}")
    #print(f"increment_chain: {trial_g=}")

    #print(f"increment_chain: {current_x=}")
    #print(f"increment_chain: {current_g=}")

    new_x = trial_x if trial_g > threshold else current_x
    new_g = trial_g if trial_g > threshold else current_g

    all_x = np.vstack([all_x, new_x[None]])
    all_g = np.append(all_g, np.array(new_g))

    #print(f"increment_chain: {all_x=}")
    #print(f"increment_chain: {all_g=}")

    return {"x": new_x, "g": new_g, "all_x": all_x, "all_g": all_g}
