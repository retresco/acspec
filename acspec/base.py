import sys
from types import ModuleType

from six import iteritems
from acspec.exceptions import UnresolvedModelError
from acspec.model import ResolvableFactory
from acspec.model import DEFAULT_MAPPINGS
from acspec.utils import camelize, is_valid_identifier, topological_iteritems
from acspec.dsl import has_option, get_option, iterspec


class Acspec(object):

    __is_frozen = False

    def __init__(
        self, specs=None, resolvable_factory=ResolvableFactory,
        finalize=True, class_mapping=None,
        model_suffix=None
    ):
        if specs is None:
            specs = {}
        if model_suffix is None:
            model_suffix = "Model"

        self._class_mapping = DEFAULT_MAPPINGS.copy()
        if class_mapping:
            self._class_mapping.update(class_mapping)

        self._resolvable_factory = resolvable_factory(
            class_mapping=self._class_mapping
        )
        self._raw_specs = {}
        self._models = {}
        self._model_suffix = model_suffix
        self.add_specs(specs)
        if finalize:
            self.finalize()

    def add_spec(self, name, spec):
        if not is_valid_identifier(name):
            return
        self._validate_not_frozen()
        self._raw_specs[name] = spec

    def add_specs(self, specs):
        self._validate_not_frozen()

        for name, spec in iterspec(specs):
            self.add_spec(name, spec)

    def get_resolvable(self, name):
        return self._models[name]

    def get_model_class(self, name):
        if name in self._models:
            return self._models[name].model_class
        elif name in self._class_mapping:
            return self._class_mapping[name]
        # raise AcspecContextError(
        #     "Model '{}' not found".format(model_class)
        # )

    def _resolve_classes(self):
        pre_emitted = self._get_known_bases()
        for name, spec in topological_iteritems(
            self._raw_specs, pre_emitted=pre_emitted
        ):
            if name in self._models:
                # TODO can classes change, should we compare/raise?
                continue
            model_name = self._get_model_name(name, spec=spec)
            self._models[name] = self._resolvable_factory.get_resolvable(
                model_name, spec
            )
            if name not in self._class_mapping:
                # inform over replacing mapping
                # or append these mappings instead of replacing?
                self._class_mapping[name] = self._models[name].model_class

    def _get_known_bases(self):
        return list(self._class_mapping.keys())

    def _resolve_references(self):
        for model_name, v in iteritems(self._models):
            v.resolve(self)
            setattr(self, v.model_class.__name__, v.model_class)

    def finalize(self, freeze=True):
        self._validate_not_frozen()

        self._resolve_classes()
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
