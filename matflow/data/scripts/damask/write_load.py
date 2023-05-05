import numpy as np
from ruamel.yaml import YAML


def format_1D_masked_array(arr, fill_symbol="x"):
    "Also formats non-masked array."

    return [
        x.item() if not isinstance(x, np.ma.core.MaskedConstant) else fill_symbol
        for x in arr
    ]


def format_2D_masked_array(arr, fill_symbol="x"):
    out = []
    for x in arr:
        sub = []
        for i in x:
            val = (
                i.item() if not isinstance(i, np.ma.core.MaskedConstant) else fill_symbol
            )
            sub.append(val)
        out.append(sub)
    return out


def masked_array_from_list(arr, fill_value="x"):
    """Generate a (masked) array from a 1D list whose elements may contain a fill value."""

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
        return np.ma.masked_array(data, mask=mask)
    else:
        return data


def write_load(path, load_case):

    solver = {"mechanical": "spectral_basic"}

    load_steps = []
    load_case = load_case.to_dict()
    def_grad_aim = load_case.get("def_grad_aim")
    def_grad_rate = load_case.get("def_grad_rate")
    vel_grad = load_case.get("vel_grad")
    stress = load_case.get("stress")
    stress_rate = load_case.get("stress_rate")
    total_time = load_case["total_time"]
    num_increments = load_case["num_increments"]
    freq = load_case.get("dump_frequency", 1)

    if sum((x is not None for x in (def_grad_aim, def_grad_rate, vel_grad))) > 1:
        msg = "Specify only one of `def_grad_rate`,  `def_grad_aim` " "and `vel_grad`."
        raise ValueError(msg)

    # If def_grad_aim/rate is masked array, stress masked array should also be passed,
    # such that the two arrays are component-wise exclusive.

    dg_arr = None
    dg_arr_sym = None
    if def_grad_aim is not None:
        dg_arr = def_grad_aim
        dg_arr_sym = "F"
    elif def_grad_rate is not None:
        dg_arr = def_grad_rate
        dg_arr_sym = "dot_F"
    elif vel_grad is not None:
        dg_arr = vel_grad
        dg_arr_sym = "L"

    stress_arr = None
    stress_arr_sym = None
    if stress is not None:
        stress_arr = stress
        stress_arr_sym = "P"
    elif stress_rate is not None:
        stress_arr = stress_rate
        stress_arr_sym = "dot_P"

    # If load case tensors are specified as (nested) lists with fill values, convert
    # to masked arrays:
    if isinstance(dg_arr, list):
        if isinstance(dg_arr[0], list):
            dg_arr = [j for i in dg_arr for j in i]  # flatten
        dg_arr = masked_array_from_list(dg_arr, fill_value="x").reshape((3, 3))

    if isinstance(stress_arr, list):
        if isinstance(stress_arr[0], list):
            stress_arr = [j for i in stress_arr for j in i]  # flatten
        stress_arr = masked_array_from_list(stress_arr, fill_value="x").reshape((3, 3))

    load_step = {"boundary_conditions": {"mechanical": {}}}
    bc_mech = load_step["boundary_conditions"]["mechanical"]

    if stress_arr is None:

        if dg_arr is None:
            msg = "Specify one of `def_grad_rate`, `def_grad_aim` or " "`vel_grad`."
            raise ValueError(msg)

        if isinstance(dg_arr, np.ma.core.MaskedArray):
            msg = (
                "To use mixed boundary conditions, `stress`/`stress_rate` must be "
                "passed as a masked array."
            )
            raise ValueError(msg)

        bc_mech[dg_arr_sym] = format_2D_masked_array(dg_arr)

    else:
        if isinstance(stress_arr, np.ma.core.MaskedArray):

            if dg_arr is None:
                msg = "Specify one of `def_grad_rate`, `def_grad_aim` or " "`vel_grad`."
                raise ValueError(msg)

            msg = (
                "`def_grad_rate`, `def_grad_aim` or `vel_grad` must be "
                "component-wise exclusive with `stress` or `stress_rate` (both as "
                "masked arrays)"
            )
            if not isinstance(dg_arr, np.ma.core.MaskedArray):
                raise ValueError(msg)
            if np.any(dg_arr.mask == stress_arr.mask):
                raise ValueError(msg)

            if dg_arr_sym == "L":
                if any((sum(row) not in (0, 3) for row in dg_arr.mask)):
                    msg = "Specify all or no values for each row of " "`vel_grad`"
                    raise ValueError(msg)

            bc_mech[dg_arr_sym] = format_2D_masked_array(dg_arr)
            bc_mech[stress_arr_sym] = format_2D_masked_array(stress_arr)

        else:
            if dg_arr is not None:
                msg = (
                    "To use mixed boundary conditions, `stress` or `stress_rate`"
                    f"must be passed as a masked array."
                )
                raise ValueError(msg)

            bc_mech[stress_arr_sym] = format_2D_masked_array(stress_arr)

        load_step["discretization"] = {
            "t": total_time,
            "N": num_increments,
        }
        load_step["f_out"] = freq

        load_steps.append(load_step)

    print(f"{bc_mech=}")
    load_data = {"solver": solver, "loadstep": load_steps}

    yaml = YAML()
    yaml.dump(load_data, path)
