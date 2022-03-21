:: Might need to disable cloud sync. engines during this
:: Make sure we ran `poetry install --extras "pyinstaller"` (or `poetry install --no-dev --extras "pyinstaller"`)
rmdir /s "build"
rmdir /s "dist"
del matflow.spec
poetry run pyinstaller --name=matflow --onefile ../matflow/cli.py 
