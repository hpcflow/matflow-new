import pprint

import numpy as np


def increment_chain(x, g, all_x, all_g, threshold):

    trial_x = x[:]  # convert to numpy array
    trial_g = g

    current_x = all_x[-1]
    current_g = all_g[-1]

    new_x = trial_x if trial_g > threshold else current_x
    new_g = trial_g if trial_g > threshold else current_g

    all_x = np.vstack([all_x, new_x[None]])
    all_g = np.append(all_g, np.array(new_g))

    return {"x": new_x, "g": new_g, "all_x": all_x, "all_g": all_g}
