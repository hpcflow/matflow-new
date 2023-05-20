from dataclasses import dataclass
import enum
from typing import Optional

import numpy as np
from hpcflow.sdk.core.parameters import ParameterValue


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
