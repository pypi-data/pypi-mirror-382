"""Type aliases needed in the package."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeAlias, TypeVar

from pydantic import BaseModel

from .model_version import ModelVersion

DecoratedBaseModel = TypeVar("DecoratedBaseModel", bound=BaseModel)

JsonValue: TypeAlias = (
    int | float | str | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonSchema: TypeAlias = dict[str, JsonValue]
JsonSchemaDefinitions: TypeAlias = dict[str, JsonValue]
JsonSchemaGenerator: TypeAlias = Callable[[type[BaseModel]], JsonSchema]
SchemaGenerators: TypeAlias = dict[ModelVersion, JsonSchemaGenerator]

MigrationData: TypeAlias = dict[str, Any]
MigrationFunc: TypeAlias = Callable[[MigrationData], MigrationData]


MigrationKey: TypeAlias = tuple[ModelVersion, ModelVersion]
MigrationMap: TypeAlias = dict[MigrationKey, MigrationFunc]

ModelName: TypeAlias = str
ModelMetadata: TypeAlias = tuple[ModelName, ModelVersion]
VersionedModels: TypeAlias = dict[ModelVersion, type[BaseModel]]
