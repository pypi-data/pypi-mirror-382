from uuid import UUID

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from tortoise import fields as field
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tortoise.models import Model as TortoiseModel


def __uuid_schema_monkey_patch(cls, source_type, handler):
    # Always treat UUID as string schema
    return core_schema.no_info_after_validator_function(
        # Accept UUID or str, always return UUID internally
        lambda v: v if isinstance(v, UUID) else UUID(str(v)),
        core_schema.union_schema(
            [
                core_schema.str_schema(),
                core_schema.is_instance_schema(UUID),
            ]
        ),
        # But when serializing, always str()
        serialization=core_schema.plain_serializer_function_ser_schema(
            str, when_used="always"
        ),
    )


# Monkey-patch UUID
UUID.__get_pydantic_core_schema__ = classmethod(__uuid_schema_monkey_patch)


class ModelMeta(type(TortoiseModel)):
    def __new__(mcls, name, bases, attrs):
        # Grab the Schema class for further processing.
        schema_opts = attrs.get("Schema", None)

        # Let Tortoise's Metaclass do it's thing.
        new_cls = super().__new__(mcls, name, bases, attrs)

        class BoundSchema:
            def __call__(self, readonly: bool = False):
                return self.get(readonly)

            @property
            def model(self):
                """Return a Pydantic model class for serializing results."""
                include = getattr(schema_opts, "include", None)
                exclude = getattr(schema_opts, "exclude", None)
                return pydantic_model_creator(
                    new_cls,
                    name=f"{new_cls.__name__}Schema",
                    include=include,
                    exclude=exclude,
                )

            @property
            def readonly(self):
                """Return a Pydantic model class for serializing readonly results."""
                include = getattr(schema_opts, "include", None)
                exclude = getattr(schema_opts, "exclude", None)
                return pydantic_model_creator(
                    new_cls,
                    name=f"{new_cls.__name__}SchemaReadonly",
                    include=include,
                    exclude=exclude,
                    exclude_readonly=True,
                )

            def get(self, readonly: bool = False):
                if readonly:
                    return self.readonly
                return self.model

        new_cls.Schema = BoundSchema()
        return new_cls


class Model(TortoiseModel, metaclass=ModelMeta):
    class Schema:
        include = None
        exclude = None
