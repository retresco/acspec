import pytest
import schematics

from acspec.base import Acspec
from acspec.model import DontSerializeWhenNoneModel
from acspec.model import BaseModel
from .conftest import blog_specs  # noqa


@pytest.mark.usefixtures('blog_specs', 'post_data')
class TestModel(object):

    def test_should_raise_on_multiple_types(self, blog_specs):
        # add dict, so it contains conflicting list and dict compound types
        blog_specs['blog']['posts']['dict'] = {'type': 'string'}

        with pytest.raises(
            schematics.exceptions.ModelConversionError

        ) as excinfo:
            Acspec(blog_specs)

        assert excinfo.value.messages == {
            'field_descriptors': {'posts': [
                'Cannot have multiple types: dict, list'
            ]}
        }

    def test_should_use_dont_serialize_when_none_class(self, blog_specs):
        blog_specs['blog'][':bases'] = ["dont_serialize_when_none"]
        acspec = Acspec(blog_specs)
        assert issubclass(acspec.BlogModel, DontSerializeWhenNoneModel)

    def test_should_allow_inheritance_form_other_specs(
        self, blog_specs, post_data
    ):
        blog_specs['extended_post'] = {
            ':bases': ["post"],
            "subtitle": {
                "type": "string"
            }
        }
        acspec = Acspec(blog_specs)
        assert issubclass(acspec.ExtendedPostModel, acspec.PostModel)
        post_data["subtitle"] = "Subtitle"
        model = acspec.ExtendedPostModel(post_data)
        model.validate()

    def test_should_allow_to_override_the_implicit_model_name(
        self, blog_specs
    ):
        blog_specs['post'][':name'] = "SuperPostModel"
        acspec = Acspec(blog_specs)
        assert issubclass(acspec.SuperPostModel, BaseModel)
