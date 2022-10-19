from PyInstaller.utils.hooks import collect_data_files

hiddenimports = ["hpcflow.sdk.data"]
datas = collect_data_files("hpcflow")
