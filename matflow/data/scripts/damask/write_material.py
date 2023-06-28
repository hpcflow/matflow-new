from damask_parse.writers import write_material as write_material_


def write_material(path, volume_element, homogenization, damask_phases):
    write_material_(
        dir_path=path.parent,
        homog_schemes=homogenization,
        phases=damask_phases,
        volume_element=volume_element,
        name=path.name,
    )
