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

    def test_should_store_birthday_with_format(self):
        from datetime import datetime

        acspec = Yspec.load(os.path.join(
            package_root, "test_acspec", "fixtures", "yaml", "blog"
        ))
        birthday = datetime(1983, 6, 4)
        author = acspec.AuthorModel({
            "first_name": "Hans",
            "last_name": "Schmidt",
            "birthday": birthday
        })

        assert author.birthday == birthday

        # the format "%Y-%m-%d" strips time information
        author = acspec.AuthorModel({
            "first_name": "Hans",
            "last_name": "Schmidt",
            "birthday": '1983-06-04T00:00:00'
        })
        assert author.birthday == birthday
        assert author.to_primitive()['birthday'] == \
            '1983-06-04T00:00:00.000000'

        with pytest.raises(
            schematics.exceptions.ModelConversionError
        ) as excinfo:
            author = acspec.AuthorModel({
                "first_name": "Hans",
                "last_name": "Schmidt",
                "birthday": 'invalid1983-06-04T00:00:00'
            })

        assert 'birthday' in excinfo.value.messages
        assert len(excinfo.value.messages['birthday']) == 1
        assert excinfo.value.messages['birthday'][0] == \
            'Could not parse invalid1983-06-04T00:00:00. Should be ISO8601.'

    def test_should_specify_models_from_file(self):
        acspec = Yspec.load(os.path.join(
            package_root, "test_acspec", "fixtures", "yaml", "multimodel.yml"
        ))
        assert issubclass(acspec.TodoListModel, BaseModel)
        assert issubclass(acspec.TodoModel, BaseModel)

    def test_source_files(
        self, model_specs
    ):
        yspec = Yspec.load(os.path.join(
            package_root, "test_acspec", "fixtures", "yaml", "blog"
        ))
        files = yspec.source_files
        files.sort()

        assert len(files) == 3
        assert files[0].endswith('test_acspec/fixtures/yaml/blog/author.yml')
        assert files[1].endswith('test_acspec/fixtures/yaml/blog/blog.yml')
        assert files[2].endswith('test_acspec/fixtures/yaml/blog/post.yml')

        yspec = Yspec.load(os.path.join(
            package_root, "test_acspec", "fixtures", "yaml", "multimodel.yml"
        ))
        files = yspec.source_files

        assert len(files) == 1
        assert files[0].endswith('test_acspec/fixtures/yaml/multimodel.yml')

    def test_get_should_print_file_name_and_line_number_if_available(
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
