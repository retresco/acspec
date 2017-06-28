
from schematics.models import Model as SchematicsModel
from schematics.models import FieldDescriptor
from schematics.models import metacopy
from schematics.types import BaseType

from acspec.utils import get_all_subclasses


class BaseModel(SchematicsModel):

    @classmethod
    def append_field(cls, name, field):
        if isinstance(field, BaseType):
            # set owner_model like is done by schematics metaclass
            field.owner_model = cls
            field.name = name
            if hasattr(field, 'field'):
                field.field.owner_model = cls

            cls._fields[name] = field

            field_descriptor = FieldDescriptor(name)

            # copy field to subclasses
            subclasses = get_all_subclasses(cls)
            if subclasses:
                for subclass in subclasses:
                    if name not in subclass._fields:
                        subclass._fields[name] = metacopy(field)
                        subclass._fields[name].owner_model = subclass

            # fix not to break the schematics model accidentially
            # TODO make the renaming transparent
            if name == "fields":
                setattr(cls, "_" + name, field_descriptor)
            else:
                setattr(cls, name, field_descriptor)
        else:
            raise TypeError('field must be of type {}'.format(BaseType))


class DontSerializeWhenNoneModel(BaseModel):

    class Options:
        serialize_when_none = False
