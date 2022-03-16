import json
from pathlib import Path
import re
import sys

from jinja2 import Template


def main(template_dir, vars_json_path):

    template_dir = Path(template_dir)
    if not template_dir.is_dir():
        raise ValueError(f"Not a directory: {str(template_dir)}.")

    template_files = list(template_dir.glob("*.in"))

    vars_json_path = Path(vars_json_path)

    with vars_json_path.open("r") as fh:
        jsonc_str = fh.read()
        json_str = re.sub(
            r'\/\/(?=([^"]*"[^"]*")*[^"]*$).*', "", jsonc_str, flags=re.MULTILINE
        )
        vars = json.loads(json_str)

    for file_path in template_files:

        with file_path.open("r") as fh:
            template = Template(fh.read())

        rendered = template.render(**vars)

        with file_path.with_suffix("").open("w", newline="\n") as fh:
            fh.write(rendered + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
