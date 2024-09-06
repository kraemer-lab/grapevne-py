from grapevne.helpers import init, script, resource, input, output, log, env, params
from unittest import mock
from pathlib import Path
import pytest


def test_script():
    init(None, None)
    with mock.patch(
        "grapevne.helpers.helpers.Helper._workflow_path",
        lambda self, path: Path("workflows") / path,
    ):
        assert script("script.py") == Path("workflows/scripts/script.py")


def test_resource():
    init(None, None)
    with mock.patch(
        "grapevne.helpers.helpers.Helper._workflow_path",
        lambda self, path: Path("workflows") / path,
    ):
        assert resource("resource.txt") == Path("workflows/../resources/resource.txt")


def test_input_single():
    config = {
        "input_namespace": "in",
    }
    init(None, config)
    assert Path(input("infile.txt")) == Path("results/in/infile.txt")


def test_input_multi():
    config = {
        "input_namespace": {
            "port1": "in1",
            "port2": "in2",
        },
    }
    init(None, config)
    assert Path(input("infile1.txt", "port1")) == Path("results/in1/infile1.txt")
    assert Path(input("infile2.txt", "port2")) == Path("results/in2/infile2.txt")


def test_output():
    config = {
        "output_namespace": "out",
    }
    init(None, config)
    assert Path(output("outfile.txt")) == Path("results/out/outfile.txt")


def test_log():
    init(None, None)
    assert log("rule.log") == "logs/rule.log"


def test_env():
    init(None, None)
    assert env("conda.yaml") == "envs/conda.yaml"


def test_params():
    config = {
        "params": {
            "param1": "value1",
            "param2": {
                "param3": "value3",
            },
        },
    }
    init(None, config)
    assert params("param1") == "value1"
    assert params("param2", "param3") == "value3"


def test_params_notfound():
    config = {
        "params": {
            "param1": "value1",
        },
    }
    init(None, config)
    with pytest.raises(ValueError):
        params("param2")
