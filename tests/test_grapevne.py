import sys
import pytest
import grapevne


def test_install_none():
    grapevne_helpers = grapevne.install(version=None)
    root_module = sys.modules[grapevne_helpers.__name__.split(".")[0]]
    assert root_module.__version__ == grapevne.__version__


def test_install_current():
    grapevne_helpers = grapevne.install(version="current")
    root_module = sys.modules[grapevne_helpers.__name__.split(".")[0]]
    assert root_module.__version__ == grapevne.__version__


def test_install_this_version():
    version = grapevne.__version__
    grapevne_helpers = grapevne.install(version=version)
    root_module = sys.modules[grapevne_helpers.__name__.split(".")[0]]
    assert root_module.__version__ == version


def test_install_nonsense():
    version = "nonsense"
    with pytest.raises(ValueError):
        grapevne.install(version=version)
