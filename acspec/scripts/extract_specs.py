from __future__ import unicode_literals
import argparse
import inspect
import os
import sys

import yaml
from six import iteritems, string_types
from schematics.models import Model
from acspec.model import MetaFieldDescriptor, TO_ACSPEC_TYPE
from acspec.utils import underscore, mkdir_p
from acspec.dsl import add_option


def _get_short_name(name):
    if name.endswith("Model") and name != "Model":
        name = name[:-len("Model")]
    return underscore(name)


def _get_acspec_type(field_descriptor):
    # TODO check subclasses?
    acspec_type_value = TO_ACSPEC_TYPE[field_descriptor.__class__]
    key = "simple"
    if acspec_type_value in ["list", "dict", "model"]:
        key = acspec_type_value
        if acspec_type_value == "model":
            acspec_type_value = _get_short_name(
                field_descriptor.model_class.__name__
            )
        else:
            acspec_type_value = _get_acspec_type(field_descriptor.field)

    return {
        key: acspec_type_value
    }


def extract_specs():
    parser = argparse.ArgumentParser(
        description='Script to extract the acspec spec from schematis models')
    parser.add_argument('input',
                        help='specify the package or module that contains '
                        'the schematcs models')
    parser.add_argument('-o', '--output',
                        help='specify the output file name (default: STDOUT)',
                        default=sys.stdout)
    parser.add_argument('-d', '--output-directory',
                        help='specify the output directoy to dump every '
                        'model in a separate file')
    parser.add_argument('-n', '--normalize',
                        default=False, action='store_true',
                        help='normalize field names')
    parser.add_argument('-i', '--inheritance',
                        default="overrides",
                        choices=["false", "overrides", "true"],
                        help='deactivate to print :overrides, print inherited '
                        'fields, too')

    args = parser.parse_args()

    root = __import__(args.input)
    module = root
    for level in args.input.split(".")[1:]:
        module = getattr(module, level)

    classes = []
    for a in [a for a in dir(module) if not a.startswith("_")]:
        definition = getattr(module, a)
        if inspect.isclass(definition) and issubclass(definition, Model):
            if definition.__module__ == module.__name__:
                classes.append(definition)

    specs = {}
    for cls in classes:
        model_name = _get_short_name(cls.__name__)
        specs[model_name] = {}
        bases = [
            _get_short_name(b.__name__) for b in cls.__bases__
            if b.__name__ not in ["Model", "BaseModel"]
        ]
        if bases:
            add_option(specs[model_name], "bases", bases)

        for field_name, field_descriptor in iteritems(cls._fields):
            spec_with_options = _extract_spec_with_options(
                field_name, field_descriptor
            )
            if spec_with_options:
                specs[model_name][field_name] = spec_with_options

    if args.output_directory:
        mkdir_p(args.output_directory)
        print("Write output to: {}".format(args.output_directory))

        for model_name, model_spec in iteritems(specs):
            path = os.path.join(args.output_directory, model_name + ".yml")
            stream = open(path, "w")
            yaml.safe_dump(model_spec, stream, default_flow_style=False)
    else:
        stream = args.output
        if isinstance(stream, string_types):
            stream = open(stream, "w")
            print("Write output to: {}".format(args.output))

        yaml.safe_dump(specs, stream, default_flow_style=False)


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
    spec = {
        "type": _get_acspec_type(field_descriptor)
    }

    for attr in MetaFieldDescriptor._fields:
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
        base_name = _get_short_name(base.__name__)

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
