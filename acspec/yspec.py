import glob
import os

from acspec.base import Acspec
from acspec.yml_utils import load_with_node_infos


class Yspec(Acspec):

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
