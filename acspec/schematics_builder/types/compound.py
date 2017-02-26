
from schematics.types import IntType
from schematics.types.compound import ListType, ModelType

from acspec.exceptions import AcspecContextError
from acspec.schematics_builder.fixes import DictType
from acspec.schematics_builder.types.base import TypeDescriptorBase


class CompoundTypeDescriptorBase(TypeDescriptorBase):
    __abstract_type_descriptor__ = True

    @classmethod
    def has_content_type(cls):
        return True

    def init_schematics_type(self, context=None):
        descriptor_class = self.schematics_type
        kwargs = self.get_descriptor_kwargs()
        nested = self.get_nested_value().init_schematics_type(
            context=context
        )
        return descriptor_class(nested, **kwargs)

    def get_nested_value(self):
        base = getattr(self, "type", None)
        if not base:
            base = self
        return base.get(self.type_name)

    def get_requires_context(self):
        nested_value = self.get_nested_value()
        if hasattr(nested_value, "get_requires_context"):
            return nested_value.get_requires_context()
        else:
            return False


class ContextTypeDescriptorBase(CompoundTypeDescriptorBase):
    __abstract_type_descriptor__ = True

    @classmethod
    def has_content_type(cls):
        return False

    def init_schematics_type(self, context=None):
        if context is None:
            raise AcspecContextError(
                "No context provided to resolve model"
            )
        else:
            model_name = self.get_nested_value()
            model_class = context.get_model_class(model_name)

            if model_class is None:
                raise AcspecContextError(
                    "Model '{}' not found".format(model_name)
                )
            return self.schematics_type(
                model_class,
                **self.get_descriptor_kwargs()
            )
        assert context

    def get_requires_context(self):
        return True


class ListTypeDescriptorBase(CompoundTypeDescriptorBase):

    type_name = "list"
    schematics_type = ListType

    min_size = IntType()
    max_size = IntType()


class DictTypeDescriptorBase(CompoundTypeDescriptorBase):

    type_name = "dict"
    schematics_type = DictType


class ModelTypeDescriptorBase(ContextTypeDescriptorBase):

    type_name = "model"
    schematics_type = ModelType

    requires_context = True


COMPOUND_TYPE_DESCRIPTORS = [
    ListTypeDescriptorBase,
    DictTypeDescriptorBase
]
