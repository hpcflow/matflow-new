from __future__ import annotations
import copy
from dataclasses import dataclass
import enum

import logging
from typing import Dict, List, Optional, Union

import numpy as np
from hpcflow.sdk.core.parameters import ParameterValue
from hpcflow.sdk.core.utils import get_enum_by_name_or_val

import matflow as mf

logger = logging.getLogger(__name__)


class StrainRateMode(enum.Enum):
    def __new__(cls, value, symbol, doc=None):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.symbol = symbol
        obj.__doc__ = doc
        return obj

    DEF_GRAD_RATE = (0, "F_rate", "Deformation gradient rate.")
    VEL_GRAD = (1, "L", "Velocity gradient.")
    VEL_GRAD_APPROX = (2, "L_approx", "Velocity gradient approximation.")


class LoadStep(ParameterValue):
    """Boundary conditions for volume element loading.

    Parameters
    ----------
    direction
        # TODO
    rotation
        # TODO
    total_time : float or int
        Total simulation time.
    num_increments
        Number of simulation increments.
    target_def_grad : numpy.ma.core.MaskedArray of shape (3, 3), optional
        Deformation gradient aim tensor. Masked values correspond to unmasked values in
        `stress`.
    target_def_grad_rate
        Deformation gradient rate tensor. Masked values correspond to unmasked values in
        `stress`.
    stress : numpy.ma.core.MaskedArray of shape (3, 3)
        Stress tensor. Masked values correspond to unmasked values in
        `target_def_grad` or `target_def_grad_rate`.
    dump_frequency : int, optional
        By default, 1, meaning results are written out every increment.
    """

    def __init__(
        self,
        total_time: float,
        num_increments: int,
        direction: Optional[str] = None,
        normal_direction: Optional[str] = None,
        target_def_grad: Optional[np.typing.ArrayLike] = None,
        target_def_grad_rate: Optional[np.typing.ArrayLike] = None,
        target_vel_grad: Optional[np.typing.ArrayLike] = None,
        stress: Optional[np.typing.ArrayLike] = None,
        dump_frequency: Optional[int] = 1,
    ) -> None:

        self.total_time = total_time
        self.num_increments = num_increments
        self.direction = direction
        self.normal_direction = normal_direction
        self.target_def_grad = target_def_grad
        self.target_def_grad_rate = target_def_grad_rate
        self.target_vel_grad = target_vel_grad
        self.stress = stress
        self.dump_frequency = dump_frequency

        # assigned if constructed via a helper class method:
        self._method_name = None
        self._method_args = None

        self._validate()

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, self.__class__):
            return False
        if (
            self.total_time == __value.total_time
            and self.num_increments == __value.num_increments
            and self.direction == __value.direction
            and self.normal_direction == __value.normal_direction
            and self.dump_frequency == __value.dump_frequency
        ):
            # check arrays:
            if self.stress is not None:
                if __value.stress is None or not np.allclose(self.stress, __value.stress):
                    return False
            elif __value.stress is None:
                return False

            if self.target_def_grad is not None:
                if __value.target_def_grad is None or not np.allclose(
                    self.target_def_grad, __value.target_def_grad
                ):
                    return False
            elif __value.target_def_grad is not None:
                return False

            if self.target_def_grad_rate is not None:
                if __value.target_def_grad_rate is None or not np.allclose(
                    self.target_def_grad_rate, __value.target_def_grad_rate
                ):
                    return False
            elif __value.target_def_grad_rate is not None:
                return False

            if self.target_vel_grad is not None:
                if __value.target_vel_grad is None or not np.allclose(
                    self.target_vel_grad, __value.target_vel_grad
                ):
                    return False
            elif __value.target_vel_grad is not None:
                return False

            return True
        return False

    def _validate(self):
        if self.strain_like_tensor is None and self.stress is None:
            raise ValueError(
                "Specify a strain-like tensor (`target_def_grad`, `target_def_grad_rate`,"
                " `target_vel_grad`) and/or the `stress` tensor."
            )
        if self.stress is not None:
            xor_arr = np.logical_xor(self.strain_like_tensor.mask, self.stress.mask)
            if not np.alltrue(xor_arr):
                raise RuntimeError(
                    "Stress and strain tensor masks should be element-wise mutually "
                    "exclusive, but they are not."
                )

    @property
    def strain_like_tensor(self):
        if self.target_def_grad is not None:
            return self.target_def_grad
        elif self.target_def_grad_rate is not None:
            return self.target_def_grad_rate
        elif self.target_vel_grad is not None:
            return self.target_vel_grad

    @property
    def method_name(self):
        return self._method_name

    @property
    def method_args(self):
        return self._method_args

    @property
    def type(self):
        """More user-friendly access to method name."""
        return self._method_name

    def __repr__(self) -> str:
        type_str = f"type={self.type!r}, " if self.type else ""
        if self.direction:
            dir_str = f", direction={self.direction!r}"
        elif self.normal_direction:
            dir_str = f", normal_direction={self.normal_direction!r}"
        else:
            dir_str = ""
        return (
            f"{self.__class__.__name__}({type_str}"
            f"num_increments={self.num_increments}, "
            f"total_time={self.total_time}{dir_str}"
            f")"
        )

    @classmethod
    def example_uniaxial(cls):
        """A non-parametrisable example uniaxial load step."""
        time = 100
        incs = 200
        direction = "x"
        rate = 1e-3
        mf.logger.debug(  # demonstration of logging in a `ParameterValue` class
            f"Generating an example uniaxial load step with parameters: time={time!r}, "
            f"num_increments={incs!r}, direction={direction!r}, "
            f"target_def_grad_rate={rate!r}."
        )
        return cls.uniaxial(
            total_time=time,
            num_increments=incs,
            direction=direction,
            target_def_grad_rate=rate,
        )

    @classmethod
    def uniaxial(
        cls,
        total_time: float,
        num_increments: int,
        direction: str,
        target_def_grad_rate: Optional[float] = None,
        target_def_grad: Optional[float] = None,
        dump_frequency: Optional[int] = 1,
    ) -> LoadStep:
        """
        Generate a uniaxial load step.

        Parameters
        ----------
        total_time : float or int
        num_increments : int
        direction : str
            A single character, "x", "y" or "z", representing the loading direction.
        target_def_grad : float
            Target deformation gradient to achieve along the loading direction component.
        target_def_grad_rate : float
            Target deformation gradient rate to achieve along the loading direction
            component.
        dump_frequency : int, optional
            By default, 1, meaning results are written out every increment.

        """

        _method_name = "uniaxial"
        _method_args = {
            "total_time": total_time,
            "num_increments": num_increments,
            "direction": direction,
            "target_def_grad_rate": target_def_grad_rate,
            "target_def_grad": target_def_grad,
            "dump_frequency": dump_frequency,
        }

        # Validation:
        msg = "Specify either `target_def_grad_rate` or `target_def_grad`."
        if all([t is None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)
        if all([t is not None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)

        if target_def_grad_rate is not None:
            def_grad_val = target_def_grad_rate
        else:
            def_grad_val = target_def_grad

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

        def_grad_aim = dg_arr if target_def_grad is not None else None
        def_grad_rate = dg_arr if target_def_grad_rate is not None else None

        obj = cls(
            direction=direction,
            total_time=total_time,
            num_increments=num_increments,
            target_def_grad=def_grad_aim,
            target_def_grad_rate=def_grad_rate,
            stress=stress_arr,
            dump_frequency=dump_frequency,
        )
        obj._method_name = _method_name
        obj._method_args = _method_args
        return obj

    @classmethod
    def biaxial(
        cls,
        total_time: float,
        num_increments: int,
        direction: str,
        target_def_grad: Optional[float] = None,
        target_def_grad_rate: Optional[float] = None,
        dump_frequency: Optional[int] = 1,
    ) -> LoadStep:
        """
        Generate a biaxial load step.

        Parameters
        ----------
        total_time
        num_increments
        direction
            String of two characters, ij, where {i,j} ∈ {"x","y","z"}, corresponding to
            the two loading directions.
        target_def_grad
            Target deformation gradient to achieve along both loading direction
            components.
        target_def_grad_rate
            Target deformation gradient rate to achieve along both loading direction
            components.
        dump_frequency
            By default, 1, meaning results are written out every increment.

        """

        # TODO this should be called `equibiaxial`? How is this different from `2D_planar`?
        _method_name = "biaxaial"
        _method_args = {
            "total_time": total_time,
            "num_increments": num_increments,
            "direction": direction,
            "target_def_grad_rate": target_def_grad_rate,
            "target_def_grad": target_def_grad,
            "dump_frequency": dump_frequency,
        }

        # Validation:
        msg = "Specify either `target_def_grad_rate` or `target_def_grad`."
        if all([t is None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)
        if all([t is not None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)

        if target_def_grad_rate is not None:
            def_grad_val = target_def_grad_rate
        else:
            def_grad_val = target_def_grad

        dir_idx = ["x", "y", "z"]
        load_dir_idx = []
        for load_dir in direction:
            try:
                loading_dir_idx = dir_idx.index(load_dir)
                load_dir_idx.append(loading_dir_idx)
            except ValueError:
                msg = (
                    f'Loading direction "{load_dir}" not allowed. Both loading directions '
                    f'should be one of "x", "y" or "z".'
                )
                raise ValueError(msg)

        zero_stress_dir = list(set(dir_idx) - set(direction))[0]
        zero_stress_dir_idx = dir_idx.index(zero_stress_dir)

        dg_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.zeros((3, 3)))
        stress_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.ones((3, 3)))

        dg_arr[load_dir_idx, load_dir_idx] = def_grad_val
        dg_arr.mask[zero_stress_dir_idx, zero_stress_dir_idx] = True
        stress_arr.mask[zero_stress_dir_idx, zero_stress_dir_idx] = False

        def_grad = dg_arr if target_def_grad is not None else None
        def_grad_rate = dg_arr if target_def_grad_rate is not None else None

        obj = cls(
            direction=direction,
            total_time=total_time,
            num_increments=num_increments,
            target_def_grad=def_grad,
            target_def_grad_rate=def_grad_rate,
            stress=stress_arr,
            dump_frequency=dump_frequency,
        )
        obj._method_name = _method_name
        obj._method_args = _method_args
        return obj

    @classmethod
    def plane_strain(
        cls,
        total_time,
        num_increments,
        direction,
        target_def_grad: Optional[float] = None,
        target_def_grad_rate: Optional[float] = None,
        dump_frequency: Optional[int] = 1,
        strain_rate_mode: Optional[Union[StrainRateMode, str]] = None,
    ) -> LoadStep:
        """Generate a plane-strain load step.

        Parameters
        ----------
        total_time
        num_increments
        direction
            String of two characters, ij, where {i,j} ∈ {"x","y","z"}. The first
            character, i, corresponds to the loading direction and the second, j,
            corresponds to the zero-strain direction. Zero stress will be specified on the
            remaining direction.
        target_def_grad
            Target deformation gradient to achieve along the loading direction component.
        target_def_grad_rate
            Target deformation gradient rate to achieve along the loading direction
            component.
        dump_frequency
            By default, 1, meaning results are written out every increment.
        strain_rate_mode
            One of "def_grad_rate", "vel_grad", "vel_grad_approx". If not specified,
            default is "def_grad_rate". Use "vel_grad_approx" for specifying non-mixed
            boundary conditions.
        """

        _method_name = "plane_strain"
        _method_args = {
            "total_time": total_time,
            "num_increments": num_increments,
            "direction": direction,
            "target_def_grad": target_def_grad,
            "target_def_grad_rate": target_def_grad_rate,
            "dump_frequency": dump_frequency,
            "strain_rate_mode": strain_rate_mode,
        }

        # Validation:
        msg = "Specify either `target_def_grad_rate` or `target_def_grad`."
        if all([t is None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)
        if all([t is not None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)

        if strain_rate_mode is None:
            strain_rate_mode = StrainRateMode.DEF_GRAD_RATE
        else:
            strain_rate_mode = get_enum_by_name_or_val(StrainRateMode, strain_rate_mode)

        if (
            strain_rate_mode in (StrainRateMode.VEL_GRAD, StrainRateMode.VEL_GRAD_APPROX)
            and target_def_grad_rate is None
        ):
            msg = (
                f"`target_def_grad_rate` must be specified for `strain_rate_mode` "
                f"{strain_rate_mode!r}"
            )
            raise ValueError(msg)

        if target_def_grad_rate is not None:
            def_grad_val = target_def_grad_rate
        else:
            def_grad_val = target_def_grad

        dir_idx = ["x", "y", "z"]
        loading_dir, zero_strain_dir = direction
        try:
            loading_dir_idx = dir_idx.index(loading_dir)
        except ValueError:
            msg = (
                f'Loading direction "{loading_dir}" not allowed. It should be one of '
                f'"x", "y" or "z".'
            )
            raise ValueError(msg)

        if zero_strain_dir not in dir_idx:
            msg = (
                f'Zero-strain direction "{zero_strain_dir}" not allowed. It should be '
                f'one of "x", "y" or "z".'
            )
            raise ValueError(msg)

        zero_stress_dir = list(set(dir_idx) - {loading_dir, zero_strain_dir})[0]
        zero_stress_dir_idx = dir_idx.index(zero_stress_dir)

        dg_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.zeros((3, 3)))
        stress_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.ones((3, 3)))

        dg_arr[loading_dir_idx, loading_dir_idx] = def_grad_val

        if strain_rate_mode is StrainRateMode.VEL_GRAD:
            # When using L with mixed BCs, each row must be either L or P:
            dg_arr.mask[zero_stress_dir_idx] = True
            stress_arr.mask[zero_stress_dir_idx] = False

        elif strain_rate_mode is StrainRateMode.VEL_GRAD_APPROX:
            dg_arr = dg_arr.data  # No need for a masked array
            # Without mixed BCs, we can get volume conservation with Trace(L) = 0:
            dg_arr[zero_stress_dir_idx, zero_stress_dir_idx] = -def_grad_val
            stress_arr = None

        elif strain_rate_mode is StrainRateMode.DEF_GRAD_RATE:
            dg_arr.mask[zero_stress_dir_idx, zero_stress_dir_idx] = True
            stress_arr.mask[zero_stress_dir_idx, zero_stress_dir_idx] = False

        if strain_rate_mode in (StrainRateMode.VEL_GRAD, StrainRateMode.VEL_GRAD_APPROX):
            def_grad = None
            def_grad_rate = None
            vel_grad = dg_arr
        else:
            def_grad = dg_arr if target_def_grad is not None else None
            def_grad_rate = dg_arr if target_def_grad_rate is not None else None
            vel_grad = None

        obj = cls(
            direction=direction,
            total_time=total_time,
            num_increments=num_increments,
            target_def_grad=def_grad,
            target_def_grad_rate=def_grad_rate,
            vel_grad=vel_grad,
            stress=stress_arr,
            dump_frequency=dump_frequency,
        )
        obj._method_name = _method_name
        obj._method_name = _method_args
        return obj

    @classmethod
    def planar_2D(
        cls,
        total_time: Union[int, float],
        num_increments: int,
        normal_direction: str,
        target_def_grad=None,
        target_def_grad_rate=None,
        dump_frequency=1,
    ) -> LoadStep:
        """Generate a planar 2D load case normal to the x-, y-, or z-direction.

        Parameters
        ----------
        total_time
        num_increments
        normal_direction
            A single character, "x", "y" or "z", representing the loading plane normal
            direction.
        target_def_grad : (nested) list of float or ndarray of shape (2, 2)
            Target deformation gradient components. Either a 2D array, nested list, or a
            flat list. If passed as a flat list, the first and fourth elements correspond
            to the normal components of the deformation gradient tensor. The second
            element corresponds to the first-row, second-column (shear) component and the
            third element corresponds to the second-row, first-column (shear) component.
        target_def_grad_rate : (nested) list of float or ndarray of shape (2, 2)
            Target deformation gradient rate components. Either a 2D array, nested list,
            or a flat list. If passed as a flat list, the first and fourth elements
            correspond to the normal components of the deformation gradient rate tensor.
            The second element corresponds to the first-row, second-column (shear)
            component and the third element corresponds to the second-row, first-column
            (shear) component.
        dump_frequency
            By default, 1, meaning results are written out every increment.
        """

        _method_name = "planar_2D"
        _method_args = {
            "total_time": total_time,
            "num_increments": num_increments,
            "normal_direction": normal_direction,
            "target_def_grad": target_def_grad,
            "target_def_grad_rate": target_def_grad_rate,
            "dump_frequency": dump_frequency,
        }

        # Validation:
        msg = "Specify either `target_def_grad_rate` or `target_def_grad`."
        if all([t is None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)
        if all([t is not None for t in [target_def_grad_rate, target_def_grad]]):
            raise ValueError(msg)
        if target_def_grad_rate is not None:
            def_grad_vals = target_def_grad_rate
        else:
            def_grad_vals = target_def_grad

        # Flatten list/array:
        if isinstance(def_grad_vals, list):
            if isinstance(def_grad_vals[0], list):
                def_grad_vals = [j for i in def_grad_vals for j in i]
        elif isinstance(def_grad_vals, np.ndarray):
            def_grad_vals = def_grad_vals.flatten()

        dir_idx = ["x", "y", "z"]
        try:
            normal_dir_idx = dir_idx.index(normal_direction)
        except ValueError:
            msg = (
                f"Normal direction {normal_direction!r} not allowed. It should be one of "
                f'"x", "y" or "z".'
            )
            raise ValueError(msg)

        loading_col_idx = list({0, 1, 2} - {normal_dir_idx})
        dg_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.zeros((3, 3)))
        stress_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.zeros((3, 3)))

        dg_row_idx = [
            loading_col_idx[0],
            loading_col_idx[0],
            loading_col_idx[1],
            loading_col_idx[1],
        ]
        dg_col_idx = [
            loading_col_idx[0],
            loading_col_idx[1],
            loading_col_idx[0],
            loading_col_idx[1],
        ]
        dg_arr[dg_row_idx, dg_col_idx] = def_grad_vals
        dg_arr.mask[:, normal_dir_idx] = True
        stress_arr.mask[:, loading_col_idx] = True

        def_grad = dg_arr if target_def_grad is not None else None
        def_grad_rate = dg_arr if target_def_grad_rate is not None else None

        obj = cls(
            normal_direction=normal_direction,
            total_time=total_time,
            num_increments=num_increments,
            target_def_grad=def_grad,
            target_def_grad_rate=def_grad_rate,
            stress=stress_arr,
            dump_frequency=dump_frequency,
        )
        obj._method_name = _method_name
        obj._method_name = _method_args
        return obj

    @classmethod
    def random_2D(
        cls,
        total_time: Union[int, float],
        num_increments: int,
        normal_direction: str,
        target_def_grad_rate: float = None,
        target_def_grad: float = None,
        dump_frequency: int = 1,
    ) -> LoadStep:
        """Get a random 2D planar load case.

        Parameters
        ----------
        total_time
        num_increments
        normal_direction
            A single character, "x", "y" or "z", representing the loading plane normal
            direction.
        target_def_grad_rate
            Maximum target deformation gradient rate component. Components will be sampled
            randomly in the interval [-target_def_grad_rate, +target_def_grad_rate).
        target_def_grad
            Maximum target deformation gradient component. Components will be sampled
            randomly in the interval [-target_def_grad, +target_def_grad).
        dump_frequency
            By default, 1, meaning results are written out every increment.

        """
        # TODO: shouldn't this be implemented in the same was as in random_3D?

        def_grad_vals = (np.random.random(4) - 0.5) * 2
        if target_def_grad_rate is not None:
            target_def_grad_rate *= def_grad_vals
        else:
            target_def_grad *= def_grad_vals
            target_def_grad += np.eye(2).reshape(-1)

        load_case = cls.planar_2D(
            total_time=total_time,
            num_increments=num_increments,
            normal_direction=normal_direction,
            target_def_grad=target_def_grad,
            target_def_grad_rate=target_def_grad_rate,
            dump_frequency=dump_frequency,
        )
        return load_case

    @classmethod
    def random_3D(
        cls,
        total_time,
        num_increments,
        target_def_grad,
        dump_frequency=1,
    ) -> LoadStep:

        _method_name = "random_3D"
        _method_args = {
            "total_time": total_time,
            "num_increments": num_increments,
            "target_def_grad": target_def_grad,
            "dump_frequency": dump_frequency,
        }

        # Five stretch components, since it's a symmetric matrix and the trace must be
        # zero:
        stretch_comps = (np.random.random((5,)) - 0.5) * target_def_grad
        stretch = np.zeros((3, 3)) * np.nan

        # Diagonal comps:
        stretch[[0, 1], [0, 1]] = stretch_comps[:2]
        stretch[2, 2] = -(stretch[0, 0] + stretch[1, 1])

        # Off-diagonal comps:
        stretch[[1, 0], [0, 1]] = stretch_comps[2]
        stretch[[2, 0], [0, 2]] = stretch_comps[3]
        stretch[[1, 2], [2, 1]] = stretch_comps[4]

        # Add the identity:
        U = stretch + np.eye(3)

        defgrad = U

        # Ensure defgrad has a unit determinant:
        defgrad = defgrad / (np.linalg.det(defgrad) ** (1 / 3))

        dg_arr = np.ma.masked_array(defgrad, mask=np.zeros((3, 3), dtype=int))
        stress_arr = np.ma.masked_array(
            np.zeros((3, 3), dtype=int), mask=np.ones((3, 3), dtype=int)
        )

        obj = cls(
            total_time=total_time,
            num_increments=num_increments,
            target_def_grad=dg_arr,
            stress=stress_arr,
            dump_frequency=dump_frequency,
        )
        obj._method_name = _method_name
        obj._method_args = _method_args
        return obj

    @classmethod
    def uniaxial_cyclic(
        cls,
        max_stress: float,
        min_stress: float,
        cycle_frequency: float,
        num_increments_per_cycle: int,
        num_cycles: int,
        direction: str,
        waveform: str = "sine",
        dump_frequency=1,
    ) -> List[LoadStep]:

        dir_idx = ["x", "y", "z"]
        try:
            loading_dir_idx = dir_idx.index(direction)
        except ValueError:
            msg = (
                f'Loading direction "{direction}" not allowed. It should be one of "x", '
                f'"y" or "z".'
            )
            raise ValueError(msg)

        cycle_time = 1 / cycle_frequency

        if waveform.lower() == "sine":

            sig_mean = (max_stress + min_stress) / 2
            sig_diff = max_stress - min_stress

            A = 2 * np.pi / cycle_time
            time = (
                np.linspace(0, 2 * np.pi, num=num_increments_per_cycle, endpoint=True) / A
            )
            sig = (sig_diff / 2) * np.sin(A * time) + sig_mean

            time_per_inc = cycle_time / num_increments_per_cycle

            stress_mask = np.ones((sig.size, 3, 3))
            stress_mask[:, [0, 1, 2], [0, 1, 2]] = 0
            stress_arr = np.ma.masked_array(
                data=np.zeros((sig.size, 3, 3)),
                mask=stress_mask,
            )
            stress_arr[:, loading_dir_idx, loading_dir_idx] = sig

            dg_arr = np.ma.masked_array(np.zeros((3, 3)), mask=np.eye(3))

            cycle = []
            for time_idx, _ in enumerate(time):
                cycle.append(
                    {
                        "num_increments": 1,
                        "total_time": time_per_inc,
                        "stress": stress_arr[time_idx],
                        "target_def_grad": dg_arr,
                        "dump_frequency": dump_frequency,
                    }
                )

            out = []
            for cycle_idx in range(num_cycles):
                cycle_i = copy.deepcopy(cycle)
                if cycle_idx != num_cycles - 1:
                    # intermediate cycle; remove repeated increment:
                    cycle_i = cycle_i[:-1]
                out.extend(cycle_i)

            out = [cls(**i) for i in out]

        else:
            raise NotImplementedError('Only waveform "sine" is currently allowed.')

        return out


@dataclass
class LoadCase(ParameterValue):

    # TODO: store step data (e.g. stress tensor for each step) in combined arrays; steps
    # can be a (cached) property that indexes those arrays?

    _typ = "load_case"

    steps: List[LoadStep]

    def __post_init__(self):
        for step_idx in range(len(self.steps)):
            if not isinstance(self.steps[step_idx], LoadStep):
                step_i = copy.deepcopy(self.steps[step_idx])  # don't mutate
                _method_name = step_i.pop("_method_name", None)
                _method_args = step_i.pop("_method_args", None)
                self.steps[step_idx] = LoadStep(**step_i)
                self.steps[step_idx]._method_name = _method_name
                self.steps[step_idx]._method_args = _method_args

    @property
    def num_steps(self):
        return len(self.steps)

    @property
    def type(self):
        if self.num_steps == 1:
            return self.steps[0].type
        else:
            return self.types

    @property
    def types(self):
        return [i.type for i in self.steps]

    @classmethod
    def uniaxial(cls, **kwargs) -> LoadCase:
        """A single-step uniaxial load case.

        See `LoadStep.uniaxial` for argument documentation.

        """
        return cls(steps=[LoadStep.uniaxial(**kwargs)])

    @classmethod
    def biaxial(cls, **kwargs) -> LoadCase:
        """A single-step biaxial load case.

        See `LoadStep.biaxial` for argument documentation.

        """
        return cls(steps=[LoadStep.biaxial(**kwargs)])

    @classmethod
    def plane_strain(cls, **kwargs) -> LoadCase:
        """A single-step plane-strain load case.

        See `LoadStep.plane_strain` for argument documentation.

        """
        return cls(steps=[LoadStep.plane_strain(**kwargs)])

    @classmethod
    def planar_2D(cls, **kwargs) -> LoadCase:
        """A single-step planar 2D load case.

        See `LoadStep.planar_2D` for argument documentation.

        """
        return cls(steps=[LoadStep.planar_2D(**kwargs)])

    @classmethod
    def random_2D(cls, **kwargs) -> LoadCase:
        """A single-step random 2D load case.

        See `LoadStep.random_2D` for argument documentation.

        """
        return cls(steps=[LoadStep.random_2D(**kwargs)])

    @classmethod
    def random_3D(cls, **kwargs) -> LoadCase:
        """A single-step random 3D load case.

        See `LoadStep.random_3D` for argument documentation.

        """
        return cls(steps=[LoadStep.random_3D(**kwargs)])

    @classmethod
    def uniaxial_cyclic(cls, **kwargs) -> LoadCase:
        """Uniaxial cyclic loading.

        See `LoadStep.uniaxial_cyclic` for argument documentation."""
        return cls(steps=LoadStep.uniaxial_cyclic(**kwargs))

    @classmethod
    def example_uniaxial(cls) -> LoadCase:
        """A non-parametrisable example single-step uniaxial load case."""
        return cls(steps=[LoadStep.example_uniaxial()])

    @classmethod
    def multistep(cls, steps: List[Union[Dict, LoadStep]]) -> LoadCase:
        """A load case with multiple steps.

        Parameters
        ----------
        steps
            A list of `LoadStep` objects or `dict`s representing `LoadStep` objects, in
            which case if a `dict` has a key `type`, the corresponding `LoadStep`
            classmethod will be invoked with the remainder of the `dict` items.

        """
        step_objs = []
        for step_i in steps:
            if isinstance(step_i, LoadStep):
                step_objs.append(step_i)
            else:
                # assume a dict
                step_i = copy.deepcopy(step_i)  # don't mutate
                step_i_type = step_i.pop("type", None)
                if step_i_type:
                    # assume a LoadStep class method:
                    try:
                        method = getattr(LoadStep, step_i_type)
                    except AttributeError:
                        raise ValueError(
                            f"No `LoadStep` method named {step_i_type!r} for load step "
                            f"specification {step_i!r}."
                        )
                    steps = method(**step_i)
                    if not isinstance(steps, list):
                        # in the general case, multiple `LoadStep`s might be generated:
                        steps = [steps]
                    step_objs.extend(steps)
                else:
                    step_objs.append(LoadStep(**step_i))

        return cls(steps=step_objs)
