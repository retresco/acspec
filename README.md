# Define schematics models by dicts and YAML

Acspec allows you to specify your schematics models with python
dicts or YAML files.


## Basic example:

```python
from acspec.base import Acspec
models = Acspec({
    "todo_list": {
        "todos": {
            "type": "list",
            "list": {
                "type": "string"
            }
        }
    }
})

todo_list = models.TodoListModel({"todos": ["write test", "write library"]})
todo_list.validate()
```

There are simple types, and 3 compound types:

    list, dict and model.

Note, the type, e.g. `"type": "list"`, is optional for compound types but may
be added for consistency.


## Features

#### Simple types and their schematics counterpart:

```python
"base": BaseType
"boolean": BooleanType
"date_time": DateTimeType
"date": DateType
"email": EmailType
"float": FloatType
"integer": IntType
"long": LongType
"string": StringType
"timestamp": DateType
"url": URLType
```

#### Compound types:

```python
"model": ModelType
"list": ListType
"dict": DictType
```


#### Implied model name

The model name is given as lowercase, underscored string and will be converted
to the camelized version plus the "Model"-suffix.
E.g. blog_post => BlogPostModel

You can override the suffix with the model_suffix option.

Model names should be valid python identifiers. If not, they will be sanitized
by default. You can customize this behavior by setting the
`on_invalid_identifier` option to `skip` or `raise`.


#### Schematics options and validations

You can use the schematics options and validations in your specs:

```python
acspec = Acspec({"todo": {
    "title": {
        "type": "string",
        "max_length": 20,
        "min_length": 3,
    }
}})
```


#### Other options

Meta information can be specified with the ":"-prefix, e.g. override the
model's name like this:

```python
acspec = Acspec({"todo": {
    ":name": "MyTodoModel"
    "title": {
        "type": "string"
    }
}})

acspec.MyTodoModel
```


#### Inheritance

The models can inherit from each other

```python
acspec = Acspec(
{
    "base_message": {
        "text": {
            "type": "string"
        }
    },
    "message": {
        ":bases": ["base_message"],
        "title": {
            "type": "string"
        }
    },
})

assert issubclass(acspec.MessageModel, acspec.BaseMessageModel)
```

The models can inherit from models defined somewhere else. To enable acspec to
use and resolve those models, you need to provide a class_mapping:

```python
class_mapping = {
    "base": CustomModel
}

acspec = Acspec(
{
    "test": {
        ":bases": ["base"]
        # your attributes
    }
}, class_mapping=class_mapping)

assert issubclass(acspec.TestModel, CustomModel)
```

As it's a very common case, Acspec ships with the DontSerializeWhenNoneModel,
so you can always:

```python
acspec = Acspec(
{
    "test": {
        ":bases": ["dont_serialize_when_none"]
    }
})
```

#### Model references

The model type enables you to reference/nest other models.

```python
models = Acspec({
    "todo_list": {
        "todos": {
            "type": "list",
            "list": {
                "type": "model",
                "model": "todo"
            }
        }
    },
    "todo": {
        "title": {
            "type": "string"
        }
    }
})

my_todo_list = models.TodoListModel({
    "todos": [
        {"title": "write tests"},
        {"title": "write docs"}
    ]
})
```


#### Update sysmodule and import your models

For prototyping you can use the experimental feature to load the models in
a python module. This way you can import them like any class defined in python.

```python
from acspec.base import Acspec
models = Acspec({
    "todo": {
        "title":{
            "type": "string"
        }
    }
})

# default module name is acspecctx
models.create_or_update_sys_module("todos")

from todos import TodoModel
# and use your model
```


## YAML

Instead of passing a dict to define your spec models, you can also use YAML
from your file system with the Yspec class.

* load a file: create a model from every key on root.
* load a directory: create a model for every file

```python
from acspec.yspec import Yspec
acspec = Yspec.load("path/to/your/yaml/files")
# use your models
```

For more examples see `test_acspec/test_yspec.py`


## Customization

Your models may need custom and helper methods. If inheritance (see above) is
not flexible enough for you, consider assigning the methods afterwards

```python
def get_identifier(self):
    return self.id

acspec.TestModel.get_identifier = get_identifier

```

or extending the model

```python
class TestModel(acspec.TestModel):

    def get_identifier(self):
        return self.id
```


#### Custom DSLs

You may have custom options and handling for your specs and require an
extended input format. The simplest way to achieve this is to provide a
type descriptor mixin with your additional fields or overrides:

```python

class MyTypeDescriptorMixin(Model):

    other_field = StringType()

    @property
    def non_kwarg_keys(self):
        return super().non_kwarg_keys | {"other_field"}

    def init_schematics_type(self, context=None):
        type_class = super(MyTypeDescriptorMixin, self).init_schematics_type(
            context=context
        )
        # extend or customize the schematics field descriptor
        # ...
        return type_class


# Make it strict: raise when encounter an unknown key / rogue field
MyDescriptionClass = build_description_class(
    type_descriptor_mixin=MyTypeDescriptorMixin, strict=True
)


models = Acspec(
    {
        "todo": {
            "title":{
                "type": "string",
                "other_field": "other_value"
            }
        }
    },
    SchematicsModelBuilder(
        description_class=MyDescriptionClass
    )
)
```

Note: Composing the description class is a complex operation. Bear in mind
to initialize your custom description only once.


## Scripts

#### extract_specs

Provide a Python module (must be importable) as parameter and the script will try
to transform the contained Schematics models to acspec YAML files.

Usage:

    env/bin/extract_specs some.module.name
    # will output the specs as YAML. Use -d option for output directory

Example:

    env/bin/extract_specs test_acspec.extract.conftest -d tmp/models


## Developing

All rules that need virtualenv accept a PYTHON variable. If set to 'python3',
`virtualenv -p python3` will be used, else the default.

To set up the environment for python2 and 3:

    make all-platforms


## Test

To run tests with default virtualenv (python2):

    make test

Python3:

    make test PYTHON=python3

All:

    make test-all-platforms

The test rules accept a TEST variable to make it easy to test single files:

    make test-all-platforms TEST=test_acspec/test_model.py
