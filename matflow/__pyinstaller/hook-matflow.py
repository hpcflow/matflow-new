from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("matflow.data")
datas = collect_data_files(
    "matflow.tests",
    include_py_files=True,
    excludes=("**/__pycache__",),
)
