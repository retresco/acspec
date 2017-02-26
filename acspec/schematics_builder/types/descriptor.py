
from six import iteritems

from schematics.types import StringType
from schematics.types.compound import PolyModelType, ModelType
from schematics.exceptions import ValidationError

from acspec.model import BaseModel
from acspec.schematics_builder.types.compound import CompoundTypeDescriptorBase
from acspec.schematics_builder.types.compound import ContextTypeDescriptorBase
from acspec.schematics_builder.types.aggregate import ALL_DESCRIPTORS


def find_descriptor(
    data, type_keys={"simple", "list", "dict", "model"},
    descriptors=ALL_DESCRIPTORS
):
    matched_type_keys = type_keys.intersection(data.keys())

    if len(matched_type_keys) > 1:
        msg = u'Cannot have multiple types: {}'.format(
            _type_keys_message(matched_type_keys, data)
        )

        raise ValidationError(msg)
    if not matched_type_keys or not any([t for t in matched_type_keys]):
        msg = u'Missing one field of {}'.format(", ".join(type_keys))

        raise ValidationError(
            u'Missing one field of {}'.format(", ".join(type_keys))
        )
    type_name = matched_type_keys.pop()

    if type_name == "simple":
        type_name = data["simple"]

    for model_class in descriptors:
        if model_class.get_type_name() == type_name:
            return model_class

    raise ValidationError("Did not find type {}".format(type_name))


class BasePolyTypeDescriptor(PolyModelType):

    def __init__(self, type_descriptors, type_descriptor_mixin=None, **kwargs):
        self._type_descriptor_mixin = type_descriptor_mixin
        super(BasePolyTypeDescriptor, self).__init__(
            self._get_extended_descriptors(type_descriptors), **kwargs
        )

    @property
    def type_keys(self):
        return self.compound_type_keys | {"simple"}

    @property
    def compound_type_keys(self):
        return {"list", "dict", "model"}

    def find_model(self, data):
        return find_descriptor(
            data, descriptors=self.model_classes, type_keys=self.type_keys
        )

    def _append_model_class(self, model_class):
        self.model_classes = tuple(self.model_classes + (model_class,))

    def _get_extended_descriptors(self, type_descriptors, nested_type=None):
        final_descriptors = []

        nested_type = self._build_nested_type(type_descriptors)

        for type_descriptor in type_descriptors:
            final_descriptor = self._build_extended_descriptor(
                type_descriptor, nested_type=nested_type
            )
            if final_descriptor:
                final_descriptors.append(final_descriptor)
        return final_descriptors

    def _build_extended_descriptor(self, type_descriptor, nested_type):
        if self._desciptor_has_content_type(type_descriptor):
            # these are self-referencing initialized in root
            return None

        nested_class_name = "Nested{}".format(type_descriptor.__name__)

        type_field_name, type_field = self._get_type_name_and_field(
            type_descriptor
        )

        TypeDescriptor = self._build_class(nested_class_name, type_descriptor)
        TypeDescriptor.append_field(type_field_name, type_field)
        return TypeDescriptor

    def _build_class(self, class_name, type_descriptor):
        if self._type_descriptor_mixin:
            bases = (self._type_descriptor_mixin, type_descriptor)
        else:
            bases = (type_descriptor,)

        return type(class_name, bases, {})

    def _build_nested_type(self, type_descriptors):
        return None

    def _get_type_name_and_field(self, type_descriptor, nested_type=None):
        if issubclass(type_descriptor, ContextTypeDescriptorBase):
            # Currently, context can only be resolved by string values
            name = type_descriptor.type_name
            type_field = StringType(required=True)

        elif issubclass(type_descriptor, CompoundTypeDescriptorBase):
            assert nested_type, "Compound types require a nested type"

            name = type_descriptor.type_name
            type_field = nested_type

        else:
            name = "simple"
            type_field = StringType(required=True, choices=[
                type_descriptor.type_name
            ])

        return name, type_field

    def _desciptor_has_content_type(self, descriptor):
        if not hasattr(descriptor, "has_content_type"):
            return

        return descriptor.has_content_type()


class PolyTypeDescriptor(BasePolyTypeDescriptor):

    def __init__(self, type_descriptors=ALL_DESCRIPTORS, **kwargs):
        super(PolyTypeDescriptor, self).__init__(
            type_descriptors, **kwargs
        )

    def find_model(self, data):
        if "type" not in data:
            raise ValidationError(
                "Cannot instantiate type descriptor without type field"
            )

        type_ = data["type"]

        return super(PolyTypeDescriptor, self).find_model(type_)

    def _build_extended_descriptor(self, type_descriptor, nested_type):
        if self._desciptor_has_content_type(type_descriptor):
            self._init_content_types(type_descriptor, nested_type)

        root_class_name = "Root{}".format(type_descriptor.__name__)
        inner_class_name = "Inner{}".format(root_class_name)

        type_field_name, type_field = self._get_type_name_and_field(
            type_descriptor, nested_type=nested_type
        )

        # TODO the inner class can be removed after streamlining the DSL
        TypeDescriptor = type(inner_class_name, (BaseModel,), {})
        TypeDescriptor.append_field(type_field_name, type_field)

        RootTypeDescriptor = self._build_class(
            inner_class_name, type_descriptor
        )
        RootTypeDescriptor.append_field("type", ModelType(TypeDescriptor))

        return RootTypeDescriptor

    def _build_nested_type(self, type_descriptors):
        return BasePolyTypeDescriptor(
            type_descriptors, required=True
        )

    def _init_content_types(self, descriptor, nested_type):
        nested_class_name = "Nested{}".format(descriptor.__name__)
        TypeDescriptor = self._build_class(
            nested_class_name, descriptor
        )
        TypeDescriptor.append_field(descriptor.type_name, nested_type)

        # nested type descriptors get appended to them selves for
        # arbitrary deep nesting
        nested_type._append_model_class(TypeDescriptor)


def _type_keys_message(type_keys, data):
    r = []
    node_infos = {}
    for type_key in type_keys:
        if hasattr(data[type_key], 'node_info'):
            node_infos[type_key] = data[type_key].node_info
        r.append(type_key)
    r.sort()
    r = ", ".join(r)
    if node_infos:
        r += " ({})".format([
            "{}: {}:{}".format(
                k, v.start_mark.name, v.start_mark.line
            )
            for k, v in iteritems(node_infos)
        ])
    return r
