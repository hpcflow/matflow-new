import numpy as np

from scipy.spatial import KDTree

from matflow.param_classes.voxel_map import VoxelMap


def get_coordinate_grid(size, grid_size):
    """Get the coordinates of the element centres of a uniform grid."""

    grid_size = np.array(grid_size)
    size = np.array(size)

    grid = np.meshgrid(*[np.arange(i) for i in grid_size])
    grid = np.moveaxis(np.array(grid), 0, -1)  # shape (*grid_size, dimension)

    element_size = (size / grid_size).reshape(1, 1, -1)

    coords = grid * size.reshape(1, 1, -1) / grid_size.reshape(1, 1, -1)
    coords += element_size / 2

    return coords, element_size


class DiscreteVoronoi(VoxelMap):
    def __init__(
        self,
        region_seeds,
        grid_size,
        size=None,
        is_periodic=True,
        random_seed=None,
        region_data=None,
    ):
        """
        Parameters
        ----------
        region_seeds : list or ndarray of shape (N, 2) or (N, 3)
            Row vectors of seed positions in 2D or 3D. Must be coordinates within real-space
            `size`.
        grid_size : list or ndarray of length 2 or 3
        size : list or ndarray of length 2 or 3, optional
            If not specified, a unit square/box is used.
        is_periodic : bool, optional
            Should the seeds and box be considered periodic. By default, True.

        """

        region_seeds = np.asarray(region_seeds)
        grid_size = np.asarray(grid_size)
        dimension = grid_size.size

        if size is None:
            size = [1] * dimension
        size = np.asarray(size)

        if size.size != grid_size.size:
            raise ValueError(
                f"`size` ({size}) implies {size.size} dimensions, but `grid_size` "
                f"({grid_size}) implies {grid_size.size} dimensions."
            )

        if region_seeds.shape[1] != grid_size.size:
            raise ValueError(
                f"Specified `region_seeds` should be of shape (num_phases, "
                f"{grid_size.size}), but `region_seeds` has shape: {region_seeds.shape}"
            )

        bad_seeds = np.logical_or(region_seeds < 0, region_seeds > size)
        if np.any(bad_seeds):
            raise ValueError(
                f"`region_seeds` must be coordinates within `size` ({size})."
            )

        self.seeds = region_seeds
        self.seeds_grid = (grid_size * region_seeds / size).astype(int)
        self.random_seed = random_seed

        region_ID = self._get_region_ID(size, grid_size, is_periodic, dimension)

        super().__init__(
            region_ID=region_ID,
            size=size,
            is_periodic=is_periodic,
            region_data=region_data,
        )

    @classmethod
    def from_random(
        cls,
        size,
        grid_size,
        num_regions,
        random_seed=None,
        is_periodic=True,
    ):
        region_seeds = cls.get_unique_random_seeds(
            num_regions=num_regions,
            size=size,
            grid_size=grid_size,
            random_seed=random_seed,
        )
        return cls(
            size=size,
            grid_size=grid_size,
            region_seeds=region_seeds,
            random_seed=random_seed,
            is_periodic=is_periodic,
        )

    @classmethod
    def from_seeds(
        cls,
        size,
        grid_size,
        region_seeds=None,
        random_seed=None,
        is_periodic=True,
    ):
        return cls(
            size=size,
            grid_size=grid_size,
            region_seeds=region_seeds,
            random_seed=random_seed,
            is_periodic=is_periodic,
        )

    @classmethod
    def get_unique_random_seeds(cls, num_regions, size, grid_size, random_seed=None):
        """Get random seeds that occupy unique elements on the voxel grid."""
        max_search_iter = 10_000
        idx = 0
        while idx == 0 or np.any(counts > 1):
            random_seed = random_seed + idx if random_seed else None
            seeds = cls.get_random_seeds(num_regions, size, random_seed)
            seeds_grid = (grid_size * seeds / size).astype(int)
            _, counts = np.unique(seeds_grid, return_counts=True, axis=0)
            if idx > max_search_iter:
                raise RuntimeError(
                    f"Could not find unique random seeds positions (when placed on the "
                    f"grid) in {max_search_iter} iterations. Consider reducing the "
                    f"number of regions (currently {num_regions}), or increasing the "
                    f"`grid_size` (currently {grid_size})."
                )
            elif idx % 1000 == 0 and idx > 0:
                num_multi_counts = np.sum(counts > 1)
                print(
                    f"Searching for random unique seeds (attempt "
                    f"{idx}/{max_search_iter} had {num_multi_counts} repeated seeds)..."
                )
            idx += 1

        if idx > 10:
            print(f"Found random unique seeds in {idx} attempts.")

        return seeds

    @staticmethod
    def get_random_seeds(num_regions, size, random_seed=None):
        size = np.asarray(size)
        rng = np.random.default_rng(seed=random_seed)
        seeds = rng.random((num_regions, size.size)) * size
        return seeds

    def _get_region_ID(self, size, grid_size, is_periodic, dimension):
        """Assign voxels to their closest seed point.

        Returns
        -------
        region_ID
            The index of the closest seed for each voxel.

        """
        print("Tessellating regions...", end="")

        # Get coordinates of grid element centres:
        coords, _ = get_coordinate_grid(size, grid_size)
        coords_flat = coords.reshape(-1, dimension)
        tree = KDTree(self.seeds, boxsize=size if is_periodic else None)
        region_ID = tree.query(coords_flat)[1].reshape(coords.shape[:-1])

        print("done!")

        return region_ID

    @property
    def num_seeds(self):
        return self.seeds_grid.shape[0]

    @property
    def seeds_periodic_mapping(self):
        "Map periodic seed indices back to base seed indices."
        return np.tile(np.arange(self.seeds_grid.shape[0]), 3**self.dimension)

    @property
    def seeds_periodic(self):
        """Get seeds positions including neighbouring periodic images."""
        trans_facts_2D = np.array(
            [
                [0, 0],
                [1, 0],
                [-1, 0],
                [0, 1],
                [0, -1],
                [1, 1],
                [-1, 1],
                [-1, -1],
                [1, -1],
            ]
        )
        if self.dimension == 2:
            trans = self.size * trans_facts_2D
        else:
            trans = self.size * np.vstack(
                [
                    np.hstack([trans_facts_2D, -np.ones((trans_facts_2D.shape[0], 1))]),
                    np.hstack([trans_facts_2D, np.zeros((trans_facts_2D.shape[0], 1))]),
                    np.hstack([trans_facts_2D, np.ones((trans_facts_2D.shape[0], 1))]),
                ]
            )

        seeds_periodic = np.concatenate(trans[:, None] + self.seeds_grid)
        return seeds_periodic
