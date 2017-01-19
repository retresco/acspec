from acspec.extract.extract import find_model_classes, model_to_spec


def test_should_extract_spec(basic_model):
    spec = model_to_spec(basic_model)

    assert "field" in spec
    assert spec["field"] == {'type': {'simple': 'string'}}


def test_should_extract_bases(sub_model):
    spec = model_to_spec(sub_model)

    assert ":bases" in spec
    assert spec[":bases"] == ['basic']


def test_should_not_extract_inherited_fields_by_default(sub_model):
    spec = model_to_spec(sub_model)

    assert "field" not in spec


def test_should_extract_inherited_fields_with_bases(sub_model):
    spec = model_to_spec(sub_model, inheritance=True)

    assert ":bases" in spec["field"]
    assert spec["field"][":bases"] == {'basic': 'implements'}
    assert "field" in spec
    assert spec["field"]["type"] == {'simple': 'string'}


def test_should_exted_inherited_fields_without_bases(sub_model):
    spec = model_to_spec(sub_model, inheritance=False)

    assert ":bases" not in spec["field"]
    assert "field" in spec
    assert spec["field"] == {'type': {'simple': 'string'}}


def test_should_extract_overridden_fields(override_model):
    for inheriance_option in ["overrides", True]:

        spec = model_to_spec(override_model, inheritance=inheriance_option)

        assert ":overrides" in spec["field"]
        assert spec["field"][":overrides"] == ['basic']
        assert "field" in spec
        assert spec["field"]["type"] == {'simple': 'string'}
        assert spec["field"]["required"] is True


def test_should_extract_bases_for_overridden_fields(sub_override_model):
    spec = model_to_spec(sub_override_model, inheritance=True)

    assert "field" in spec
    assert ":overrides" not in spec["field"]
    assert ":bases" in spec["field"]
    # override is the model's name (implied from OverrideModel)
    assert "override" in spec["field"][":bases"]
    assert spec["field"][":bases"]["override"] == {
        ':overrides': ['basic']
    }

    assert "other_field" in spec
    assert ":overrides" in spec["other_field"]
    assert spec["other_field"][":overrides"] == ['override']


def test_should_extract_overridden_fields_with_overrides(override_model):
    spec = model_to_spec(override_model, inheritance=False)

    assert ":bases" not in spec["field"]
    assert ":overrides" not in spec["field"]
    assert "field" in spec
    assert spec["field"] == {
        'type': {'simple': 'string'},
        'required': True
    }
    assert "other_field" in spec


def test_should_find_model_classes(blog_module):
    classes = find_model_classes(blog_module)

    assert len(classes) == 3
    assert blog_module.AuthorModel in classes
    assert blog_module.PostModel in classes
    assert blog_module.BlogModel in classes


def test_should_only_find_model_classes(mixed_utitily_module):
    classes = find_model_classes(mixed_utitily_module)

    assert len(classes) > 0
    assert mixed_utitily_module.dummy_utitily_method not in classes
    assert mixed_utitily_module.ImportedModel not in classes
    assert mixed_utitily_module.OtherNonModel not in classes
    assert mixed_utitily_module.BasicModel in classes


def test_should_resolve_compond_types(blog_module):
    spec = model_to_spec(blog_module.BlogModel, inheritance=False)

    assert "posts" in spec
    assert "type" in spec["posts"]
    assert spec["posts"]["type"] == {'list': {'model': 'post'}}
