# -*- coding: utf-8 -*-
import pytest
from types import ModuleType

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType


class BasicModel(Model):

    field = StringType()


class SubModel(BasicModel):

    extended_field = StringType()


class OverrideModel(BasicModel):

    field = StringType(required=True)
    other_field = StringType()


class SubOverrideModel(OverrideModel):

    other_field = StringType(required=True)


class AuthorModel(Model):

    id = StringType()
    first_name = StringType()
    last_name = StringType()


class PostModel(Model):

    id = StringType()
    title = StringType()
    test = StringType()
    tags = ListType(StringType, serialize_when_none=False)
    author = ModelType(AuthorModel, required=True)


class BlogModel(Model):

    posts = ListType(ModelType(PostModel), serialize_when_none=False)


class OtherNonModel(object):
    pass


def dummy_utitily_method():
    pass


@pytest.fixture()
def basic_model(request):
    return BasicModel


@pytest.fixture()
def sub_model(request):
    return SubModel


@pytest.fixture()
def override_model(request):
    return OverrideModel


@pytest.fixture()
def sub_override_model(request):
    return SubOverrideModel


@pytest.fixture()
def blog_module(request):
    module = ModuleType(__name__)

    module.BlogModel = BlogModel
    module.AuthorModel = AuthorModel
    module.PostModel = PostModel

    return module


@pytest.fixture()
def mixed_utitily_module(request):
    module = ModuleType(__name__)

    module.ImportedModel = Model
    module.BasicModel = BasicModel
    module.OtherNonModel = OtherNonModel
    module.dummy_utitily_method = dummy_utitily_method

    return module
