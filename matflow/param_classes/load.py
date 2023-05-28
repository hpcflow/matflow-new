from __future__ import annotations

import logging

import numpy as np
from hpcflow.sdk.core.parameters import ParameterValue

logger = logging.getLogger(__name__)


class LoadCase(ParameterValue):

    _typ = "load_case"

    def __init__(
        self,
        direction: str,
        total_time: float,
        num_increments: int,
        def_grad_rate: np.typing.ArrayLike,
        def_grad_aim: np.typing.ArrayLike,
        stress: np.typing.ArrayLike,
        dump_frequency: int,
    ) -> None:
        self.direction = direction
        self.total_time = total_time
        self.num_increments = num_increments
        self.def_grad_rate = def_grad_rate
        self.def_grad_aim = def_grad_aim
        self.direction = direction
        self.stress = stress
        self.dump_frequency = dump_frequency

    @staticmethod
    def helper_method(a):
        pass

    @classmethod
    def uniaxial(
        cls,
        total_time: float,
        num_increments: int,
        direction: str,
        target_strain_rate: float = None,
        target_strain: float = None,
        dump_frequency: int = 1,
    ) -> LoadCase:
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
