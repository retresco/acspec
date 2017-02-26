import pytest

import schematics.exceptions
from acspec.schematics_builder.types import simple


def test_base_type(base_type_input):
    descriptor = simple.BaseTypeDescriptor
    field_descriptor = descriptor(
        base_type_input
    ).init_schematics_type()

    data = {"test": "data"}
    field_descriptor.validate(data)

    native_data = field_descriptor.to_native(data)
    assert native_data == data


def test_base_type_required(base_type_input):
    descriptor = simple.BaseTypeDescriptor
    base_type_input["required"] = True
    field_descriptor = descriptor(
        base_type_input
    ).init_schematics_type()

    data = None
    with pytest.raises(schematics.exceptions.ValidationError) as e_info:
        field_descriptor.validate(data)

    assert e_info.value.messages == [
        'This field is required.'
    ]


def test_base_type_choices(base_type_input):
    descriptor = simple.BaseTypeDescriptor
    base_type_input["choices"] = ["right text"]
    field_descriptor = descriptor(
        base_type_input
    ).init_schematics_type()

    data = "wrong text"
    with pytest.raises(schematics.exceptions.ValidationError) as e_info:
        field_descriptor.validate(data)

    assert e_info.value.messages == [
        "Value must be one of ['right text']."
    ]


def test_base_custom_message(base_type_input):
    descriptor = simple.BaseTypeDescriptor
    base_type_input["required"] = True
    base_type_input["messages"] = {
        "required": "custom text"
    }
    field_descriptor = descriptor(
        base_type_input
    ).init_schematics_type()

    data = None
    with pytest.raises(schematics.exceptions.ValidationError) as e_info:
        field_descriptor.validate(data)

    assert e_info.value.messages == [
        'custom text'
    ]
