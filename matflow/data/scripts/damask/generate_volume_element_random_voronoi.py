import copy
import numpy as np
from damask import Grid
from damask_parse.utils import validate_volume_element, validate_orientations


def generate_volume_element_random_voronoi(
    microstructure_seeds,
    VE_grid_size,
    homog_label,
):
    grid_obj = Grid.from_Voronoi_tessellation(
        cells=np.array(VE_grid_size),
        size=np.array(microstructure_seeds["size"]),
        seeds=np.array(microstructure_seeds["position"]),
        periodic=True,
    )
    oris = copy.deepcopy(microstructure_seeds["orientations"])
    oris = validate_orientations(oris)

    num_grains = len(microstructure_seeds["position"])
    const_phase_lab = np.array(microstructure_seeds["phase_labels"])[
        np.zeros(num_grains, dtype=int)
    ]

    ori_idx = np.arange(num_grains)

    volume_element = {
        "size": grid_obj.size.astype(float).tolist(),
        "grid_size": grid_obj.cells.tolist(),
        "orientations": oris,
        "element_material_idx": grid_obj.material,
        "constituent_material_idx": np.arange(num_grains),
        "constituent_material_fraction": np.ones(num_grains),
        "constituent_phase_label": const_phase_lab,
        "constituent_orientation_idx": ori_idx,
        "material_homog": np.full(num_grains, homog_label),
    }
    volume_element = validate_volume_element(volume_element)
    return {"volume_element": volume_element}
