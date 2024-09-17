from pathlib import Path
from dataclasses import dataclass
from packaging.version import Version
from contextlib import contextmanager

try:
    import snakemake

except ImportError:
    raise ImportError(
        "This library must be called from within a snakemake environment."
    )


# Retain workflow _helper


@dataclass
class Helper:
    snakemake_version = Version(snakemake.__version__)

    def __init__(self, workflow=None):
        self.workflow = workflow
        self.config = workflow.config if workflow else None

    def _check_config(self):
        if self.config is None:
            raise ValueError("Configuration not loaded")

    def _check_workflow(self):
        if self.workflow is None:
            raise ValueError("Workflow not loaded")

    # Utility functions to return the workflow file path

    def _workflow_path(self, path):
        if Helper.snakemake_version < Version("8"):
            return self._workflow_path_snakemake_7(path)
        else:
            return self._workflow_path_snakemake_8(path)

    def _workflow_path_snakemake_7(self, path):
        return snakemake.workflow.srcdir(path)

    def _workflow_path_snakemake_8(self, path):
        return Path(self.workflow.current_basedir) / path

    # Utility functions to return the remote file path

    def _get_remote_file_path(self, path):
        if Helper.snakemake_version < Version("8"):
            return self._get_remote_file_path_snakemake_7(path)
        else:
            return self._get_remote_file_path_snakemake_8(path)

    def _get_remote_file_path_snakemake_7(self, path):
        return snakemake.remote.AUTO.remote(path)

    def _get_remote_file_path_snakemake_8(self, path):
        return self.workflow._storage_registry(path)

    def _get_file_path(self, path):
        return self._workflow_path(path)

    # Utility functions to return a module file path

    def _module_path(self, base, path):
        """Return the path to a module file"""
        folder = f"{base}"
        module_name = self.config.get("output_namespace", None) if self.config else None
        folder += f"/{module_name}" if module_name else ""
        return f"{folder}/{path}"

    # File-type specialisations

    def script(self, relpath):
        """Return the path to a script file"""
        return self._get_file_path(Path("scripts") / relpath)

    def resource(self, relpath):
        """Return the path to a resource file"""
        return self._get_file_path(Path("../resources") / relpath)

    def remote(self, path):
        """Return the path to a remote file"""
        return self._get_remote_file_path(path)

    def input(self, path, port=None):
        """Return the path to an input file

        Args:
            path (str): The path to the input file
            port (str): The name of the input port (optional)
        """
        self._check_config()
        input_namespace = self.config.get("input_namespace", None)
        if isinstance(input_namespace, str):
            if port:
                raise ValueError("Attempting to index a non-indexable input namespace")
            indir = self.config["input_namespace"]
        elif isinstance(input_namespace, dict):
            indir = self.config["input_namespace"].get(port, None)
        else:
            raise ValueError(
                "Snakemake config error - Input namespace type not recognised"
            )
        if not indir:
            raise ValueError("Attempting to read from a non-configured input port")
        if path:
            return f"results/{indir}/{path}"
        else:
            return f"results/{indir}"

    def output(self, path=None):
        """Return the path to an output file"""
        self._check_config()
        outdir = self.config.get("output_namespace", None)
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

    def params(self, *args):
        """Return the value of a parameter in the configuration

        Args:
            *args:  The path to the parameter in the configuration
                    Example: params("foo", "bar") will return the value of
                        config["params"]["foo"]["bar"]
                    If no arguments are provided, return the entire params dictionary
        """
        self._check_config()
        if len(args) == 0:
            return self.config.get("params", {})
        value = self.config.get("params", {})
        for arg in args:
            if not isinstance(value, dict):
                raise ValueError(f"Attempting to index a non-indexable value: {value}")
            if arg not in value:
                raise ValueError(f"Parameter not found: {arg}")
            value = value.get(arg, {})
        return value

    # Alias function - 'params' is the Snakefile directive, but 'param' is more
    # intuitive and consistent with other helper functions.
    def param(self, *args):
        return self.params(*args)


@contextmanager
def grapevne_helper(globals_dict):
    workflow = globals_dict.get("workflow", None)
    gv = Helper(workflow)

    globals_dict["script"] = gv.script
    globals_dict["resource"] = gv.resource
    globals_dict["input"] = gv.input
    globals_dict["output"] = gv.output
    globals_dict["log"] = gv.log
    globals_dict["env"] = gv.env
    globals_dict["param"] = gv.param
    globals_dict["params"] = gv.params

    try:
        yield gv
    finally:
        del globals_dict["script"]
        del globals_dict["resource"]
        del globals_dict["input"]
        del globals_dict["output"]
        del globals_dict["log"]
        del globals_dict["env"]
        del globals_dict["params"]


_helper = Helper()


def init(workflow=None):
    _helper.workflow = workflow
    _helper.config = workflow.config if workflow else None
    _helper.snakemake_version = Version(snakemake.__version__)


def script(relpath):
    """Return the path to a script file"""
    return _helper.script(relpath)


def resource(relpath):
    """Return the path to a resource file"""
    return _helper.resource(relpath)


def remote(path):
    """Return the path to a remote file"""
    return _helper.remote(path)


def input(path, port=None):
    """Return the path to an input file

    Args:
        path (str): The path to the input file
        port (str): The name of the input port (optional)
    """
    return _helper.input(path, port)


def output(path=None):
    """Return the path to an output file"""
    return _helper.output(path)


def log(path=None):
    """Return the path to a log file"""
    return _helper.log(path)


def env(path):
    """Return the path to an environment file"""
    return _helper.env(path)


def benchmark(path=None):
    """Return the path to a benchmark file"""
    return _helper.benchmark(path)


def param(*args):
    return _helper.param(*args)


def params(*args):
    return _helper.params(*args)
