from six import iteritems, add_metaclass

from schematics.types import StringType, BooleanType, BaseType
from schematics.types.compound import ListType

from acspec.schematics_builder.fixes import DictType
from acspec.model import BaseModel

from schematics.models import ModelMeta


REQUIRED_FIELDS = ["type_name", "schematics_type"]


class TypeDescriptorMeta(ModelMeta):

    def __new__(mcs, name, bases, attrs):
        mcs._validate_required_fields(name, bases, attrs)
        return ModelMeta.__new__(mcs, name, bases, attrs)

    @classmethod
    def _validate_required_fields(mcs, name, bases, attrs):
        is_abstract = attrs.get("__abstract_type_descriptor__", False)
        if is_abstract:
            return

        for required_field in REQUIRED_FIELDS:
            if required_field not in attrs and not any(
                hasattr(base, required_field) for base in bases
            ):
                raise TypeError(
                    "{}: Can't define TypeDescriptor without {}.".format(
                        name, required_field
                    ) + " Or make it abstract with" +
                    " __abstract_type_descriptor__ = True"
                )


# We need a superclass for the metaclass:
# else the default Options are not applied
@add_metaclass(TypeDescriptorMeta)
class InternalTypeDescriptor(BaseModel):
    __abstract_type_descriptor__ = True

    @classmethod
    def get_type_name(cls):
        return cls.type_name

    @classmethod
    def has_content_type(cls):
        return False

    def get_requires_context(self):
        return False


class TypeDescriptorBase(InternalTypeDescriptor):
    __abstract_type_descriptor__ = True

    class Options(object):

        serialize_when_none = False

    required = BooleanType()
    default = BaseType()
    serialized_name = StringType()
    deserialize_from = ListType(StringType())
    choices = ListType(BaseType())
    serialize_when_none = BooleanType()
    messages = DictType(StringType())

    def init_schematics_type(self, context=None):
        descriptor_class = self.schematics_type
        kwargs = self.get_descriptor_kwargs()
        return descriptor_class(**kwargs)

    def get_descriptor_kwargs(self):
        primitive = self.to_primitive()
        # may be empty if no raw data is provided
        if primitive is None:
            return {}
        return {
            k: v
            for k, v in iteritems(primitive)
            if k not in self.non_kwarg_keys
        }

    @property
    def non_kwarg_keys(self):
        return {"type"}
