import importlib.util
from typing import Any, Dict
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel
from pydantic.dataclasses import is_pydantic_dataclass
from typing import get_origin, get_args

if importlib.util.find_spec("drf_spectacular") is not None:
    from drf_spectacular.extensions import OpenApiSerializerFieldExtension
    from drf_spectacular.openapi import AutoSchema
    from drf_spectacular.plumbing import build_basic_type
    from drf_spectacular.types import OpenApiTypes

    USE_SPECTACULAR = True
else:
    USE_SPECTACULAR = False


if USE_SPECTACULAR:

    class PydanticFieldExtension(OpenApiSerializerFieldExtension):
        target_class = "drf_pydantic_serializer.fields.PydanticField"

        def _get_basic_type_for_python_type(
            self, python_type: Any, auto_schema: AutoSchema, direction: str
        ) -> Dict[str, Any]:
            origin = get_origin(python_type)
            args = get_args(python_type)

            if origin is list:
                if args:
                    inner_type = args[0]
                    try:
                        if isinstance(inner_type, type) and (
                            issubclass(inner_type, BaseModel)
                            or is_pydantic_dataclass(inner_type)
                        ):
                            return {
                                "type": "array",
                                "items": self._extract_pydantic_model_schema(
                                    inner_type, auto_schema, direction
                                ),
                            }
                    except TypeError:
                        pass
                    return {
                        "type": "array",
                        "items": self._get_basic_type_for_python_type(
                            inner_type, auto_schema, direction
                        ),
                    }
                return {"type": "array", "items": build_basic_type(OpenApiTypes.STR)}

            base_type = python_type if origin is None else origin

            try:
                if isinstance(python_type, type) and (
                    issubclass(python_type, BaseModel)
                    or is_pydantic_dataclass(python_type)
                ):
                    return self._extract_pydantic_model_schema(
                        python_type, auto_schema, direction
                    )
            except TypeError:
                pass

            if base_type is UUID:
                return build_basic_type(OpenApiTypes.UUID)
            elif base_type is Decimal:
                return build_basic_type(OpenApiTypes.DECIMAL)
            elif base_type is int:
                return build_basic_type(OpenApiTypes.INT)
            elif base_type is float:
                return build_basic_type(OpenApiTypes.FLOAT)
            elif base_type is bool:
                return build_basic_type(OpenApiTypes.BOOL)
            elif base_type is str:
                return build_basic_type(OpenApiTypes.STR)
            else:
                return build_basic_type(OpenApiTypes.STR)

        def _extract_pydantic_model_schema(
            self, model_cls: type, auto_schema: AutoSchema, direction: str
        ) -> Dict[str, Any]:
            properties = {}
            required = []

            if is_pydantic_dataclass(model_cls):
                fields = model_cls.__pydantic_fields__  # type: ignore[attr-defined]
            else:
                fields = model_cls.model_fields  # type: ignore[attr-defined]

            for field_name, field_info in fields.items():
                properties[field_name] = self._get_basic_type_for_python_type(
                    field_info.annotation, auto_schema, direction
                )

                if field_info.is_required():
                    required.append(field_name)

            schema = {"type": "object", "properties": properties}
            if required:
                schema["required"] = required
            return schema

        def map_serializer_field(
            self, auto_schema: AutoSchema, direction: str
        ) -> Dict[str, Any]:
            field = self.target
            type_adapter = getattr(field, "type_adapter", None)
            if type_adapter is None:
                return build_basic_type(OpenApiTypes.STR)

            core_schema = type_adapter.core_schema
            schema_type = core_schema.get("type")

            if schema_type == "uuid":
                return build_basic_type(OpenApiTypes.UUID)
            elif schema_type == "decimal":
                return build_basic_type(OpenApiTypes.DECIMAL)
            elif schema_type in ("int", "integer"):
                return build_basic_type(OpenApiTypes.INT)
            elif schema_type == "float":
                return build_basic_type(OpenApiTypes.FLOAT)
            elif schema_type in ("bool", "boolean"):
                return build_basic_type(OpenApiTypes.BOOL)
            elif schema_type in ("str", "string"):
                return build_basic_type(OpenApiTypes.STR)
            elif schema_type == "enum":
                enum_choices = core_schema.get("members", [])
                return {"type": "string", "enum": enum_choices}
            elif schema_type == "list":
                items_schema = core_schema.get("items_schema", {})
                items_type = items_schema.get("type")

                if items_type in ("model", "dataclass"):
                    model_cls = items_schema.get("cls")
                    if (
                        model_cls
                        and isinstance(model_cls, type)
                        and (
                            issubclass(model_cls, BaseModel)
                            or is_pydantic_dataclass(model_cls)
                        )
                    ):
                        return {
                            "type": "array",
                            "items": self._extract_pydantic_model_schema(
                                model_cls, auto_schema, direction
                            ),
                        }

            return self._get_basic_type_for_python_type(
                type_adapter._type, auto_schema, direction
            )
