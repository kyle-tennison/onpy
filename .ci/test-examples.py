"""Run the examples in examples/ and check for a good status code"""

import os
from pathlib import Path
import subprocess
import sys

from loguru import logger


examples_path = Path(__file__).parent.parent.joinpath("examples").resolve()


examples: list[Path] = []
for dir in examples_path.iterdir():
    if dir.is_dir():
        examples.extend(
            [
                f
                for f in dir.iterdir()
                if f.suffix in (".ipynb", ".py") and not f.name.endswith("-tmp.py")
            ]
        )

# Use nbconvert to convert notebooks into python files
for example in examples:

    if example.suffix != ".ipynb":
        continue

    logger.info(f"Converting '{example.name}' to python.")

    output = example.name.replace(".ipynb", "-tmp.py")

    process = subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "python",
            str(example.resolve()),
            "--output",
            output,
        ],
        check=False,
    )

    if process.returncode != 0:
        logger.error(f"Failed to convert notebook '{example.name}' to python")
        sys.exit(1)

logger.info(f"\n\nTesting the following files:\n{[f.name for f in examples]}\n\n")

for example in examples:

    filename = (
        example.name
        if example.suffix == ".py"
        else example.name.replace(".ipynb", "-tmp.py")
    )
    file = example.parent.joinpath(filename)

    logger.debug(f"Running file '{filename}'...")

    # change dir into example dir
    process = subprocess.run(
        [sys.executable, file.resolve()], check=False, env=os.environ
    )
    if process.returncode != 0:
        logger.error(f"Error in example '{example}'")
        exit(1)

    else:
        logger.debug(f"Test passed with code {process.returncode}")
        if file.name.endswith("-tmp.py"):
            file.unlink()


exit(0)
