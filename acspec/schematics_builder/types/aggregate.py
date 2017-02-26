from acspec.schematics_builder.types.compound import (
    DictTypeDescriptorBase, ListTypeDescriptorBase
)
from acspec.schematics_builder.types.compound import ModelTypeDescriptorBase
from acspec.schematics_builder.types.simple import SIMPLE_DESCRIPTORS

ALL_DESCRIPTORS = SIMPLE_DESCRIPTORS + [
    ModelTypeDescriptorBase, DictTypeDescriptorBase, ListTypeDescriptorBase
]

ALL_VALID_DISCRIPTOR_OPTIONS = []
TO_ACSPEC_TYPE = {}

for descriptor in ALL_DESCRIPTORS:
    schematics_descriptor = descriptor.schematics_type
    if schematics_descriptor not in TO_ACSPEC_TYPE:
        TO_ACSPEC_TYPE[schematics_descriptor] = descriptor.get_type_name()

    for name in descriptor._fields:

        if name not in ["type", "simple", "list", "dict", "model"]:
            if name not in ALL_VALID_DISCRIPTOR_OPTIONS:
                ALL_VALID_DISCRIPTOR_OPTIONS.append(name)
