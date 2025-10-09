"""
Usage:

    ruffup


Runs ruff format + isort on the current path.

Thanks to https://stackoverflow.com/a/78156861/344286
"""

import os
import sys


def main() -> None:
    path = path or "."
    os.system(f"ruff check --select I --fix .")
    os.system(f"ruff format .")


if __name__ == "__main__":
    main()
