from PyInstaller.utils.hooks import collect_data_files

hiddenimports = ["matflow.data", "matflow.param_classes"]
datas = collect_data_files("matflow.data")
datas += collect_data_files(
    "matflow.tests",
    include_py_files=True,
    excludes=("**/__pycache__",),
)
datas += collect_data_files(
    "matflow.data.scripts",
    include_py_files=True,
    excludes=("**/__pycache__",),
)
