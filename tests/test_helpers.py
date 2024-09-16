from grapevne.helpers import (
    init,
    script,
    resource,
    input,
    output,
    log,
    env,
    param,
    params,
)
from unittest import mock
from pathlib import Path
import pytest


class Workflow:
    def __init__(self, config):
        self.config = config


def test_script():
    init()
    with mock.patch(
        "grapevne.helpers.helpers.Helper._workflow_path",
        lambda self, path: Path("workflows") / path,
    ):
        assert script("script.py") == Path("workflows/scripts/script.py")


def test_resource():
    init()
    with mock.patch(
        "grapevne.helpers.helpers.Helper._workflow_path",
        lambda self, path: Path("workflows") / path,
    ):
        assert resource("resource.txt") == Path("workflows/../resources/resource.txt")


def test_input_single():
    workflow = Workflow(
        {
            "input_namespace": "in",
        }
    )
    init(workflow)
    assert Path(input("infile.txt")) == Path("results/in/infile.txt")


def test_input_multi():
    workflow = Workflow(
        {
            "input_namespace": {
                "port1": "in1",
                "port2": "in2",
            },
        }
    )
    init(workflow)
    assert Path(input("infile1.txt", "port1")) == Path("results/in1/infile1.txt")
    assert Path(input("infile2.txt", "port2")) == Path("results/in2/infile2.txt")


def test_output():
    workflow = Workflow(
        {
            "output_namespace": "out",
        }
    )
    init(workflow)
    assert Path(output("outfile.txt")) == Path("results/out/outfile.txt")


def test_log():
    init()
    assert log("rule.log") == "logs/rule.log"


def test_env():
    init()
    assert env("conda.yaml") == "envs/conda.yaml"


def test_param():
    workflow = Workflow(
        {
            "params": {
                "param1": "value1",
                "param2": {
                    "param3": "value3",
                },
            },
        }
    )
    init(workflow)
    assert param("param1") == "value1"
    assert param("param2", "param3") == "value3"


def test_param_notfound():
    workflow = Workflow(
        {
            "params": {
                "param1": "value1",
            },
        }
    )
    init(workflow)
    with pytest.raises(ValueError):
        param("param2")


def test_params():
    workflow = Workflow(
        {
            "params": {
                "param1": "value1",
                "param2": {
                    "param3": "value3",
                },
            },
        }
    )
    init(workflow)
    assert params("param1") == "value1"
    assert params("param2", "param3") == "value3"


def test_params_notfound():
    workflow = Workflow(
        {
            "params": {
                "param1": "value1",
            },
        }
    )
    init(workflow)
    with pytest.raises(ValueError):
        params("param2")
