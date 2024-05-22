import pprint
from typing import Optional
import numpy as np
from numpy.typing import NDArray


def model(x):
    return x[0] + x[1]


def system_analysis(x: NDArray):
    """`x` is within the failure domain if the return is greater than zero."""
    print(f"system_analysis: A x")
    pprint.pp(x)

    x = x[:]  # convert to numpy array

    print(f"system_analysis: B x")
    pprint.pp(x)

    # print(f"system_analysis: A g")
    # pprint.pp(g)

    g_i = model(x) - 9

    print(f"system_analysis: g_i")
    pprint.pp(g_i)

    # if g is None:
    #     g_new = g_i
    # else:
    #     g_new = np.concatenate([g, g_i])

    # print(f"system_analysis: g_new")
    # pprint.pp(g_i)

    return {"g": g_i}
