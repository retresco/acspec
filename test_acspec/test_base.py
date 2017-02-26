import pytest
import schematics
from schematics.types import StringType

from acspec.base import Acspec
from acspec.exceptions import MissingBaseClassMappingError
from acspec.model import BaseModel, SchematicsModel


class CustomModel(SchematicsModel):
    pass


@pytest.mark.usefixtures()
class TestAcspec(object):

    def test_should_specify_models_as_subclass_of_base_model(self, acspec):
        assert issubclass(acspec.AuthorModel, BaseModel)
        assert issubclass(acspec.PostModel, BaseModel)
        assert issubclass(acspec.BlogModel, BaseModel)

    def test_should_be_importable(self, acspec):
        acspec.create_or_update_sys_module()
        from acspecctx import BlogModel  # noqa
        from acspecctx import PostModel  # noqa
        from acspecctx import AuthorModel  # noqa

    def test_should_append_to_importables(self, blog_specs, acspec):
        acspec.create_or_update_sys_module()
        from acspecctx import BlogModel  # noqa
        from acspecctx import PostModel  # noqa
        from acspecctx import AuthorModel  # noqa

        with pytest.raises(
            ImportError
        ) as excinfo:
            from acspecctx import ImportErrorModel  # noqa

        assert excinfo.typename == "ImportError"

        blog_specs["import_error"] = {
            "test": {
                "type": {
                    "simple": "string"
                }
            }
        }
        acspec = Acspec(blog_specs)
        acspec.create_or_update_sys_module()

        from acspecctx import ImportErrorModel
        assert hasattr(ImportErrorModel, "test")

    def test_should_iterate_over_model_classes(self, acspec):
        model_classes = list(acspec.itermodelclasses())
        assert set([m.__name__ for m in model_classes]) == \
            set(('AuthorModel', 'BlogModel', 'PostModel'))

    def test_should_deserialize_and_serialize_a_model(
        self, acspec, post_data
    ):
        model = acspec.PostModel(post_data)
        assert model.to_primitive() == post_data

    def test_should_be_inheritable(
        self, acspec, post_data
    ):
        class PostModel(acspec.PostModel):
            custom_field = StringType(required=True)

        post_data["custom_field"] = "test"

        model = PostModel(post_data)
        assert model.to_primitive() == post_data

    def test_should_handle_list_types(
        self, acspec, post_data
    ):
        model = acspec.PostModel(post_data)
        assert model.to_primitive()["tags"] == ["test", "blog"]

    def test_should_handle_dict_types(
        self, blog_specs, post_data
    ):
        blog_specs["blog"]["messages"] = {
            "type": {"dict": {"simple": "string"}}
        }
        acspec = Acspec(blog_specs)
        model = acspec.BlogModel({
            "messages": {
                "test_scope": "test_content"
            }
        })
        assert model.to_primitive()["messages"] == {
            "test_scope": "test_content"
        }

    def test_should_raise_validation_error(
        self, acspec, post_data
    ):
        del post_data["author"]
        model = acspec.PostModel(post_data)

        with pytest.raises(
            schematics.exceptions.ModelValidationError
        ) as excinfo:
            model.validate()

        assert excinfo.value.messages == {
            'author': ['This field is required.']
        }

    def test_should_deserialize_and_serialize_a_nested_model(
        self, acspec, post_data, author_data
    ):
        post_data["author"] = author_data
        model = acspec.PostModel(post_data)

        assert model.to_primitive()["author"] == author_data

    def test_should_define_and_accept_the_whole_blog(
        self, acspec, post_data, author_data
    ):
        post_data["author"] = author_data
        post_data2 = {
            "id": "2",
            "title": "Second post",
            "text": "",
            "author": {
                "id": "2",
                "first_name": "Second",
                "last_name": "Author"
            }
        }

        blog_data = {"posts": [post_data, post_data2]}
        blog = acspec.BlogModel(blog_data)
        blog.validate()

        assert blog.to_primitive() == {"posts": [post_data, post_data2]}


@pytest.mark.usefixtures()
class TestAcspecClassMapping(object):

    def test_specify_superclass(self, basic_specs):
        class_mapping = {
            "custom_model": CustomModel
        }
        basic_specs["basic"][":bases"] = ["custom_model"]
        acspec = Acspec(basic_specs, class_mapping=class_mapping)

        assert hasattr(acspec, "BasicModel")
        assert issubclass(acspec.BasicModel, CustomModel)

    def test_raises_on_missing_superclass(self, basic_specs):
        basic_specs["basic"][":bases"] = ["custom_model"]
        with pytest.raises(MissingBaseClassMappingError) as excinfo:
            Acspec(basic_specs)

        assert str(excinfo.value) == \
            "Please provide a class_mapping for 'custom_model'"

    def test_provice_custom_base(self, basic_specs):
        class_mapping = {
            ":bases": [CustomModel]
        }
        acspec = Acspec(basic_specs, class_mapping=class_mapping)

        assert hasattr(acspec, "BasicModel")
        assert issubclass(acspec.BasicModel, CustomModel)
