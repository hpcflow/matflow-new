from damask import __version__
from damask_parse.writers import write_load_case


def write_load(path, load_case):

    if not isinstance(load_case, list):
        load_case = [load_case]

    load_cases = [i.to_dict() for i in load_case]
    write_load_case(
        dir_path=path.parent,
        load_cases=load_cases,
        name=path.name,
        write_2D_arrs=(__version__ != "3.0.0-alpha3"),
    )
