import pytest
import schematics

from acspec.base import Acspec
from acspec.model import DontSerializeWhenNoneModel
from acspec.model import BaseModel
from .conftest import blog_specs  # noqa


@pytest.mark.usefixtures('blog_specs', 'post_data')
class TestModel(object):

    def test_should_raise_on_multiple_types(self, blog_specs):
        blog_specs['blog']['posts']['type']['simple'] = 'string'

        with pytest.raises(
            schematics.exceptions.ModelValidationError
        ) as excinfo:
            Acspec(blog_specs)

        assert excinfo.value.messages == {
            'type': {'dict': [
                "Cannot have multiple types: list, simple"
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
                "type": {
                    "simple": "string"
                }
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

    def test_should_initialize_polymorphic_models(
        self, polymorphic_contact_specs
    ):
        acspec = Acspec(polymorphic_contact_specs)

        model = acspec.ContactModel({
            "preferred": {
                "street_and_number": "Green Mountain Street 44",
                "city": "Berlin"
            }
        })
        model.validate()
        model = acspec.ContactModel({
            "preferred": {
                "email": "person@his.domain.de"
            }
        })
        model.validate()
        model = acspec.ContactModel({
            "preferred": {
                "telephone": "030123456"
            }
        })
        model.validate()

    def test_should_not_accept_multiple_models(
        self, polymorphic_contact_specs
    ):
        acspec = Acspec(polymorphic_contact_specs)

        with pytest.raises(
            schematics.exceptions.ModelConversionError
        ) as excinfo:
            acspec.ContactModel({
                "preferred": {
                    "street_and_number": "Green Mountain Street 44",
                    "city": "Berlin",
                    "email": "person@his.domain.de"
                }
            })
        # longer matches 'city,street_and_number' have prevalence
        assert excinfo.value.messages == {
            'preferred': {
                'email': 'Rogue field'
            }
        }
