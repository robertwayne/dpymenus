# This file is used for calling scripts through the poetry CLI.

from subprocess import run


def fmt():
    """Runs black on the project source directory. Uses the config defined in `pyproject.toml`."""
    run(['black', 'dpymenus/', 'examples'])


def rtd():
    """Generates a compatible requirements.txt file from our pyproject.toml dependencies. This is
    required by readthedocs configuration."""
    run(['poetry', 'export', '--output', 'docs/requirements.txt', '--dev', '--without-hashes'])
