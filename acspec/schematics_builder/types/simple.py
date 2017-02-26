from schematics.types import BaseType, StringType, NumberType
from schematics.types import URLType, EmailType
from schematics.types import IntType, LongType, FloatType, DecimalType
from schematics.types import DateType, DateTimeType
from schematics.types import BooleanType

from schematics.types.compound import ListType

from acspec.schematics_builder.types.base import TypeDescriptorBase

# for reference, all simple schematics types:
# [
#     'UUIDType', 'IntType', 'EmailType', 'BooleanType', 'DateType',
#     'DecimalType', 'StringType', 'URLType', 'FloatType', 'MD5Type',
#     'NumberType', 'BaseType', 'SHA1Type', 'LongType', 'GeoPointType',
#     'HashType', 'IPv4Type', 'DateTimeType', 'MultilingualStringType'
# ]


class SimpleTypeDescriptorBase(TypeDescriptorBase):
    __abstract_type_descriptor__ = True


class BaseTypeDescriptor(SimpleTypeDescriptorBase):

    type_name = "base"
    schematics_type = BaseType


class StringTypeDescriptor(SimpleTypeDescriptorBase):

    type_name = "string"
    schematics_type = StringType

    regex = StringType()
    max_length = IntType()
    min_length = IntType()


class UrlTypeDescriptor(StringTypeDescriptor):

    type_name = "string"
    schematics_type = URLType

    verify_exists = BooleanType()


class EmailTypeDescriptor(StringTypeDescriptor):

    type_name = "email"
    schematics_type = EmailType


class NumberTypeDescriptor(SimpleTypeDescriptorBase):

    type_name = "number"
    schematics_type = NumberType

    min_value = IntType()
    max_value = IntType()


class IntTypeDescriptor(NumberTypeDescriptor):

    type_name = "integer"
    schematics_type = IntType


class LongTypeDescriptor(NumberTypeDescriptor):

    type_name = "long"
    schematics_type = LongType


class FloatTypeDescriptor(NumberTypeDescriptor):

    type_name = "float"
    schematics_type = FloatType


class DecimalTypeDescriptor(NumberTypeDescriptor):

    type_name = "decimal"
    schematics_type = DecimalType


# TODO add hash types


class BooleanTypeDescriptor(SimpleTypeDescriptorBase):

    type_name = "boolean"
    schematics_type = BooleanType


class DateTypeDescriptor(SimpleTypeDescriptorBase):

    type_name = "date"
    schematics_type = DateType


class DateTimeTypeDescriptor(SimpleTypeDescriptorBase):

    type_name = "date_time"
    schematics_type = DateTimeType

    formats = ListType(StringType)
    serialized_format = StringType()


class TimestampTypeDescriptor(DateTimeTypeDescriptor):

    type_name = "timestamp"
    schematics_type = DateTimeType


SIMPLE_DESCRIPTORS = [
    BaseTypeDescriptor,
    StringTypeDescriptor,
    UrlTypeDescriptor,
    EmailTypeDescriptor,

    NumberTypeDescriptor,
    IntTypeDescriptor,
    LongTypeDescriptor,
    FloatTypeDescriptor,
    DecimalTypeDescriptor,

    BooleanTypeDescriptor,

    DateTypeDescriptor,
    DateTimeTypeDescriptor,
    TimestampTypeDescriptor,
]
