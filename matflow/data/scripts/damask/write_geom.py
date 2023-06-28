from damask_parse.writers import write_geom as write_geom_


def write_geom(path, volume_element):
    write_geom_(dir_path=path.parent, volume_element=volume_element, name=path.name)
