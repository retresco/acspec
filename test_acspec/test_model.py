import pytest
import schematics

from acspec.base import Acspec
from acspec.model import DontSerializeWhenNoneModel
from acspec.model import BaseModel
from .conftest import model_specs  # noqa


@pytest.mark.usefixtures('model_specs', 'post_data')
class TestModel(object):

    def test_should_raise_on_multiple_types(self, model_specs):
        model_specs['blog']['posts']['type']['simple'] = 'string'

        with pytest.raises(
            schematics.exceptions.ModelValidationError
        ) as excinfo:
            Acspec(model_specs)

        assert excinfo.value.messages == {
            'type': {'dict': [
                "Cannot have multiple types: list, simple"
            ]}
        }

    def test_should_use_dont_serialize_when_none_class(self, model_specs):
        model_specs['blog'][':bases'] = ["dont_serialize_when_none"]
        acspec = Acspec(model_specs)
        assert issubclass(acspec.BlogModel, DontSerializeWhenNoneModel)

    def test_should_allow_inheritance_form_other_specs(
        self, model_specs, post_data
    ):
        model_specs['extended_post'] = {
            ':bases': ["post"],
            "subtitle": {
                "type": {
                    "simple": "string"
                }
            }
        }
        acspec = Acspec(model_specs)
        assert issubclass(acspec.ExtendedPostModel, acspec.PostModel)
        post_data["subtitle"] = "Subtitle"
        model = acspec.ExtendedPostModel(post_data)
        model.validate()

    def test_should_allow_to_override_the_implicit_model_name(
        self, model_specs
    ):
        model_specs['post'][':name'] = "SuperPostModel"
        acspec = Acspec(model_specs)
        assert issubclass(acspec.SuperPostModel, BaseModel)
