from __future__ import unicode_literals
import inspect

from six import iteritems
from schematics.models import Model
from acspec.utils import underscore
from acspec.dsl import add_option
from acspec.schematics_builder.types.aggregate import (
    ALL_VALID_DISCRIPTOR_OPTIONS, TO_ACSPEC_TYPE
)


def find_model_classes(module):
    classes = []
    for a in [a for a in dir(module) if not a.startswith("_")]:
        definition = getattr(module, a)
        if inspect.isclass(definition) and issubclass(definition, Model):
            if definition.__module__ == module.__name__:
                classes.append(definition)
    return classes


def model_to_spec(model_class, **kwargs):
    spec = {}

    bases = [
        get_short_name(b.__name__) for b in model_class.__bases__
        if b.__name__ not in ["Model", "BaseModel"]
    ]
    if bases:
        add_option(spec, "bases", bases)

    for field_name, field_descriptor in iteritems(model_class._fields):
        spec_with_options = _extract_spec_with_options(
            field_name, field_descriptor, **kwargs
        )
        if spec_with_options:
            spec[field_name] = spec_with_options

    return spec


def get_short_name(name):
    if name.endswith("Model") and name != "Model":
        name = name[:-len("Model")]
    return underscore(name)


def _get_acspec_type(field_descriptor):
    # TODO check subclasses?
    acspec_type_value = TO_ACSPEC_TYPE[field_descriptor.__class__]

    type_spec = {
        "type": acspec_type_value
    }

    if acspec_type_value in ["list", "dict", "model"]:
        if acspec_type_value == "model":
            type_spec[acspec_type_value] = get_short_name(
                field_descriptor.model_class.__name__
            )
        else:
            type_spec[acspec_type_value] = _get_acspec_type(
                field_descriptor.field
            )

    return type_spec


def _extract_spec_with_options(
    field_name, field_descriptor, inheritance="overrides"
):
    spec = _extract_spec(field_name, field_descriptor)

    if inheritance == "false" or not inheritance:
        return spec

    overrides, bases = _traverse_inheritance_tree(
        field_name, field_descriptor.owner_model.__bases__, spec
    )
    if overrides:
        spec[":overrides"] = overrides
    if bases:
        if inheritance == "true" or inheritance is True:
            spec[":bases"] = bases
        elif not overrides:
            # this field is specified in superclases
            return {}

    return spec


def _extract_spec(field_name, field_descriptor):
    spec = _get_acspec_type(field_descriptor)

    for attr in ALL_VALID_DISCRIPTOR_OPTIONS:
        if attr == "messages":
            continue

        if hasattr(field_descriptor, attr):
            value = getattr(field_descriptor, attr)
            if value is not None:
                if attr == "required" and value is False:
                    continue
                spec[attr] = value
    return spec


def _traverse_inheritance_tree(field_name, bases, spec):
    bases_with_field = [b for b in bases if hasattr(b, field_name)]
    bases = {}
    overrides = []
    for base in bases_with_field:
        parent_field_descriptor = getattr(base, field_name)
        parent_spec = _extract_spec(field_name, parent_field_descriptor)
        base_name = get_short_name(base.__name__)

        if spec != parent_spec:
            overrides.append(base_name)
        else:
            parent_overrides, superbases = _traverse_inheritance_tree(
                field_name, base.__bases__, spec
            )
            if parent_overrides:
                superbases[":overrides"] = parent_overrides

            if superbases:
                bases[base_name] = superbases
            else:
                bases[base_name] = "implements"

    return overrides, bases
