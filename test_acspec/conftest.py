# -*- coding: utf-8 -*-
import pytest


@pytest.fixture()
def basic_specs(request):
    return {
        "basic": {
            "field": {
                "type": "string"
            }
        }
    }


@pytest.fixture()
def invalid_model_name_specs(request):
    return {
        "$%&to-be-sanitized": {
            "field": {
                "type": "string"
            }
        }
    }


@pytest.fixture()
def blog_specs(request):
    return {
        "blog": {
            "posts": {
                "list": {
                    "type": "model",
                    "model": "post"
                }
            }
        },
        "author": {
            "id": {
                "type": "string"
            },
            "first_name": {
                "type": "string"
            },
            "last_name": {
                "type": "string"
            }
        },
        "post": {
            "id": {
                "type": "string"
            },
            "title": {
                "type": "string"
            },
            "text": {
                "type": "string"
            },
            "tags": {
                "type": "list",
                "list": {
                    "type": "string"
                },
                "serialize_when_none": False,
            },
            "author": {
                "type": "model",
                "model": "author",
                "serialize_when_none": False,
                "required": True
            }
        }
    }


@pytest.fixture()
def acspec(request):
    from acspec.base import Acspec
    return Acspec(blog_specs(request))


@pytest.fixture()
def author_data(request):
    return {
        "id": "1",
        "first_name": "John",
        "last_name": "Smith"
    }


@pytest.fixture()
def post_data(request):
    return {
        "id": "123",
        "title": "TestPost",
        "text": "TestText",
        "tags": ["test", "blog"],
        "author": author_data(request)
    }
