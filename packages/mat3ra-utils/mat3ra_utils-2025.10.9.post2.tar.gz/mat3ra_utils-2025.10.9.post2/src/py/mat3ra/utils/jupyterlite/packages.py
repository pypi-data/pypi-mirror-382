import json
import os
import re
import sys
from typing import List

from .enums import EnvironmentsEnum
from .environment import ENVIRONMENT
from .logger import log

if ENVIRONMENT == EnvironmentsEnum.PYODIDE:
    import micropip
elif ENVIRONMENT == EnvironmentsEnum.PYTHON:
    import subprocess


async def install_init():
    if sys.platform == "emscripten":
        import micropip

        for package in ["pyyaml"]:
            await micropip.install(package)


async def install_package_pyodide(pkg: str, verbose: bool = True):
    """
    Install a package in a Pyodide environment.

    Args:
        pkg (str): The name of the package to install.
        verbose (bool): Whether to print the name of the installed package.
    """
    is_url = pkg.startswith("http://") or pkg.startswith("https://") or pkg.startswith("emfs:/")
    are_dependencies_installed = not is_url
    await micropip.install(pkg, deps=are_dependencies_installed)
    pkg_name = pkg.split("/")[-1].split("-")[0] if is_url else pkg.split("==")[0]
    if verbose:
        log(f"Installed {pkg_name}", force_verbose=verbose)


def install_package_python(pkg: str, verbose: bool = True):
    """
    Install a package in a standard Python environment.

    Args:
        pkg (str): The name of the package to install.
        verbose (bool): Whether to print the name of the installed package.
    """
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    if verbose:
        log(f"Installed {pkg}", force_verbose=verbose)


async def install_package(pkg: str, verbose: bool = True):
    """
    Install a package in the current environment.

    Args:
        pkg (str): The name of the package to install.
        verbose (bool): Whether to print the name of the installed package.
    """
    if ENVIRONMENT == EnvironmentsEnum.PYODIDE:
        await install_package_pyodide(pkg, verbose)
    elif ENVIRONMENT == EnvironmentsEnum.PYTHON:
        install_package_python(pkg, verbose)


def get_config_yml_file_path(config_file_path) -> str:
    """
    Get the path to the requirements file.

    Returns:
        str: The path to the requirements file.
    """
    base_path = os.getcwd()
    config_file_full_path = os.path.normpath(os.path.join("/drive/", "./config.yml"))
    if config_file_path != "":
        config_file_full_path = os.path.normpath(os.path.join(base_path, config_file_path))
    return config_file_full_path


def get_packages_list(requirements_dict: dict, notebook_name_pattern: str = "") -> List[str]:
    """
    Get the list of packages to install based on the requirements file.

    Args:
        requirements_dict (dict): The dictionary containing the requirements.
        notebook_name_pattern (str): The pattern of the notebook name.

    Returns:
        List[str]: The list of packages to install.
    """
    packages_default_common = requirements_dict.get("default", {}).get("packages_common", [])
    packages_default_environment_specific = requirements_dict.get("default", {}).get(
        f"packages_{ENVIRONMENT.value}", []
    )

    matching_notebook_requirements_list = [
        cfg for cfg in requirements_dict.get("notebooks", []) if re.search(cfg.get("name"), notebook_name_pattern)
    ]
    packages_notebook_common = []
    packages_notebook_environment_specific = []

    for notebook_requirements in matching_notebook_requirements_list:
        packages_common = notebook_requirements.get("packages_common", [])
        packages_environment_specific = notebook_requirements.get(f"packages_{ENVIRONMENT.value}", [])
        if packages_common:
            packages_notebook_common.extend(packages_common)
        if packages_environment_specific:
            packages_notebook_environment_specific.extend(packages_environment_specific)

    # Note: environment specific packages have to be installed first,
    # because in Pyodide common packages might depend on them
    packages = [
        *packages_default_environment_specific,
        *packages_notebook_environment_specific,
        *packages_default_common,
        *packages_notebook_common,
    ]
    return packages


async def install_packages_with_hashing(packages: List[str], verbose: bool = True):
    """
    Install the packages listed in the requirements file for the notebook with the given name.

    Args:
        notebook_name_pattern (str): The name pattern of the notebook for which to install packages.
        config_file_path (str): The path to the requirements file.
        verbose (bool): Whether to print the names of the installed packages and status of installation.
    """
    # Hash the requirements to avoid re-installing packages
    requirements_hash = str(hash(json.dumps(packages)))
    if os.environ.get("requirements_hash") != requirements_hash:
        for pkg in packages:
            await install_package(pkg, verbose)
        if verbose:
            log("Packages installed successfully.", force_verbose=verbose)
        os.environ["requirements_hash"] = requirements_hash
    else:
        if verbose:
            log("Packages are already installed.", force_verbose=verbose)


async def install_packages(notebook_name_pattern: str, config_file_path: str = "", verbose: bool = True):
    """
    Install the packages listed in the requirements file for the notebook with the given name.

    Args:
        notebook_name_pattern (str): The name pattern of the notebook for which to install packages.
        config_file_path (str): The path to the requirements file.
        verbose (bool): Whether to print the names of the installed packages and status of installation.
    """
    if ENVIRONMENT == EnvironmentsEnum.PYODIDE:
        await install_init()
    # PyYAML has to be installed before being imported in Pyodide and can't appear at the top of the file
    import yaml  # type: ignore[import]

    with open(get_config_yml_file_path(config_file_path), "r") as f:
        requirements_dict = yaml.safe_load(f)
    packages = get_packages_list(requirements_dict, notebook_name_pattern)
    await install_packages_with_hashing(packages, verbose)
