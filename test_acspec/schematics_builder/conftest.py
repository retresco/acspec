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

#
# class UrlTypeDescriptor(StringTypeDescriptor):
#
#     type_name = "string"
#     schematics_field_descriptor = URLType
#
#     verify_exists = BooleanType()
#
#
# class EmailTypeDescriptor(StringTypeDescriptor):
#
#     type_name = "email"
#     schematics_field_descriptor = EmailType
#
#
# class NumberTypeDescriptor(TypeDescriptorBase):
#
#     type_name = "number"
#     schematics_field_descriptor = NumberType
#
#     min_value = IntType()
#     max_value = IntType()
#
#
# class IntTypeDescriptor(NumberTypeDescriptor):
#
#     type_name = "integer"
#     schematics_field_descriptor = IntType
#
#
# class LongTypeDescriptor(NumberTypeDescriptor):
#
#     type_name = "long"
#     schematics_field_descriptor = LongType
#
#
# class FloatTypeDescriptor(NumberTypeDescriptor):
#
#     type_name = "float"
#     schematics_field_descriptor = FloatType
#
#
# class DecimalTypeDescriptor(NumberTypeDescriptor):
#
#     type_name = "decimal"
#     schematics_field_descriptor = DecimalType
#
#
# # TODO add hash types
#
#
# class BooleanTypeDescriptor(TypeDescriptorBase):
#
#     type_name = "boolean"
#     schematics_field_descriptor = BooleanType
#
#
# class DateTypeDescriptor(TypeDescriptorBase):
#
#     type_name = "date"
#     schematics_field_descriptor = DateType
#
#
# class DateTimeTypeDescriptor(TypeDescriptorBase):
#
#     type_name = "date_time"
#     schematics_field_descriptor = DateTimeType
#
#     formats = ListType(StringType)
#     serialized_format = StringType()
#
#
# class TimestampTypeDescriptor(DateTimeTypeDescriptor):
#
#     type_name = "timestamp"
#     schematics_field_descriptor = DateTimeType
