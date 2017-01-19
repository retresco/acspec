from __future__ import unicode_literals
import argparse
import errno
import os
import sys

import yaml
from six import iteritems, string_types

from acspec.extract.extract import (
    find_model_classes, model_to_spec, get_short_name
)


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

    classes = find_model_classes(module)

    specs = {}
    for cls in classes:
        model_name = get_short_name(cls.__name__)
        specs[model_name] = model_to_spec(cls)

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


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
