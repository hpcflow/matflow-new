import numpy as np
import pyvista as pv


def get_array_edge_mask(arr):
    """Get a boolean mask array that is True at the edge elements of an array."""
    all_idx = np.indices(arr.shape)
    mask = np.zeros_like(arr)
    for dim_idx, dim_size in enumerate(arr.shape):
        dim_mask = np.logical_or(all_idx[dim_idx] == 0, all_idx[dim_idx] == dim_size - 1)
        mask = np.logical_or(mask, dim_mask)
    return mask


class VoxelMap:
    def __init__(self, region_ID, size, is_periodic, region_data=None, quiet=False):
        """
        Parameters
        ---------
        region_ID : 2D or 3D array of integer IDs

        """

        self.region_ID = np.asarray(region_ID).astype(int)
        self.size = np.asarray(size)
        self.is_periodic = is_periodic

        self.neighbour_voxels = self.get_neighbour_voxels(quiet)
        self.neighbour_list = self.get_neighbour_list(quiet)
        self.num_regions = self.get_num_regions()

        self.region_data = region_data or {}

        for k, v in self.region_data.items():
            v = np.asarray(v)
            if v.shape[0] != self.num_regions:
                raise ValueError(
                    f"Region data must be the same length as the number of regions "
                    f"({self.num_regions}), but specified lenght for {k!r} was "
                    f"{v.shape[0]}."
                )
            self.region_data[k] = v

        self._coordinates = None  # assigned by `get_coordinates`

    @property
    def region_ID_flat(self):
        return self.region_ID.reshape(-1)

    @property
    def dimension(self):
        return self.region_ID.ndim

    @property
    def grid_size(self):
        return np.array(self.region_ID.shape)

    @property
    def shape(self):
        return tuple(self.grid_size)

    @property
    def spacing(self):
        return self.size / self.grid_size

    @property
    def spacing_3D(self):
        return self.size_3D / self.grid_size_3D

    @property
    def num_voxels(self):
        return np.product(self.grid_size)

    @property
    def coordinates(self):
        if self._coordinates is None:
            self._coordinates = self._get_coordinates()
        return self._coordinates

    def _get_coordinates(self):
        mg_args = [np.arange(i) * j / i for i, j in zip(self.grid_size, self.size)]
        coords = np.concatenate([i[..., None] for i in np.meshgrid(*mg_args)], axis=-1)
        return coords

    def generate_voxel_mask(self):
        voxel_mask = np.zeros(self.shape, dtype=int)
        return voxel_mask.astype(bool)

    def get_num_regions(self):
        return np.unique(self.region_ID).size

    def get_neighbour_region(self, dimension: int, direction: int):
        """
        Parameters
        ----------
        dimension :
            Which dimension to consider (0, 1, or 2 [if 3D])
        direction :
            Which direction to consider (-1, +1)

        """

        region = np.roll(self.region_ID, shift=direction, axis=dimension)

        if not self.is_periodic:
            idx = 0 if direction == 1 else -1
            if dimension == 0:
                region[idx] = self.region_ID[idx]
            elif dimension == 1:
                region[:, idx] = self.region_ID[:, idx]
            elif dimension == 2:
                region[:, :, idx] = self.region_ID[:, :, idx]

        return region

    @property
    def region_ID_above(self):
        return self.get_neighbour_region(self.dimension - 2, 1)

    @property
    def region_ID_below(self):
        return self.get_neighbour_region(self.dimension - 2, -1)

    @property
    def region_ID_left(self):
        return self.get_neighbour_region(self.dimension - 1, 1)

    @property
    def region_ID_right(self):
        return self.get_neighbour_region(self.dimension - 1, -1)

    @property
    def region_ID_in(self):
        if self.dimension != 3:
            raise AttributeError("No `region_ID_in` for 2D geometry.")
        else:
            return self.get_neighbour_region(0, 1)

    @property
    def region_ID_out(self):
        if self.dimension != 3:
            raise AttributeError("No `region_ID_out` for 2D geometry.")
        else:
            return self.get_neighbour_region(0, -1)

    @property
    def region_ID_diff_above(self):
        return self.region_ID - self.region_ID_above != 0

    @property
    def region_ID_diff_below(self):
        return self.region_ID - self.region_ID_below != 0

    @property
    def region_ID_diff_left(self):
        return self.region_ID - self.region_ID_left != 0

    @property
    def region_ID_diff_right(self):
        return self.region_ID - self.region_ID_right != 0

    @property
    def region_ID_diff_in(self):
        return self.region_ID - self.region_ID_in != 0

    @property
    def region_ID_diff_out(self):
        return self.region_ID - self.region_ID_out != 0

    @property
    def region_ID_diff_horz(self):
        return np.logical_or(self.region_ID_diff_left, self.region_ID_diff_right)

    @property
    def region_ID_diff_vert(self):
        return np.logical_or(self.region_ID_diff_above, self.region_ID_diff_below)

    @property
    def region_ID_diff_depth(self):
        return np.logical_or(self.region_ID_diff_in, self.region_ID_diff_out)

    @property
    def region_ID_bulk(self):
        out = np.logical_and(
            np.logical_not(self.region_ID_diff_horz),
            np.logical_not(self.region_ID_diff_vert),
        )
        if self.dimension == 3:
            out = np.logical_and(out, np.logical_not(self.region_ID_diff_depth))

        return out

    def get_region_boundary_voxels(self, r1: int, r2: int):
        r1_vox = (self.region_ID == r1).astype(int)
        r2_vox = (self.region_ID == r2).astype(int)
        overlap = np.concatenate(
            [
                (r1_vox + np.roll(r2_vox, shift=1, axis=0) == 2)[None],
                (r2_vox + np.roll(r1_vox, shift=1, axis=0) == 2)[None],
                (r1_vox + np.roll(r2_vox, shift=-1, axis=0) == 2)[None],
                (r2_vox + np.roll(r1_vox, shift=-1, axis=0) == 2)[None],
                (r1_vox + np.roll(r2_vox, shift=1, axis=1) == 2)[None],
                (r2_vox + np.roll(r1_vox, shift=1, axis=1) == 2)[None],
                (r1_vox + np.roll(r2_vox, shift=-1, axis=1) == 2)[None],
                (r2_vox + np.roll(r1_vox, shift=-1, axis=1) == 2)[None],
            ]
        )
        if self.dimension == 3:
            overlap = np.concatenate(
                [
                    overlap,
                    (r1_vox + np.roll(r2_vox, shift=1, axis=2) == 2)[None],
                    (r2_vox + np.roll(r1_vox, shift=1, axis=2) == 2)[None],
                    (r1_vox + np.roll(r2_vox, shift=-1, axis=2) == 2)[None],
                    (r2_vox + np.roll(r1_vox, shift=-1, axis=2) == 2)[None],
                ]
            )

        boundary_vox = np.sum(overlap, axis=0) > 0
        return boundary_vox

    def get_neighbour_voxels(self, quiet=False):
        if not quiet:
            print("Finding neighbouring voxels...", end="")
        interface_voxels = np.copy(self.region_ID)
        interface_voxels[self.region_ID_bulk] = -1
        if not quiet:
            print("done!")
        return interface_voxels

    def get_interface_voxels(self):
        interface_voxels = np.copy(self.region_ID)
        interface_voxels[self.region_ID_bulk] = -1
        interface_voxels[interface_voxels != -1] = 0
        return interface_voxels

    def get_neighbour_list(self, quiet=False):
        """Get the pairs of regions that are neighbours"""
        if not quiet:
            print("Finding neighbour list...", end="")
        region_boundary_above = np.array(
            [self.region_ID_flat, self.region_ID_above.reshape(-1)]
        )
        region_boundary_left = np.array(
            [self.region_ID_flat, self.region_ID_left.reshape(-1)]
        )
        region_boundary_below = np.array(
            [self.region_ID_flat, self.region_ID_below.reshape(-1)]
        )
        region_boundary_right = np.array(
            [self.region_ID_flat, self.region_ID_right.reshape(-1)]
        )

        region_boundary_all = np.concatenate(
            (
                region_boundary_above[:, self.region_ID_diff_above.reshape(-1)],
                region_boundary_below[:, self.region_ID_diff_below.reshape(-1)],
                region_boundary_left[:, self.region_ID_diff_left.reshape(-1)],
                region_boundary_right[:, self.region_ID_diff_right.reshape(-1)],
            ),
            axis=1,
        )

        if self.dimension == 3:
            region_boundary_in = np.array(
                [self.region_ID_flat, self.region_ID_in.reshape(-1)]
            )
            region_boundary_out = np.array(
                [self.region_ID_flat, self.region_ID_out.reshape(-1)]
            )
            region_boundary_all = np.concatenate(
                (
                    region_boundary_all,
                    region_boundary_in[:, self.region_ID_diff_in.reshape(-1)],
                    region_boundary_out[:, self.region_ID_diff_out.reshape(-1)],
                ),
                axis=1,
            )

        neighbours = np.unique(region_boundary_all, axis=1)
        if not quiet:
            print("done!")

        return neighbours

    def get_interface_idx(self, interface_map, as_3D=False):
        interface_idx_above_flat = interface_map[
            self.region_ID_flat, self.region_ID_above.reshape(-1)
        ]
        interface_idx_below_flat = interface_map[
            self.region_ID_flat, self.region_ID_below.reshape(-1)
        ]
        interface_idx_left_flat = interface_map[
            self.region_ID_flat, self.region_ID_left.reshape(-1)
        ]
        interface_idx_right_flat = interface_map[
            self.region_ID_flat, self.region_ID_right.reshape(-1)
        ]

        interface_idx_above = interface_idx_above_flat.reshape(self.shape)
        interface_idx_below = interface_idx_below_flat.reshape(self.shape)
        interface_idx_left = interface_idx_left_flat.reshape(self.shape)
        interface_idx_right = interface_idx_right_flat.reshape(self.shape)

        interface_idx_all = np.concatenate(
            (
                interface_idx_above[None],
                interface_idx_below[None],
                interface_idx_left[None],
                interface_idx_right[None],
            ),
            axis=0,
        )

        if self.dimension == 3:
            interface_idx_in_flat = interface_map[
                self.region_ID_flat,
                self.region_ID_in.reshape(-1),
            ]
            interface_idx_out_flat = interface_map[
                self.region_ID_flat,
                self.region_ID_out.reshape(-1),
            ]
            interface_idx_in = interface_idx_in_flat.reshape(self.shape)
            interface_idx_out = interface_idx_out_flat.reshape(self.shape)

            interface_idx_all = np.concatenate(
                (
                    interface_idx_all,
                    interface_idx_in[None],
                    interface_idx_out[None],
                ),
                axis=0,
            )

        # avoid self-phase neighbour idx of -1:
        interface_idx_all = np.sort(interface_idx_all, axis=0)[-1]
        interface_idx_all[self.region_ID_bulk] = -1

        if not self.is_periodic:
            interface_idx_all[get_array_edge_mask(interface_idx_all)] = -1

        if self.dimension == 2 and as_3D:
            return interface_idx_all.T[:, :, None]
        else:
            return interface_idx_all

    @property
    def grid_size_3D(self):
        if self.dimension == 2:
            return np.hstack([self.grid_size[::-1], 1])
        else:
            return np.asarray(self.grid_size)

    @property
    def size_3D(self):
        if self.dimension == 2:
            return np.hstack([self.size[::-1], self.size[0] / self.grid_size[0]])
        else:
            return np.asarray(self.size)

    def get_pyvista_grid(self, include_region_ID=False):
        """Experimental!"""

        img = pv.ImageData()

        img.dimensions = self.grid_size_3D + 1  # +1 to inject values on cell data
        img.spacing = self.spacing_3D

        if include_region_ID:
            img.cell_data["data1"] = self.region_ID.flatten(order="F")

        return img

    def show(self):
        """Experimental!"""

        print("WARNING: experimental!")

        grid = self.get_pyvista_grid()

        grid.cell_data["data"] = self.region_ID.flatten(order="F")

        # TODO: fix plotter to show multiple cell data
        pl = pv.Plotter(notebook=True)
        pl.add_mesh(grid)
        pl.show()
