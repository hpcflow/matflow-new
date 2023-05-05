from dataclasses import dataclass
import enum
import logging
from typing import Optional

import numpy as np

from hpcflow.sdk.core.parameters import ParameterValue

logger = logging.getLogger(__name__)


class LoadCase(ParameterValue):

    _typ = "load_case"

    def __init__(
        self,
        direction,
        total_time,
        num_increments,
        def_grad_rate,
        def_grad_aim,
        stress,
        dump_frequency,
    ) -> None:
        self.direction = direction
        self.total_time = total_time
        self.num_increments = num_increments
        self.def_grad_rate = def_grad_rate
        self.def_grad_aim = def_grad_aim
        self.direction = direction
        self.stress = stress
        self.dump_frequency = dump_frequency

    @classmethod
    def uniaxial(
        cls,
        total_time,
        num_increments,
        direction,
        target_strain_rate=None,
        target_strain=None,
        dump_frequency=1,
    ):
        # Validation:
        msg = "Specify either `target_strain_rate` or `target_strain`."
        if all([t is None for t in [target_strain_rate, target_strain]]):
            raise ValueError(msg)
        if all([t is not None for t in [target_strain_rate, target_strain]]):
            raise ValueError(msg)

        if target_strain_rate is not None:
            def_grad_val = target_strain_rate
        else:
            def_grad_val = target_strain

        dir_idx = ["x", "y", "z"]
        try:
            loading_dir_idx = dir_idx.index(direction)
        except ValueError:
            msg = (
                f'Loading direction "{direction}" not allowed. It should be one of "x", '
                f'"y" or "z".'
            )
            raise ValueError(msg)

        dg_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.eye(3))
        stress_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.logical_not(np.eye(3)))

        dg_arr[loading_dir_idx, loading_dir_idx] = def_grad_val
        dg_arr.mask[loading_dir_idx, loading_dir_idx] = False
        stress_arr.mask[loading_dir_idx, loading_dir_idx] = True

        def_grad_aim = dg_arr if target_strain is not None else None
        def_grad_rate = dg_arr if target_strain_rate is not None else None

        load_case = {
            "direction": direction,
            "total_time": total_time,
            "num_increments": num_increments,
            "def_grad_rate": def_grad_rate,
            "def_grad_aim": def_grad_aim,
            "stress": stress_arr,
            "dump_frequency": dump_frequency,
        }
        return cls(**load_case)


@dataclass
class SubParameter:
    pass


@dataclass
class OrientationFormat(enum.Enum):

    # i.e. InputValue(parameter=Parameter(typ='orientations'), path=('ori_format',), value=...)

    QUATERNION = 1
    EULER = 2


@dataclass
class Orientations(ParameterValue):

    # i.e. InputValue(parameter=Parameter(typ='orientations'), value=...)
    _typ = "orientations"

    # _sub_parameters = (
    #     SubParameter(path=("ori_format",), is_enum=True, class_obj=OrientationFormat),
    # )

    data: np.ndarray
    ori_format: Optional[OrientationFormat] = None

    def __post_init__(self):
        pass
        # if not isinstance(self.ori_format, OrientationFormat):
        #     self.ori_format = getattr(OrientationFormat, self.ori_format.upper())

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
            ori_format="quaternion",
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
