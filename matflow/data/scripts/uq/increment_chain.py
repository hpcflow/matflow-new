import pprint

import numpy as np


def increment_chain(x, g, all_x, all_g, all_accept, threshold):

    trial_x = x[:]  # convert to numpy array
    trial_g = g

    current_x = all_x[-1]
    current_g = all_g[-1]

    is_accept = trial_g > threshold
    new_x = trial_x if is_accept else current_x
    new_g = trial_g if is_accept else current_g

    all_x = np.vstack([all_x, new_x[None]])
    all_g = np.append(all_g, np.array(new_g))
    all_accept = np.append(all_accept, np.array(is_accept))

    return {
        "x": new_x,
        "g": new_g,
        "all_x": all_x,
        "all_g": all_g,
        "all_accept": all_accept,
    }
