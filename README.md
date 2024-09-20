# grapevne-py

Designed for use with [GRAPEVNE](https://github.com/kraemer-lab/GRAPEVNE), the Graphical Analytical Pipeline Development Environment - an interactive environment for building and validating data processing workflows, built around the Snakemake workflow manager.

grapevne-py is a python library for grapevne snakemake support. It provides a set of classes and functions to help you build and validate snakemake modules that are compatible with GRAPEVNE. By using grapevne-py, you can easily create snakemake modules that can be imported into GRAPEVNE and used to build complex data processing workflows.

See [GRAPEVNE](https://grapevne.readthedocs.io/en/latest/?badge=latest) for more information about these tools.

## Installation

Each GRAPEVNE module employing grapevne-py will include a `grapevne_helper.py` file that installs the latest version of grapevne-py. To install the package manually you can use pip, or another package manager of your choice:

```bash
pip install grapevne-py
```

## Usage

grapevne-py provides a set of classes and functions that you can use to build snakemake modules that can be interconnected with one another via GRAPEVNE. Here's an example of how you might use grapevne-py to build a simple snakemake module:

```python
from grapevne_helper import import_grapevne
gv = import_grapevne(workflow)

rule all:
    input:
        src = gv.input("input.txt"),
    output
        target = gv.output("output.txt"),
    shell:
        "cp {input.src} {output.target}"
```

grapevne-py uses a helper function that is bundled with each module to bootstrap the latest version of grapevne-py. Once imported the wrapper functions that we will use are available through the `gv` object. In this example we simply copy an input file to an output. Note that the `gv.input` and `gv.output` wrapper functions are used to allow GRAPEVNE to redirect the input and output file paths as required (as-well as providing a number of other benefits, such as automatic remote file support and Snakemake version compatibility checks). There are a number of other wrapper available, outlined below.

In the next example we will use several more wrappers including `script`, `resource`, `log` and the `params` wrapper to access parameters passed to the module from the configuration file. For convenience, we will expose all wrappers to the global namespace, allowing us to write `output(params("Filename"))` instead of `gv.output(gv.params("Filename"))`.  This module assumes a configuration file that contains a `Filename` parameter along with a `script.sh` script and `payload.txt` resource file that is bundled with the module.

```python
configfile: "config/config.yaml"
from grapevne_helper import import_grapevne

grapevne = import_grapevne(workflow)
globals.update(vars(grapevne))

rule all:
    input:
        script = script("script.sh"),
        payload = resource("payload.txt")),
    output:
        target = output(params("Filename")),
    log:
        log("log.txt"),
    shell:
        "{input.script} {input.payload} {output.target}"
```


## Wrappers

Most wrappers take a single `path` argument and redirect that file path as required by GRAPEVNE:
- `output()` - Wrapper for output file paths
- `script()` - Wrapper for scripts that are executed by the workflow (shell, python, R, etc.)
- `resource()` - Wrapper for resource files (payload items) that are provided by the module
- `remote()` - Wrapper for remote files (http, s3, etc.)
- `log()` - Wrapper for log file paths (manages location, which is useful in larger workflows)
- `env()` - Wrapper for environment file paths
- `benchmark()` - Wrapper for benchmark file paths

There are also several wrappers that take multiple inputs:

- `input(path, port=None)`
  
  Wrapper for input file paths. When input ports are unnamed (see [GRAPEVNE documentation](https://grapevne.readthedocs.io/en/latest/?badge=latest)) then the `input` wrapper can be used without specifying a port, e.g. `input("input.txt")`.

  When multiple input ports are available, or the input port is named, then the wrapper should be used with a port specifier, e.g. `input("input.txt", "port1")`.

- `param(*args)`

  References parameters in the configuration file. For example - assume the following parameters:

    ```yaml
    Filename: "input.txt"
    Triggers:
        Start: "2022-01-01"
        End: "2022-12-31"
    ```

    We would access the `Filename` parameter as `params("Filename")` and the `Triggers` parameter as `params("Triggers")`. To access the `Start` parameter we would use `params("Triggers", "Start")`, or `params("Triggers.Start")` as shorthand.

- `params(*args)`

  Redirects to `param(*args)`.
