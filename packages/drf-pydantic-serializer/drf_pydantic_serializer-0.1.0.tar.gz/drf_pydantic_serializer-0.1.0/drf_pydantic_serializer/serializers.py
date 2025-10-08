from typing import (
    Any,
    Dict,
    Type,
    Generic,
    TypeVar,
    get_args,
    get_origin,
    cast,
)


from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import is_pydantic_dataclass
from pydantic.type_adapter import TypeAdapter

from rest_framework import serializers
from rest_framework.exceptions import ParseError

from drf_pydantic_serializer.fields import PydanticField


T = TypeVar("T", bound=BaseModel)
DataclassType = TypeVar("DataclassType")


def _is_optional(tp: Any) -> bool:
    origin = get_origin(tp)
    if origin is None:
        return False
    args = get_args(tp)
    return type(None) in args


def _pydantic_errors_to_drf(exc: ValidationError) -> Dict[str, Any]:
    errors: Dict[str, Any] = {}
    for err in exc.errors():
        loc = err.get("loc", ())
        msg = err.get("msg", "Validation error")
        field_path = ".".join(str(x) for x in loc) if loc else "non_field_errors"
        errors.setdefault(field_path, []).append(msg)
    return errors


def _extract_generic_base_model(cls: type) -> Type[BaseModel] | None:
    for base in getattr(cls, "__orig_bases__", ()):
        if (
            get_origin(base) is not None
            and getattr(get_origin(base), "__name__", "") == "PydanticModelSerializer"
        ):
            args = get_args(base)
            if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                return args[0]
    return None


def _extract_generic_dataclass(cls: type) -> type | None:
    for base in getattr(cls, "__orig_bases__", ()):
        if (
            get_origin(base) is not None
            and getattr(get_origin(base), "__name__", "")
            == "PydanticDataclassSerializer"
        ):
            args = get_args(base)
            if args and isinstance(args[0], type) and is_pydantic_dataclass(args[0]):
                return args[0]
    return None


class PydanticModelSerializer(Generic[T], serializers.Serializer):
    pydantic_model: Type[BaseModel] | None = None

    _validated_model: BaseModel | None = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # meta model...
        meta_model = getattr(getattr(cls, "Meta", None), "base_model", None)

        # ... or generic
        generic_model = _extract_generic_base_model(cls)

        chosen = meta_model or generic_model

        if chosen is not None:
            if not issubclass(chosen, BaseModel):
                raise TypeError(
                    f"{cls.__name__}.Meta.base_model must be a Pydantic BaseModel subclass"
                )
            cls.pydantic_model = chosen  # set at class level

    def __init__(
        self, *args: Any, pydantic_model: Type[BaseModel] | None = None, **kwargs: Any
    ):
        if pydantic_model is not None:
            self.pydantic_model = pydantic_model
        if self.pydantic_model is None:
            raise AssertionError(
                "Pydantic model not configured. "
                "You can declare `class Meta: base_model = CustomModel` or subclass as "
                "`PydanticModelSerializer[CustomModel]`, or pass `pydantic_model=` at init."
            )
        super().__init__(*args, **kwargs)

    def get_fields(self) -> Dict[str, serializers.Field]:
        model = self.pydantic_model
        assert model is not None

        fields: Dict[str, serializers.Field] = {}
        for name, f in model.model_fields.items():
            ann = f.annotation if f.annotation is not None else Any
            # annotated = Annotated[ann, f]  # include FieldInfo constraints
            ta: TypeAdapter[Any] = TypeAdapter(ann)

            required = f.is_required()
            default = f.default if not required else serializers.empty
            allow_none = _is_optional(ann)

            drf_field = PydanticField(
                type_adapter=ta,
                required=required,
                default=default,
                allow_none=allow_none,
                label=(getattr(f, "title", None) or name.replace("_", " ").title()),
                help_text=getattr(f, "description", None),
            )
            fields[name] = drf_field
        return fields

    def validate(self, attrs: Dict[str, Any]) -> BaseModel:
        model = self.pydantic_model  # type: ignore[assignment]
        assert model is not None
        try:
            self._validated_model = model.model_validate(attrs)
            return self._validated_model
        except ValidationError as e:
            raise ParseError(_pydantic_errors_to_drf(e))

    def save(self, **kwargs: Any) -> BaseModel:
        assert hasattr(
            self, "_errors"
        ), "You must call `.is_valid()` before calling `.save()`."
        assert (
            not self.errors
        ), "You cannot call `.save()` on a serializer with invalid data."

        validated_data = cast(BaseModel, self.validated_data)
        instance: BaseModel | None = cast(BaseModel | None, self.instance)  # type: ignore[assignment,has-type]
        if instance is not None:
            result = self.update(instance, validated_data)
            self.instance = result
            return result
        else:
            result = self.create(validated_data)
            self.instance = result
            return result

    def create(self, validated_data: BaseModel) -> BaseModel:
        return validated_data

    def update(self, instance: BaseModel, validated_data: BaseModel) -> BaseModel:
        model = self.pydantic_model  # type: ignore[assignment]
        assert model is not None
        merged = {**instance.model_dump(), **validated_data.model_dump()}
        return model.model_validate(merged)

    def to_representation(self, instance: Any) -> Dict[str, Any]:
        model = self.pydantic_model  # type: ignore[assignment]
        assert model is not None
        if isinstance(instance, BaseModel):
            return instance.model_dump(mode="json")
        coerced = model.model_validate(instance)
        return coerced.model_dump(mode="json")


class PydanticDataclassSerializer(serializers.Serializer):
    pydantic_dataclass: type | None = None

    _validated_dataclass: Any = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        meta_dataclass = getattr(getattr(cls, "Meta", None), "pydantic_dataclass", None)

        generic_dataclass = _extract_generic_dataclass(cls)

        chosen = meta_dataclass or generic_dataclass

        if chosen is not None:
            if not is_pydantic_dataclass(chosen):
                raise TypeError(
                    f"{cls.__name__}.Meta.pydantic_dataclass must be a Pydantic dataclass"
                )
            cls.pydantic_dataclass = chosen

    def __init__(
        self, *args: Any, pydantic_dataclass: type | None = None, **kwargs: Any
    ):
        if pydantic_dataclass is not None:
            self.pydantic_dataclass = pydantic_dataclass
        if self.pydantic_dataclass is None:
            raise AssertionError(
                "Pydantic dataclass not configured. "
                "You can declare `class Meta: pydantic_dataclass = CustomDataclass` or "
                "subclass as `PydanticDataclassSerializer[CustomDataclass]`, or pass "
                "`pydantic_dataclass=` at init."
            )
        super().__init__(*args, **kwargs)

    def get_fields(self) -> Dict[str, serializers.Field]:
        dc = self.pydantic_dataclass
        assert dc is not None
        assert is_pydantic_dataclass(dc)

        fields: Dict[str, serializers.Field] = {}
        for name, f in dc.__pydantic_fields__.items():
            ann = f.annotation if f.annotation is not None else Any
            ta: TypeAdapter[Any] = TypeAdapter(ann)

            required = f.is_required()
            default = f.default if not required else serializers.empty
            allow_none = _is_optional(ann)

            drf_field = PydanticField(
                type_adapter=ta,
                required=required,
                default=default,
                allow_none=allow_none,
                label=(getattr(f, "title", None) or name.replace("_", " ").title()),
                help_text=getattr(f, "description", None),
            )
            fields[name] = drf_field
        return fields

    def validate(self, attrs: Dict[str, Any]) -> Any:
        dc = self.pydantic_dataclass
        assert dc is not None
        try:
            ta: TypeAdapter[Any] = TypeAdapter(dc)
            self._validated_dataclass = ta.validate_python(attrs)
            return self._validated_dataclass
        except ValidationError as e:
            raise ParseError(_pydantic_errors_to_drf(e))

    def save(self, **kwargs: Any) -> Any:
        assert hasattr(
            self, "_errors"
        ), "You must call `.is_valid()` before calling `.save()`."
        assert (
            not self.errors
        ), "You cannot call `.save()` on a serializer with invalid data."

        validated_data = self.validated_data
        instance: Any = self.instance  # type: ignore[assignment,has-type]
        if instance is not None:
            result = self.update(instance, validated_data)
            self.instance = result
            return result
        else:
            result = self.create(validated_data)
            self.instance = result
            return result

    def create(self, validated_data: Any) -> Any:
        return validated_data

    def update(self, instance: Any, validated_data: Any) -> Any:
        dc = self.pydantic_dataclass
        assert dc is not None
        ta: TypeAdapter[Any] = TypeAdapter(dc)
        instance_dict = ta.dump_python(instance)
        merged = {**instance_dict, **ta.dump_python(validated_data)}
        return ta.validate_python(merged)

    def to_representation(self, instance: Any) -> Dict[str, Any]:
        dc = self.pydantic_dataclass
        assert dc is not None
        ta: TypeAdapter[Any] = TypeAdapter(dc)
        if is_pydantic_dataclass(type(instance)):
            return ta.dump_python(instance, mode="json")
        coerced = ta.validate_python(instance)
        return ta.dump_python(coerced, mode="json")
