import pprint
from typing import Optional
import numpy as np
from numpy.typing import NDArray


def model(x):
    return x[0] + x[1]


def system_analysis(MC_state: NDArray, g: Optional[NDArray] = None):
    """`x` is within the failure domain if the return is greater than zero."""
    print(f"system_analysis: A MC_state")
    pprint.pp(MC_state)

    if MC_state.ndim == 1:
        MC_state = MC_state[:][None]
    else:
        MC_state = MC_state[:]

    print(f"system_analysis: B MC_state")
    pprint.pp(MC_state)

    print(f"system_analysis: A g")
    pprint.pp(g)

    g_i = np.array([model(MC_state[-1]) - 9])

    print(f"system_analysis: g_i")
    pprint.pp(g_i)

    if g is None:
        g_new = g_i
    else:
        g_new = np.concatenate([g, g_i])

    print(f"system_analysis: g_new")
    pprint.pp(g_new)

    return {"g": g_new, "MC_state": MC_state}
