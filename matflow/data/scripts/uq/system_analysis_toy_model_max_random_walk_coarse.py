import pprint
from typing import Optional
import numpy as np
from scipy.stats import norm
from numpy.typing import NDArray


def get_approx_y_star_random_walk(dimension, target_pf, sigma=1):
    z = norm.ppf(1 - target_pf / 2)
    return sigma * (np.sqrt(dimension) * z - 0.5826)


def make_voxel_grouping(dimension: int, block_size: int):
    """Partition `dimension` fine grid points into contiguous blocks of `block_size`
    (the last block may be smaller), representing a coarser mesh voxelisation."""
    if block_size < 1:
        raise ValueError("block_size must be >= 1")
    n_blocks = int(np.ceil(dimension / block_size))
    return np.repeat(np.arange(n_blocks), block_size)[:dimension]


def voxel_block_average(x, group_idx):
    """Coarse-grain `x` (..., dimension) by averaging within each block defined by
    `group_idx`, broadcasting each block's mean back over its fine positions (so fine
    and coarse fields live in the same space)."""
    x = np.asarray(x)
    out = np.empty_like(x, dtype=float)
    for block_idx in range(group_idx.max() + 1):
        mask = group_idx == block_idx
        out[..., mask] = x[..., mask].mean(axis=-1, keepdims=True)
    return out


def model_coarse(x, dimension, block_size):
    group_idx = make_voxel_grouping(dimension, block_size)
    x_coarse = voxel_block_average(x, group_idx)
    return np.max(x_coarse, axis=-1)


def system_analysis_toy_model_max_random_walk_coarse(
    x: NDArray, dimension: int, target_pf: float, block_size: int
):
    """`x` is within the failure domain if the return is greater than zero."""
    x = x[:]  # convert to numpy array
    x = np.cumsum(x, axis=-1)
    y_star = get_approx_y_star_random_walk(dimension, target_pf)
    g_i = model_coarse(x, dimension, block_size) - y_star
    return {"g": g_i}
