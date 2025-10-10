#!/usr/bin/env python3

"""Find supported python versions for this package."""

import json
from collections.abc import Generator
from itertools import count
from pathlib import Path

import tomli
from packaging.specifiers import SpecifierSet
from packaging.version import Version

MAX_VERSION = 13  # 3.13


def get_python_versions() -> Generator[str, None, None]:
    """Get all python versions this package is compatible with."""
    with Path("pyproject.toml").open("rb") as f:
        pyproject_data = tomli.load(f)

    specifier = SpecifierSet(pyproject_data["project"]["requires-python"])

    below_spec = True
    for v_minor in count():
        version = Version(f"3.{v_minor}")

        # above max version: return
        if v_minor > MAX_VERSION:
            return

        # in specifier: yield
        if version in specifier:
            below_spec = False
            yield str(version)
            continue

        # below specifier: skip
        if below_spec:
            continue

        # above specifier: return
        return


print(json.dumps(list(get_python_versions())))
