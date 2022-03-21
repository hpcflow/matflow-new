# Make sure we ran `poetry install --extras "pyinstaller"` (or `poetry install --no-dev --extras "pyinstaller"`)
rm -r build
rm -r dist
rm matflow.spec
poetry run pyinstaller --name=matflow --onefile ../matflow/cli.py 
