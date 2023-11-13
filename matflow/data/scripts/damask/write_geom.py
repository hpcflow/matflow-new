from pathlib import Path

from damask_parse.writers import write_geom as write_geom_


def write_geom(path, volume_element):
    path = Path(path)  # if using as a non IFG script, `path` will be a normal input
    write_geom_(dir_path=path.parent, volume_element=volume_element, name=path.name)
