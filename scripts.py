# This file is used for calling scripts through the poetry CLI.

from subprocess import check_call


def fmt():
    """Runs black on the project source directory. Uses the config defined in `pyproject.toml`."""
    check_call(["black", "dpymenus/", "examples"])
