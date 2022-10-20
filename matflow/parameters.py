from dataclasses import dataclass
import enum
import logging
from typing import Optional

import numpy as np

from hpcflow.sdk.core.zarr_io import ZarrEncodable

logger = logging.getLogger(__name__)


@dataclass
class SubParameter:
    pass


@dataclass
class OrientationFormat(enum.Enum):

    # i.e. InputValue(parameter=Parameter(typ='orientations'), path=('ori_format',), value=...)

    QUATERNION = 1
    EULER = 2


@dataclass
class Orientations(ZarrEncodable):

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
