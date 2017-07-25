import sys
import datetime

from six import iteritems

from schematics.exceptions import BaseError, ValidationError, ConversionError
from schematics.transforms import EMPTY_DICT
from schematics.types import DateTimeType as SchematicDateTimeType
from schematics.types.compound import DictType as SchematicDictType


class DictType(SchematicDictType):
    """
    The schematics version does not wrap to_native validation errors to their
    key and they cannot be recovered.

    This class nests items conversion and validation errors in their key.
    """

    def to_native(self, value, safe=False, context=None):
        if value == EMPTY_DICT:
            value = {}

        value = value or {}

        if not isinstance(value, dict):
            raise ValidationError(
                u'Only dictionaries may be used in a DictType'
            )

        result = {}
        errors = {}

        for key, v in iteritems(value):
            try:
                result[self.coerce_key(key)] = self.field.to_native(
                    v, context
                )
            except BaseError as exc:
                errors[key] = exc

        if errors:
            raise ValidationError(errors)

        return result


class DateTimeType(SchematicDateTimeType):
    """
    Let's be nice and support iso8601.

    Note, Python does not yet support full iso8601. So we fix it.

    See http://bugs.python.org/issue15873
    """

    DEFAULT_FORMATS = (
        '%Y-%m-%dT%H:%M:%S.%f',  '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%f%z'
    )

    def to_native(self, value, context=None):
        if isinstance(value, datetime.datetime):
            return value

        for fmt in self.formats:
            try:
                return datetime.datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue

        # as last ressort, try https://stackoverflow.com/a/13182163/1029655
        if (
            len(value) > 2 and value[-3] == ":" and
            '%Y-%m-%dT%H:%M:%S.%f%z' in self.formats
        ):
            try:
                return datetime.datetime.strptime(
                    ''.join(value.rsplit(':', 1)), '%Y-%m-%dT%H:%M:%S.%f%z'
                )
            except (ValueError, TypeError):
                pass

        if self.formats == self.DEFAULT_FORMATS:
            message = self.messages['parse'].format(value)
        else:
            message = self.messages['parse_formats'].format(
                value, ", ".join(self.formats)
            )
        raise ConversionError(message)
