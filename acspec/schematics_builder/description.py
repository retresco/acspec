from six import iteritems

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ListType
from schematics.types.compound import ModelType

from acspec.dsl import get_option, has_option
from acspec.exceptions import MissingBaseClassMappingError
from acspec.model import BaseModel
from acspec.schematics_builder.fixes import DictType
from acspec.schematics_builder.types.descriptor import PolyTypeDescriptor


def build_description_class(
    type_descriptors, type_descriptor_mixin=None, strict=False
):

    class CustomSchematicsModelDescription(SchematicsModelDescription):

        field_descriptors = DictType(PolyTypeDescriptor(
            type_descriptors=type_descriptors,
            type_descriptor_mixin=type_descriptor_mixin,
            strict=strict
        ))

    return CustomSchematicsModelDescription


class ModelOptions(Model):

    key = StringType(required=True)
    name = StringType(required=True)
    model_suffix = StringType(default="Model")
    bases = ListType(StringType, default=[])


class SchematicsModelDescription(Model):

    options = ModelType(ModelOptions)
    field_descriptors = DictType(PolyTypeDescriptor(strict=False))

    def __init__(self, *args, **kwargs):
        self.base_model = kwargs.pop("base_model", BaseModel)
        super(SchematicsModelDescription, self).__init__(*args, **kwargs)

    @property
    def model_name(self):
        return self.options.name

    def build_model_class(self, class_mapping):
        bases = self._find_base_classes(class_mapping)
        model_class = type(str(self.model_name), bases, {})

        for name, field_descriptor in iteritems(
            self.field_descriptors
        ):
            if field_descriptor.get_requires_context():
                # is resolved later
                pass
            else:
                model_class.append_field(
                    name,
                    field_descriptor.init_schematics_type()
                )

        return model_class

    def resolve_references(self, model_class, context, class_mapping):
        for name, field_descriptor in iteritems(
            self.field_descriptors
        ):

            if field_descriptor.get_requires_context():
                model_class.append_field(
                    name,
                    field_descriptor.init_schematics_type(
                        context=context
                    )
                )
            else:
                # already initialized
                pass

        return model_class

    def _find_base_classes(self, class_mapping):
        r = []
        for base in self.options.bases:
            if base in class_mapping:
                r.append(class_mapping[base])
            else:
                raise MissingBaseClassMappingError(
                    "Please provide a class_mapping for '{}'".format(base)
                )

        # TODO: how to provide additional mappings for a model name?
        # Note: the next lines conflict if models inherit from each other
        # if name in class_mapping:
        #     r.append(class_mapping[name])

        if has_option(class_mapping, "bases"):
            r += get_option(class_mapping, "bases")

        if not any([isinstance(base, self.base_model) for base in r]):
            r.append(self.base_model)

        return tuple(r)
