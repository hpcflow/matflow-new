from typing import List
import numpy as np


def masked_array_from_list(arr, fill_value="x"):
    """Generate a (masked) array from a 1D or 2D list whose elements may contain a fill
    value."""

    is_2D = False
    if isinstance(arr[0], list):
        is_2D = True
        n_rows = len(arr)
        arr = [item for row in arr for item in row]

    data = np.empty(len(arr))
    mask = np.zeros(len(arr))
    has_mask = False
    for idx, i in enumerate(arr):
        if i == fill_value:
            mask[idx] = True
            has_mask = True
        else:
            data[idx] = i
    if has_mask:
        out = np.ma.masked_array(data, mask=mask)
    else:
        out = data
    if is_2D:
        out = out.reshape(n_rows, -1, order="C")
    return out
