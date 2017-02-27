from acspec.dsl import iterspec, remove_option_prefix

from acspec.utils import camelize

from acspec.model import DontSerializeWhenNoneModel
from acspec.schematics_builder.description import build_description_class
from acspec.schematics_builder.types.aggregate import ALL_DESCRIPTORS

DEFAULT_DESCRIPTION = build_description_class(
    type_descriptors=ALL_DESCRIPTORS
)

DEFAULT_MAPPING = {
    "dont_serialize_when_none": DontSerializeWhenNoneModel
}


class ResolveableModel(object):

    def __init__(self, model_class, model_description):
        self.model_class = model_class
        self.model_description = model_description
        self.resolved = False

    def resolve(self, context, class_mapping):
        self.resolved = True
        self.model_description.resolve_references(
            self.model_class, context, class_mapping
        )
        return self.model_class


class SchematicsModelBuilder():

    name = "schematics"

    def __init__(
        self,
        model_suffix="Model",
        class_mapping=None,
        description_class=None
    ):
        self._class_mapping = DEFAULT_MAPPING.copy()
        if class_mapping:
            self._class_mapping.update(class_mapping)
        self._model_suffix = model_suffix

        if description_class is None:
            description_class = DEFAULT_DESCRIPTION
        self._description_class = description_class

    @property
    def class_mapping(self):
        return self._class_mapping

    @property
    def description_class(self):
        return self._description_class

    def get_already_defined_bases(self):
        return list(self.class_mapping.keys())

    def build_resolveable(self, name, spec):
        model_description = self._build_model_description(name, spec)
        model_description.validate()

        model_class = model_description.build_model_class(self.class_mapping)

        self.class_mapping[name] = model_class

        return ResolveableModel(model_class, model_description)

    def resolve_references(self, resolveable, context):
        model_class = resolveable.resolve(context, self.class_mapping)
        return model_class

    def resolve_and_update_context(self, resolveable, context):
        model_class = resolveable.resolve(context, self.class_mapping)

        return model_class

    def _build_model_description(self, name, spec, **kw):
        options = {
            "key": name,
            "name": self._get_default_model_name(name)
        }
        field_descriptors = {}

        for name, spec, is_option in iterspec(spec, with_options=True):
            if is_option:

                options[remove_option_prefix(name)] = spec
            else:
                field_descriptors[name] = spec

        return self.description_class({
            "options": options,
            "field_descriptors": field_descriptors
        }, **kw)

    def _get_default_model_name(self, name):
        return camelize(name) + self._model_suffix
