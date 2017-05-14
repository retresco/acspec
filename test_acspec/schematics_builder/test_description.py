import pytest

import schematics.exceptions
import schematics.types

from acspec.schematics_builder.description import build_description_class
from acspec.schematics_builder.types import simple
from acspec.schematics_builder.types import compound

description_class = build_description_class()


def test_find_descriptor(base_type_input):
    descriptor = description_class.find_descriptor({"type": "string"})
    assert issubclass(descriptor, simple.StringTypeDescriptor)


def test_find_descriptor_finds_by_compound_key(base_type_input):
    descriptor = description_class.find_descriptor({
        "list": {
            "type": "string"
        }
    })
    assert issubclass(descriptor, compound.ListTypeDescriptorBase)

    descriptor = description_class.find_descriptor({
        "dict": {
            "type": "string"
        }
    })
    assert issubclass(descriptor, compound.DictTypeDescriptorBase)

    descriptor = description_class.find_descriptor({
        "model": "test"
    })
    assert issubclass(descriptor, compound.ModelTypeDescriptorBase)


def test_build_schematics_type(base_type_input):
    schematics_type = description_class.build_schematics_type({
        "type": "string"
    })
    assert isinstance(schematics_type, schematics.types.StringType)


def test_build_schematics_type_builds_compound_model(base_type_input):
    schematics_type = description_class.build_schematics_type({
        "list": {
            "type": "string"
        }
    })

    assert isinstance(schematics_type, schematics.types.compound.ListType)

    schematics_type = description_class.build_schematics_type({
        "dict": {
            "type": "string"
        }
    })

    assert isinstance(schematics_type, schematics.types.compound.DictType)


def test_build_schematics_type_raises_for_model_types(base_type_input):
    with pytest.raises(ValueError) as e_info:
        description_class.build_schematics_type({
            "model": "test"
        })

    assert str(e_info.value) == 'Cannot resolve context for model'
