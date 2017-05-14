
from six import iteritems, string_types

from schematics.types import StringType
from schematics.types.compound import PolyModelType
from schematics.exceptions import ValidationError

from acspec.schematics_builder.types.compound import CompoundTypeDescriptorBase


class PolyTypeDescriptor(PolyModelType):

    def __init__(self, type_descriptors, type_descriptor_mixin=None, **kwargs):
        self._type_descriptor_mixin = type_descriptor_mixin
        super(PolyTypeDescriptor, self).__init__(
            self._get_extended_descriptors(type_descriptors), **kwargs
        )
        self._init_compound_type_keys()

    def find_model(self, data):
        return self._find_descriptor_class(data)

    def _find_descriptor_class(self, data):
        descriptors = self.model_classes
        compound_type_keys = self._get_compound_type_keys()

        type_name = None
        if "type" in data:
            type_name = data["type"]
        else:
            type_names = [
                k for k in data
                if k in compound_type_keys
            ]

            if len(type_names) > 1:
                msg = u'Cannot have multiple types: {}'.format(
                    _type_keys_message(type_names, data)
                )
                raise ValidationError(msg)

            elif not type_names:
                msg = u'Missing type for field spec'
                raise ValidationError(msg)

            else:
                type_name = type_names[0]

        if not isinstance(type_name, string_types):
            raise ValidationError(
                "Type name has to be str: {}".format(type_name)
            )

        for model_class in descriptors:
            if model_class.get_type_name() == type_name:
                return model_class

        raise ValidationError("Did not find type {}".format(type_name))

    def _init_compound_type_keys(self):
        self._compound_type_keys = {
            m.get_compound_type_key() for m in self.model_classes
            if issubclass(m, CompoundTypeDescriptorBase)
        }

    def _get_compound_type_keys(self):
        return self._compound_type_keys

    def _append_model_class(self, model_class):
        self.model_classes = tuple(self.model_classes + (model_class,))
        self._init_compound_type_keys()

    def _get_extended_descriptors(self, type_descriptors):
        if not type_descriptors:
            return []

        final_descriptors = []

        # TODO review options to propagate
        nested_type = self.__class__([], required=True)

        for type_descriptor in type_descriptors:
            final_descriptor = self._build_domain_descriptor(
                type_descriptor
            )

            # set references for arbitrary deep nesting
            nested_type._append_model_class(final_descriptor)
            if issubclass(type_descriptor, CompoundTypeDescriptorBase):
                final_descriptor.append_field(
                    type_descriptor.get_compound_type_key(),
                    type_descriptor.get_compound_type(nested_type)
                )

            final_descriptors.append(final_descriptor)

        return final_descriptors

    def _build_domain_descriptor(self, type_descriptor):
        class_name = "Domain{}".format(type_descriptor.__name__)

        type_field = StringType(
            required=True,
            choices=[type_descriptor.type_name],
            default=type_descriptor.type_name,
        )

        if self._type_descriptor_mixin:
            bases = (self._type_descriptor_mixin, type_descriptor)
        else:
            bases = (type_descriptor,)

        TypeDescriptor = type(class_name, bases, {})
        TypeDescriptor.append_field("type", type_field)

        return TypeDescriptor


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
