import copy
from damask_parse.writers import write_material as write_material_


def write_material(
    path,
    volume_element,
    homogenization,
    damask_phases,
    single_crystal_parameters,
):
    if single_crystal_parameters is not None:
        # merge single-crystal properties into phases:
        damask_phases = copy.deepcopy(damask_phases)
        for phase_label in damask_phases.keys():
            SC_params_name = damask_phases[phase_label]["mechanical"]["plastic"].pop(
                "single_crystal_parameters", None
            )
            if SC_params_name:
                SC_params = single_crystal_parameters[SC_params_name]
                damask_phases[phase_label]["mechanical"]["plastic"].update(**SC_params)

    write_material_(
        dir_path=path.parent,
        homog_schemes=homogenization,
        phases=damask_phases,
        volume_element=volume_element,
        name=path.name,
    )
