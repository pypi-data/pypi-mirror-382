from typing import Any

from pydantic import BaseModel, ValidationError
from pydantic.type_adapter import TypeAdapter
from rest_framework import serializers


class PydanticField(serializers.Field):
    def __init__(
        self,
        *,
        type_adapter: TypeAdapter[Any],
        required: bool = True,
        default: Any = serializers.empty,
        allow_none: bool = False,
        **kwargs: Any,
    ):
        self.type_adapter = type_adapter
        self.allow_none = allow_none
        if default is not serializers.empty:
            kwargs.setdefault("default", default)
            required = False
        kwargs.setdefault("required", required)
        super().__init__(**kwargs)

    def to_internal_value(self, data: Any) -> Any:
        if data is None and self.allow_none:
            return None
        try:
            return self.type_adapter.validate_python(data)
        except ValidationError as e:
            raise serializers.ValidationError(e)

    def to_representation(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        return value
