from pathlib import Path

import numpy as np


def get_yield_stress(damask_hdf5_file, calculate_yield_stress, VE_response):

    yield_point = calculate_yield_stress["yield_point"]

    strain_name = calculate_yield_stress.get(
        "strain_name", "vol_avg_equivalent_plastic_strain"
    )
    strain_data_type = calculate_yield_stress.get("strain_data_type", "phase_data")

    stress_name = calculate_yield_stress.get("stress_name", "vol_avg_equivalent_stress")
    stress_data_type = calculate_yield_stress.get("stress_data_type", "phase_data")

    strain = VE_response[strain_data_type][strain_name]["data"][:]
    yield_idx = np.argmin(np.abs(strain - yield_point))
    yield_stress = VE_response[stress_data_type][stress_name]["data"][yield_idx]
    return yield_stress
