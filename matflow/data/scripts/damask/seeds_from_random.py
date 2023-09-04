from damask import seeds
from damask import Rotation
import numpy as np


def seeds_from_random(
    VE_size,
    num_grains,
    phase_label,
    orientation_coordinate_system=None,
):

    VE_size = np.array(VE_size)
    position = seeds.from_random(VE_size, num_grains)
    rotation = Rotation.from_random(shape=(num_grains,))
    out = {
        "microstructure_seeds": {
            "position": position,
            "orientations": {
                "data": rotation.quaternion,
                "representation": {
                    "type": "quaternion",
                    "quat_order": "scalar_vector",
                },
                "unit_cell_alignment": {
                    "x": "a",
                    "y": "b_star",
                    "z": "c",
                },
            },
            "box_size": VE_size,
            "random_seed": None,
            "phase_label": phase_label,
        }
    }
    return out
