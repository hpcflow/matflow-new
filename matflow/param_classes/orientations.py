from dataclasses import dataclass
import enum
from typing import Optional

import numpy as np
import zarr

from hpcflow.sdk.core.parameters import ParameterValue


class OrientationRepresentation(enum.Enum):

    QUATERNION = 0
    EULER = 1


class LatticeDirection(enum.Enum):
    # real-space directions:
    a = 0
    b = 1
    c = 2

    # reciprocal-space directions
    a_star = 3
    b_star = 4
    c_star = 5


@dataclass
class UnitCellAlignment(ParameterValue):

    _typ = "unit_cell_alignment"

    x: Optional[LatticeDirection] = None
    y: Optional[LatticeDirection] = None
    z: Optional[LatticeDirection] = None

    def __post_init__(self):
        # assume enum values:
        if not isinstance(self.x, LatticeDirection):
            self.x = LatticeDirection(int(self.x))
        if not isinstance(self.y, LatticeDirection):
            self.y = LatticeDirection(int(self.y))
        if not isinstance(self.z, LatticeDirection):
            self.z = LatticeDirection(int(self.z))

    @classmethod
    def from_hex_convention_DAMASK(cls):
        # TODO: check!
        return cls(x=LatticeDirection.a, y=LatticeDirection.b_star, z=LatticeDirection.c)

    @classmethod
    def from_hex_convention_MTEX(cls):
        """Generate a unit cell alignment from MTEX's default convention for hexagonal
        symmetry.

        Tested using this command in MTEX: `crystalSymmetry("hexagonal").alignment`

        """
        return cls(
            x=LatticeDirection.a_star,
            y=LatticeDirection.b,
            z=LatticeDirection.c_star,
        )


@dataclass
class Orientations(ParameterValue):

    _typ = "orientations"

    data: np.ndarray
    unit_cell_alignment: UnitCellAlignment
    representation: Optional[OrientationRepresentation] = None

    def __post_init__(self):
        if not isinstance(self.representation, OrientationRepresentation):
            # assume we have stored to value of the enum:
            self.representation = OrientationRepresentation(int(self.representation))

        if not isinstance(self.unit_cell_alignment, UnitCellAlignment):
            self.unit_cell_alignment = UnitCellAlignment(**self.unit_cell_alignment)

    @classmethod
    def save_from_HDF5_group(cls, group, param_id: int, workflow):
        """Save orientation data from an HDF5 group to a persistent workflow.

        We avoid loading the data into memory all at once by firstly generating an
        `Orientations` object with a small data array, and then copying from the HDF5
        group directly into the newly created Zarr group.

        """

        obj = cls(
            data=np.array([0]),
            representation=group.attrs.get("representation"),
            unit_cell_alignment=dict(
                zip(("x", "y", "z"), group.attrs.get("unit_cell_alignment"))
            ),
        )
        workflow.set_parameter_value(param_id=param_id, value=obj, commit=True)

        # now replace placeholder data with correct data:
        zarr_grp, dataset_name = workflow._store._get_array_group_and_dataset(
            mode="r+",
            param_id=param_id,
            data_path=["data"],
        )
        zarr.copy(
            source=group["data"],
            dest=zarr_grp,
            name=dataset_name,
            if_exists="replace",
        )

    def dump_to_HDF5_group(self, HDF5_group):
        pass

    @classmethod
    def from_JSON_like(cls, data, ori_format):
        """For custom initialisation via YAML or JSON."""
        return cls(data=np.asarray(data), ori_format=ori_format)

    # def to_json_like(self, dct=None, shared_data=None, exclude=None, _depth=0):
    #     return

    @classmethod
    def from_random(cls, number):
        return cls(
            data=cls.quat_sample_random(number),
            unit_cell_alignment=UnitCellAlignment.from_hex_convention_DAMASK(),
            representation=OrientationRepresentation.QUATERNION,
        )

    @staticmethod
    def quat_sample_random(number):
        """Generate random uniformly distributed unit quaternions.

        Parameters
        ----------
        number : int
            How many quaternions to generate.

        Returns
        -------
        quats : ndarray of shape (number, 4)

        References
        ----------
        https://stackoverflow.com/a/44031492/5042280
        http://planning.cs.uiuc.edu/node198.html
        """

        rand_nums = np.random.random((number, 3))
        quats = np.array(
            [
                np.sqrt(1 - rand_nums[:, 0]) * np.sin(2 * np.pi * rand_nums[:, 1]),
                np.sqrt(1 - rand_nums[:, 0]) * np.cos(2 * np.pi * rand_nums[:, 1]),
                np.sqrt(rand_nums[:, 0]) * np.sin(2 * np.pi * rand_nums[:, 2]),
                np.sqrt(rand_nums[:, 0]) * np.cos(2 * np.pi * rand_nums[:, 2]),
            ]
        ).T

        return quats
