import sys
from types import ModuleType

from six import iteritems
from acspec.exceptions import UnresolvedModelError
from acspec.utils import (
    camelize, is_valid_identifier, sanitize_identifier,
    topological_iteritems
)
from acspec.dsl import has_option, get_option, iterspec

from acspec.schematics_builder.builder import SchematicsModelBuilder


class Acspec(object):

    __is_frozen = False

    def __init__(
        self, specs=None, model_builder=None,
        finalize=True, class_mapping=None,
        model_suffix=None, on_invalid_identifier="sanitize"
    ):
        assert on_invalid_identifier in ["sanitize", "skip", "raise"]

        if specs is None:
            specs = {}
        if model_suffix is None:
            model_suffix = "Model"

        if model_builder is None:
            model_builder = SchematicsModelBuilder(
                class_mapping=class_mapping
            )

        self._model_builder = model_builder
        self._raw_specs = {}
        self._models = {}
        self._model_suffix = model_suffix
        self._on_invalid_identifier = on_invalid_identifier
        self.add_specs(specs)
        if finalize:
            self.finalize()

    @property
    def class_mapping(self):
        return self._model_builder.class_mapping

    def add_spec(self, name, spec):
        name = self._get_valid_identifier(name)
        if not name:
            return

        self._validate_not_frozen()
        self._raw_specs[name] = spec

    def add_specs(self, specs):
        self._validate_not_frozen()

        for name, spec in iterspec(specs):
            self.add_spec(name, spec)

    def get_model_class(self, name):
        if name in self._models:
            return self._models[name].model_class
        elif name in self.class_mapping:
            return self.class_mapping[name]
        # raise AcspecContextError(
        #     "Model '{}' not found".format(model_class)
        # )

    def finalize(self, freeze=True):
        self._validate_not_frozen()

        self._build_resolvables()
        self._resolve_references()

        if freeze:
            self.__is_frozen = True

    def itermodelclasses(self, raise_on_unresolved_model=True):
        for v in self._models.values():
            if raise_on_unresolved_model and not v.resolved:
                raise UnresolvedModelError(
                    "{} is not yet resolved".format(v.model_class.__name__)
                )
            yield v.model_class

    def create_or_update_sys_module(self, name="acspecctx"):
        if name in sys.modules:
            ctx = sys.modules[name]
        else:
            ctx = ModuleType(name)

        for model_class in self.itermodelclasses():
            setattr(ctx, model_class.__name__, model_class)
        sys.modules[name] = ctx

    def _get_valid_identifier(self, name):
        assert name, "Please provide a name for your specification"

        if not is_valid_identifier(name):
            if self._on_invalid_identifier == "raise":
                raise ValueError("Invaliid identifier: {}".format(name))
            elif self._on_invalid_identifier == "sanitize":
                return sanitize_identifier(name)
            else:
                return False

        return name

    def _build_resolvables(self):
        pre_emitted = self._model_builder.get_already_defined_bases()
        for name, spec in topological_iteritems(
            self._raw_specs, pre_emitted=pre_emitted
        ):
            if name in self._models:
                # TODO can classes change, should we compare/raise?
                continue
            self._models[name] = self._model_builder.build_resolveable(
                name, spec
            )

    def _resolve_references(self):
        for model_name, v in iteritems(self._models):
            model_class = self._model_builder.resolve_references(v, self)
            setattr(self, model_class.__name__, model_class)

    def _get_model_name(self, name, spec=None):
        if spec and has_option(spec, "name"):
            return get_option(spec, "name")
        return camelize(name) + self._model_suffix

    def _validate_not_frozen(self):
        if self.__is_frozen:
            raise TypeError("{} is a frozen class".format(self))

    def __setattr__(self, key, value):
        self._validate_not_frozen()
        object.__setattr__(self, key, value)
