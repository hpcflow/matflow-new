# Make sure we ran `poetry install --extras "pyinstaller"` (or `poetry install --no-dev --extras "pyinstaller"`)
# Might need to disable cloud sync. engines during this
param($ExeName = "matflow", $LogLevel = "INFO")
poetry run pyinstaller --log-level=$LogLevel --onefile --clean -y --name=$ExeName ..\matflow\cli.py
