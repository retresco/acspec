import os
import pytest

import schematics

from acspec import package_root
from acspec.yspec import Yspec
from acspec.model import BaseModel


class TestYspec(object):

    def test_should_specify_models_from_directory(self):
        acspec = Yspec.load(os.path.join(
            package_root, "test_acspec", "fixtures", "yaml", "blog"
        ))
        assert issubclass(acspec.AuthorModel, BaseModel)
        assert issubclass(acspec.PostModel, BaseModel)
        assert issubclass(acspec.BlogModel, BaseModel)

    def test_should_specify_models_from_file(self):
        acspec = Yspec.load(os.path.join(
            package_root, "test_acspec", "fixtures", "yaml", "multimodel.yml"
        ))
        assert issubclass(acspec.TodoListModel, BaseModel)
        assert issubclass(acspec.TodoModel, BaseModel)

    def test_should_print_file_name_and_line_number_if_available(
        self, model_specs
    ):
        file_path = os.path.join(
            package_root, "test_acspec", "fixtures", "yaml", "invalid"
        )
        with pytest.raises(
            schematics.exceptions.ModelValidationError
        ) as excinfo:
            Yspec.load(file_path)

        assert "test_acspec/fixtures/yaml/invalid/type_mismatch.yml:3" \
            in str(excinfo.value.messages)
        assert (
            "test_acspec/fixtures/"
            "yaml/invalid/type_mismatch.yml:5"
        ) in str(excinfo.value.messages)
