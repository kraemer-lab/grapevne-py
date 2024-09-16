import sys
import ensurepip
import subprocess
import importlib
import logging
from packaging.version import Version
from .version import __version__


def _install_package(package_name: str, version: Version, path: str = ""):
    version_str = version.public
    path = f"{package_name}_v{version_str}"

    ensurepip.bootstrap(upgrade=True)
    args = [
        sys.executable,
        "-m",
        "pip",
        "install",
        f'"{package_name}~={version_str}"',
    ]
    if path:
        args += [
            "-t",
            path,
        ]
    try:
        logging.info(f"Installing {package_name} v{version_str}...")
        logging.debug(f"Running: {' '.join(args)}")
        subprocess.run(*args, check=True)
    except subprocess.CalledProcessError as e:
        logging.warning(f"Global install failed: {e}. Retrying with --user.")
        try:
            subprocess.run([*args, "--user", package_name], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"User install failed: {e}. Exiting.")
            sys.exit(1)


def _get_versioned_module(
    version: Version, module_name: str = "grapevne", path: str = ""
):
    _install_package(module_name, version, path)
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            raise ImportError(f"Failed to load {module_name} from {path}.")
        module = importlib.util.module_from_spec(spec)
    except ImportError as e:
        logging.error(f"Failed to import {module_name}: {e}. Exiting.")
        sys.exit(1)
    return module


def install(version):
    if not version or (isinstance(version, str) and version == "current"):
        # Return the current module
        logging.info("No version requirements specified.")
        return sys.modules[__name__.split(".")[0]]
    required_version = Version(version)
    logging.info(f"Installing grapevne v{required_version}...")
    current_version = Version(__version__)
    logging.info(f"Current version: v{current_version}")
    if current_version < required_version:
        # Install the required version and return the module
        logging.info(f"Installing grapevne v{required_version}...")
        module = _get_versioned_module(required_version)
        return module
    else:
        # Return the current module
        logging.info(f"grapevne v{current_version} is up-to-date.")
        return sys.modules[__name__.split(".")[0]]
