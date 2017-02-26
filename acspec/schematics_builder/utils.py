
from acspec.schematics_builder.types.aggregate import ALL_DESCRIPTORS
from acspec.schematics_builder.types.descriptor import find_descriptor
from acspec.schematics_builder.types.compound import (
    CompoundTypeDescriptorBase, ContextTypeDescriptorBase
)


def build_schematics_descriptor(
    data, type_keys={"simple", "list", "dict", "model"},
    descriptors=ALL_DESCRIPTORS
):
    descriptor = find_descriptor(
        data, type_keys=type_keys, descriptors=descriptors
    )
    if issubclass(descriptor, ContextTypeDescriptorBase):
        raise ValueError("Cannot resolve context for model")

    elif issubclass(descriptor, CompoundTypeDescriptorBase):
        nested = build_schematics_descriptor(
            data[descriptor.type_name],
            type_keys=type_keys, descriptors=descriptors
        )
        return descriptor.schematics_type(nested)

    return descriptor.schematics_type()
