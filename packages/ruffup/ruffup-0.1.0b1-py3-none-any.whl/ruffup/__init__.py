"""
Usage:

    ruffup

or

    ruffup PATH

Either run ruff format + isort on the current path, or on the path provided.

Thanks to https://stackoverflow.com/a/78156861/344286
"""

import os
import sys


def main(path=".") -> None:
    path = path or "."
    print("Hello from ruffup!")
    os.system(f"ruff check --select I --fix {path}")
    os.system(f"ruff format {path}")


if __name__ == "__main__":
    main(*sys.argv[1:])
