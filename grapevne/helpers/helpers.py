import os
import logging
import ensurepip
import subprocess

from urllib.parse import urlparse
from abc import ABC, abstractmethod
from pathlib import Path
from packaging.version import Version
from contextlib import contextmanager
from typing import Union
from grapevne.utils import (
    get_ports,
    get_port_spec,
    get_namespace,
    get_port_namespace,
)

try:
    import snakemake

except ImportError:
    raise ImportError(
        "This library must be called from within a snakemake environment."
    )

_expose_methods = [
    "script",
    "resource",
    "remote",
    "input",
    "output",
    "log",
    "env",
    "benchmark",
    "param",
    "params",
]


class HelperBase(ABC):
    """Abstract Base Class (ABC) for helper functions"""

    def __init__(self, workflow=None):
        self.workflow = workflow
        self.config = workflow.config if workflow else None

    def _check_config(self):
        if self.config is None:
            raise ValueError("Configuration not loaded")

    def _check_workflow(self):
        if self.workflow is None:
            raise ValueError("Workflow not loaded")

    # Utility functions

    @abstractmethod
    def _workflow_path(self, path):
        pass

    @abstractmethod
    def _get_remote_file_path(self, path, provider=None):
        pass

    def _get_provider(self, path):
        parsed = urlparse(path)
        # We need to account for Windows which returns 'C' for 'C:/
        if os.path.isabs(path) or os.path.exists(path) or not parsed.scheme:
            return ""
        return parsed.scheme

    def _get_file_path(self, path):
        path = self._workflow_path(str(path))
        provider = self._get_provider(path)
        if provider:
            return self._get_remote_file_path(path)
        return path

    def _module_path(self, base, path):
        """Return the path to a module file"""
        folder = f"{base}"
        module_name = self._get_namespace()
        folder += f"/{module_name}" if module_name else ""
        return f"{folder}/{path}"

    def _get_port_spec(self, port: Union[str, dict, list, None]):
        return get_port_spec(port)

    def _get_ports(self, config):
        return get_ports(config)

    def _get_port_namespace(self, ports, port_ref):
        return get_port_namespace(ports, port_ref)

    def _get_namespace(self):
        return get_namespace(self.config)

    # File-type specialisations

    def script(self, relpath):
        """Return the path to a script file"""
        return self._get_file_path(Path("scripts") / relpath)

    def resource(self, relpath):
        """Return the path to a resource file"""
        return self._get_file_path(Path("..") / "resources" / relpath)

    def remote(self, path):
        """Return the path to a remote file"""
        return self._get_remote_file_path(str(path))

    def input(self, path=None, port=None):
        """Return the path to an input file

        Args:
            path (str): The path to the input file
            port (str): The name of the input port (optional)
        """
        self._check_config()
        ports = self._get_ports(self.config)
        if len(ports) == 0:
            raise ValueError("No input ports defined in config")
        if port:  # port ref specified
            indir = self._get_port_namespace(ports, port)
        elif len(ports) == 1:
            indir = ports[0]["namespace"]
        else:
            raise Exception(f"Port not specified for input: {path} {port}")
        if path:
            return f"results/{indir}/{path}"
        else:
            return f"results/{indir}"

    def output(self, path=None):
        """Return the path to an output file"""
        self._check_config()
        outdir = self._get_namespace()
        if not outdir:
            raise ValueError("Output namespace not defined in config")
        if path:
            return f"results/{outdir}/{path}"
        else:
            return f"results/{outdir}"

    def log(self, path=None):
        """Return the path to a log file"""
        path = path if path else "log.txt"
        return self._module_path("logs", path)

    def env(self, path):
        """Return the path to an environment file"""
        return f"envs/{path}"

    def benchmark(self, path=None):
        """Return the path to a benchmark file"""
        path = path if path else "benchmark.tsv"
        return self._module_path("benchmarks", path)

    # Parameter indexing

    def params(self, *args, default=None):
        """Return the value of a parameter in the configuration

        Args:
            *args:  The path to the parameter in the configuration
                    Example: params("foo", "bar") will return the value of
                        config["params"]["foo"]["bar"]
                    You can also use the shorthand params("foo.bar"), so long as a
                    unique key "foo.bar" does not already exist.
                    If no arguments are provided, return the entire params dictionary
        """
        self._check_config()
        if len(args) == 0:
            return self.config.get("params", {})
        value = self.config.get("params", {})
        # Check if the argument is a dot-separated string
        if len(args) == 1:
            if args[0] not in value:
                args = args[0].split(".")
        # Iterate through the arguments
        for arg in args:
            if not isinstance(value, dict):
                raise ValueError(f"Attempting to index a non-indexable value: {value}")
            if arg not in value:
                if default is not None:
                    return default
                raise ValueError(f"Parameter not found: {arg}")
            value = value.get(arg, {})
        return value

    # Alias function - 'params' is the Snakefile directive, but 'param' is more
    # intuitive and consistent with other helper functions.
    def param(self, *args, **kwargs):
        return self.params(*args, **kwargs)


class HelperSnakemake7(HelperBase):
    """Helper class for Snakemake 7"""

    def __init__(self, workflow=None):
        super().__init__(workflow)

    # Implementations of abstract methods

    def _workflow_path(self, path):
        return snakemake.workflow.srcdir(path)

    def _get_remote_file_path(self, path, provider=None):
        from snakemake.remote import AUTO

        return next(iter(AUTO.remote(path)))


class HelperSnakemake8(HelperBase):
    """Helper class for Snakemake 8"""

    def __init__(self, workflow=None):
        super().__init__(workflow)

    # Utility functions

    def _install_remote_provider(self, path, provider=None):
        # Determine which storage plugin(s) to install
        if not provider:  # Infer provider if not explicit
            provider = self._get_provider(path)
        install_plugins = []
        if provider in ["http", "https"]:
            install_plugins += ["http"]
        if provider == "s3":
            install_plugins += ["s3"]
        if len(install_plugins) == 0:
            logging.warn(
                f"Provider '{provider}' not recognised - "
                "cannot install storage plugin(s)."
            )
            return
        # Install plugins and register with snakemake
        ensurepip.bootstrap()
        for plugin in install_plugins:
            subprocess.run(
                ["pip", "install", f"snakemake-storage-plugin-{plugin}"], check=True
            )
        # Register the plugins with snakemake
        from snakemake_interface_storage_plugins.registry import (
            StoragePluginRegistry,
        )

        StoragePluginRegistry().collect_plugins()

    # Implementations of abstract methods

    def _workflow_path(self, relpath):
        basedir = str(self.workflow.current_basedir)
        provider = self._get_provider(basedir)
        if provider:
            path = f"{basedir}/{relpath}"
        else:
            path = str(Path(basedir) / relpath)
        return path.replace("workflow/../", "")

    def _get_remote_file_path(self, path, provider=None):
        try:
            return self.workflow.storage_registry(path)
        except snakemake.exceptions.WorkflowError:
            logging.warn(
                "Error loading remote file - "
                "attempting to install provider and retrying."
            )
            self._install_remote_provider(path, provider)
            return self.workflow.storage_registry(path)


class Helper:
    """Wrapper class to handle different versions of snakemake"""

    def __new__(cls, workflow=None):
        snakemake_version = Version(snakemake.__version__)
        if snakemake_version < Version("7"):
            raise ValueError("GRAPEVNE requires snakemake version 7 or higher")
        if snakemake_version < Version("8"):
            return HelperSnakemake7(workflow)
        else:
            return HelperSnakemake8(workflow)


@contextmanager
def grapevne_helper(globals_dict):
    workflow = globals_dict.get("workflow", None)
    gv = Helper(workflow)

    # Expose methods from Helper as method in calling (globals) namespace
    for name in _expose_methods:
        globals_dict[name] = getattr(gv, name)

    try:
        # Yield the Helper object as a context manager
        yield gv
    finally:
        # Clean up the globals namespace
        for name in _expose_methods:
            del globals_dict[name]


_helper = Helper()


def init(workflow=None):
    _helper.workflow = workflow
    _helper.config = workflow.config if workflow else None
