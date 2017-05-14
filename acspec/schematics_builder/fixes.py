from six import iteritems

from schematics.exceptions import BaseError, ValidationError
from schematics.transforms import EMPTY_DICT
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
