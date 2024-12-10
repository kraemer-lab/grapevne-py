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
from grapevne.helpers.helpers import (
    Helper,
    _helper,
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
        "grapevne.helpers.helpers.HelperBase._get_file_path",
        lambda self, path: Path("workflows") / path,
    ):
        assert script("script.py") == Path("workflows/scripts/script.py")


def test_resource():
    init()
    with mock.patch(
        "grapevne.helpers.helpers.HelperBase._get_file_path",
        lambda self, path: Path("workflows") / path,
    ):
        assert resource("resource.txt") == Path("workflows/../resources/resource.txt")


def test_port_spec_null():
    helper = Helper()
    port = None
    assert helper._port_spec(port) == []


def test_port_spec_str():
    helper = Helper()
    port = "incoming_namespace_1"
    expected_port_spec = [
        {
            "ref": "in",
            "label": "In",
            "namespace": "incoming_namespace_1",
        },
    ]
    assert helper._port_spec(port) == expected_port_spec


def test_port_spec_dict_shorthand():
    helper = Helper()
    port = {
        "port1": "incoming_namespace_1",
        "port2": "incoming_namespace_2",
    }
    expected_port_spec = [
        {
            "ref": "port1",
            "label": "port1",
            "namespace": "incoming_namespace_1",
        },
        {
            "ref": "port2",
            "label": "port2",
            "namespace": "incoming_namespace_2",
        },
    ]
    assert helper._port_spec(port) == expected_port_spec


def test_port_spec_dict():
    helper = Helper()
    port = {
        "ref": "port1",
        "label": "port1",
        "namespace": "incoming_namespace_1",
    }
    expected_port_spec = [
        {
            "ref": "port1",
            "label": "port1",
            "namespace": "incoming_namespace_1",
        },
    ]
    assert helper._port_spec(port) == expected_port_spec


def test_port_spec_list():
    helper = Helper()
    expected_port_spec = [
        {
            "ref": "port1",
            "label": "port1",
            "namespace": "incoming_namespace_1",
        },
        {
            "ref": "port2",
            "label": "port2",
            "namespace": "incoming_namespace_2",
        },
    ]
    assert helper._port_spec(expected_port_spec) == expected_port_spec


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


def test_get_namespace():
    workflow = Workflow(
        {
            "namespace": "namespace1",
        }
    )
    init(workflow)
    assert _helper._get_namespace() == "namespace1"


def test_get_namespace_none():
    workflow = Workflow(
        {
            "no_namespace_given": "namespace1",
        }
    )
    init(workflow)
    assert _helper._get_namespace() is None


def test_get_namespace_legacy():
    """Legacy 'output_namespace' check"""
    workflow = Workflow(
        {
            "output_namespace": "namespace1",
        }
    )
    init(workflow)
    assert _helper._get_namespace() == "namespace1"


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
    # Single value
    assert params("param1") == "value1"
    # Long-form (comma-separated arguments)
    assert params("param2", "param3") == "value3"
    # Short-hand (dot-separated string)
    assert params("param2.param3") == "value3"


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


def test_param_default():
    workflow = Workflow(
        {
            "params": {
                "param1": "value1",
            },
        }
    )
    init(workflow)
    default = "default_value"
    assert param("param2", default=default) == default


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
    # Single value
    assert params("param1") == "value1"
    # Long-form (comma-separated arguments)
    assert params("param2", "param3") == "value3"
    # Short-hand (dot-separated string)
    assert params("param2.param3") == "value3"


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
