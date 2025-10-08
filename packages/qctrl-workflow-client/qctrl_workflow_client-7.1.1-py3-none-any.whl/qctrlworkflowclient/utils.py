# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
from __future__ import annotations

import sys
from dataclasses import dataclass
from importlib.metadata import (
    PackageNotFoundError,
    version,
)
from pathlib import Path
from types import ModuleType
from typing import Optional

import requests
import tomli
from importlib_metadata import packages_distributions
from packaging.version import parse


def get_installed_version(package: str) -> Optional[str]:
    """
    Get the installed version of the package. If
    the version cannot be found (e.g. package not installed)
    then None is returned.
    """
    try:
        pkg_version = version(package)

    except PackageNotFoundError:
        pkg_version = None

    return pkg_version


@dataclass
class PackageInfo:
    """
    Dataclass containing information about a Python package.
    """

    name: str
    install_name: str
    import_name: str
    changelog_url: Optional[str] = None


def get_latest_pypi_version(package: str) -> str:
    """
    Retrieve package from PyPI and return latest version.
    """
    package_url = f"https://pypi.org/pypi/{package}/json"
    contents = requests.get(package_url, timeout=60).json()
    return contents["info"]["version"]


def check_package_version(package: PackageInfo) -> None:
    """
    Fetch the latest version of a package from PyPI and
    show an upgrade message if the current version is outdated.
    """
    local_package = sys.modules.get(package.import_name)
    assert local_package is not None, f"{package.import_name} is not found."
    local_version = getattr(local_package, "__version__")
    latest_version = get_latest_pypi_version(package.install_name)

    if parse(local_version) < parse(latest_version):
        print(f"{package.name} update available.")
        print(f"Latest version is {latest_version}, you have {local_version}.")
        if package.changelog_url is not None:
            print(f"Visit {package.changelog_url} for the latest product updates.")


def package_versions_table(package_names: list[str]) -> str:
    """
    Create a Markdown-formatted table showing the Python version being used
    as well as the versions of the provided packages.

    Parameters
    ----------
    package_names : list[str]
        The import names of the packages to display in the table.

    Returns
    -------
    str
        A string containing the Markdown-formatted table.
    """

    # List containing the items in the different rows.
    table_items = get_package_versions(package_names=package_names)

    # Widths of the table columns.
    package_width = max(max(len(item[0]) for item in table_items), 7)
    version_width = max(max(len(item[1]) for item in table_items), 7)

    # Add headers and Python version at top of table.
    table_items = [
        ("Package", "Version"),
        ("-" * package_width, "-" * version_width),
    ] + table_items

    # Build table.
    return "\n".join(
        [
            f"| {name:{package_width}s} | {version_:{version_width}s} |"
            for name, version_ in table_items
        ]
    )


def _get_package_name(module: ModuleType) -> str:
    """
    Get package names from top level module names.

    Parameters
    ----------
    module : ModuleType
        The module name to get package names from.

    Returns
    -------
    str
        The package name.

    Notes
    -----
    packages_distributions returns a map between the top-level module names and package names.
    However, it doesn't understand packages installed in editable mode,
    which are handled in get_package_name.
    """
    _package_names_mapping = packages_distributions()
    if module.__name__ in _package_names_mapping:
        return _package_names_mapping[module.__name__][0]

    # The package is in editable mode: look in pyproject.toml to get the package name.
    with open(
        Path.joinpath(Path(module.__path__[0]).parent, "pyproject.toml"), "rb"
    ) as file:
        config = tomli.load(file)
        return config["tool"]["poetry"]["name"]


def get_package_versions(package_names: list[str]) -> list[tuple[str, str]]:
    """
    Get the package versions for the list of packages provided.

    Parameters
    ----------
    package_names : list[str]
        The list of package names

    Returns
    -------
    list[tuple[str, str]]
        The package name and package version.
    """

    package_versions = [
        (
            _get_package_name(sys.modules[module_name]),
            sys.modules[module_name].__version__,
        )
        for module_name in package_names
        if module_name in sys.modules
    ]
    package_versions = [
        (
            "Python",
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )
    ] + package_versions
    return package_versions
