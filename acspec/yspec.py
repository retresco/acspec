import glob
import os

from schematics.exceptions import BaseError

from acspec.base import Acspec
from acspec.model import ResolvableFactory
from acspec.yml_utils import load_with_node_infos


def transform_messages(name, messages):
    if hasattr(name, "node_info"):
        node_info = name.node_info
        key = "{}:{}:{}".format(
            node_info.start_mark.name, node_info.start_mark.line, name
        )
        messages = {
            key: messages
        }
    return messages


class YamlResolvableFactory(ResolvableFactory):
    def _get_field_descriptor(self, name, constraints):
        try:
            return super(YamlResolvableFactory, self)._get_field_descriptor(
                name, constraints
            )
        except BaseError as e:
            raise e.__class__(transform_messages(name, e.messages))


class Yspec(Acspec):

    def __init__(self, *args, **kwargs):
        if "resolvable_factory" not in kwargs:
            kwargs["resolvable_factory"] = YamlResolvableFactory
        super(Yspec, self).__init__(*args, **kwargs)

    def load_spec(self, spec_path):
        name = os.path.splitext(os.path.basename(spec_path))[0]
        with open(spec_path) as f:
            self.add_spec(name, load_with_node_infos(f))

    def load_specs(self, specs_path):
        with open(specs_path) as f:
            self.add_specs(load_with_node_infos(f))

    @property
    def source_files(self):
        files = []
        for key, raw_spec in self._raw_specs.items():
            if hasattr(raw_spec, 'node_info'):
                file_name = raw_spec.node_info.start_mark.name
                if file_name not in files:
                    files.append(file_name)
        return files

    @classmethod
    def load(cls, path, finalize=True, **kwargs):
        path = os.path.normpath(path)
        acspec = cls(finalize=False, **kwargs)

        if os.path.isdir(path):
            files = glob.glob(os.path.join(path, '*.yml'))
            for file_path in files:
                acspec.load_spec(file_path)
        else:
            acspec.load_specs(path)

        if finalize is True:
            acspec.finalize()
        return acspec
