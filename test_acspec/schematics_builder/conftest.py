import pytest


@pytest.fixture()
def base_type_input():
    return {}


@pytest.fixture()
def base_options_input():
    return {
        "required": True,
        "default": "Test",
        "serialized_name": "serialized_name_override",
        # TODO This might be very handy to specify transforms here.
        # It would require to map string values to schematics internals
        # "deserialize_from": StringType(),
        "choices": [],
        "serialize_when_none": True,
        "messages": {
            'required': "Overridden message",
        }
    }


@pytest.fixture()
def string_type_input():
    return {
        "regex": r'[a-zA-Z_]*',
        "max_length": 10,
        "min_length": 3,
    }
