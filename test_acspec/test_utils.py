import pytest
from collections import OrderedDict

from acspec import utils


def test_topological_iteritems():
    specs = OrderedDict([
        ("subspec", {":bases": ["spec"]}),
        ("superspec", {}),
        ("spec", {":bases": ["superspec"]}),
    ])
    assert list(specs.keys()) == ['subspec', 'superspec', 'spec']

    topological_specs = OrderedDict(utils.topological_iteritems(specs))
    assert list(topological_specs.keys()) == [
        'superspec', 'spec', 'subspec'
    ]


def test_topological_iteritems_cyclic_inheritance():
    specs = {
        "spec": {
            ":bases": ["superspec"]
        },
        "superspec": {
            ":bases": ["subspec"]
        },
        "subspec": {
            ":bases": ["spec"]
        }
    }
    with pytest.raises(ValueError) as excinfo:
        list(utils.topological_iteritems(specs))

    assert str(excinfo.value) == \
        'Cyclic inheritance: spec < superspec < subspec < spec'


def test_underscore():
    assert utils.underscore("test_model") == "test_model"
    assert utils.underscore("TestModel") == "test_model"


def test_camelize():
    assert utils.camelize("TestModel") == "TestModel"
    assert utils.camelize("test_model") == "TestModel"


def test_is_valid_identifier():
    assert utils.is_valid_identifier("") is False
    assert utils.is_valid_identifier("test model") is False
    assert utils.is_valid_identifier("test-model") is False
    assert utils.is_valid_identifier("test_model") is True
    assert utils.is_valid_identifier("TestModel") is True
