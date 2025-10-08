# DRF Pydantic Serializer

Django REST Framework serializers powered by Pydantic models and dataclasses.

## Features

- ✅ **Auto-generate DRF serializers** from Pydantic models and dataclasses
- ✅ **Full Pydantic validation** - leverage Pydantic's powerful validation engine
- ✅ **Type-safe** - get IDE autocomplete and type checking
- ✅ **OpenAPI schema generation** - automatic drf-spectacular integration
- ✅ **Nested models & dataclasses** - full support for complex structures
- ✅ **Generic support** - use `PydanticModelSerializer[YourModel]` syntax

## Installation

```bash
pip install drf-pydantic-serializer
```

Or with Poetry:

```bash
poetry add drf-pydantic-serializer
```

## Quick Start

### Using Pydantic Models

```python
from pydantic import BaseModel, Field
from drf_pydantic_serializer.serializers import PydanticModelSerializer

class Person(BaseModel):
    name: str
    age: int
    email: str | None = None

# Option 1: Generic syntax
class PersonSerializer(PydanticModelSerializer[Person]):
    pass

# Option 2: Meta class
class PersonSerializer(PydanticModelSerializer):
    class Meta:
        base_model = Person
```

### Using Pydantic Dataclasses

```python
from pydantic.dataclasses import dataclass
from drf_pydantic_serializer.serializers import PydanticDataclassSerializer

@dataclass
class Product:
    id: int
    title: str
    price: float
    description: str | None = None

class ProductSerializer(PydanticDataclassSerializer):
    class Meta:
        pydantic_dataclass = Product
```

### Use in Django Views

```python
from rest_framework.views import APIView
from rest_framework.response import Response

class PersonView(APIView):
    def post(self, request):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            person = serializer.save()  # Returns Pydantic model instance
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

## Advanced Usage

### Nested Models

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    email: str
    address: Address

class UserSerializer(PydanticModelSerializer[User]):
    pass
```

### Lists and Collections

```python
from pydantic import BaseModel

class Tag(BaseModel):
    name: str
    color: str

class Article(BaseModel):
    title: str
    tags: list[Tag]

class ArticleSerializer(PydanticModelSerializer[Article]):
    pass
```

### Validation Errors

Pydantic validation errors are automatically converted to DRF-compatible error format:

```python
serializer = PersonSerializer(data={"name": "John", "age": "invalid"})
serializer.is_valid()  # False
print(serializer.errors)
# {'age': ['Input should be a valid integer...']}
```

## OpenAPI/Swagger Integration

Automatically generate OpenAPI schemas with drf-spectacular:

### Setup

```bash
pip install drf-spectacular
```

**settings.py:**

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_spectacular',
    'drf_pydantic_serializer',  # Auto-registers OpenAPI extension
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'VERSION': '1.0.0',
}
```

**urls.py:**

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
```

Now all your Pydantic-based serializers will automatically appear in Swagger UI with proper schema generation!

## How It Works

1. **Field Generation**: Automatically creates DRF fields from Pydantic model/dataclass fields
2. **Validation**: Uses Pydantic's validation during `is_valid()`
3. **Serialization**: Converts instances to JSON-compatible dicts using Pydantic's `model_dump()`
4. **Deserialization**: Creates Pydantic instances from validated data

## Comparison with Standard DRF Serializers

**Standard DRF:**
```python
class PersonSerializer(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()
    email = serializers.EmailField(required=False, allow_null=True)

    def validate_age(self, value):
        if value < 0:
            raise ValidationError("Age must be positive")
        return value
```

**With drf-pydantic-serializer:**
```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: str | None = None

class PersonSerializer(PydanticModelSerializer[Person]):
    pass
```

Benefits:
- Less boilerplate
- Reuse Pydantic models across your codebase
- Type safety and IDE support
- Consistent validation logic

## API Reference

### PydanticModelSerializer

Serializer for Pydantic `BaseModel` classes.

**Configuration:**
- Generic: `PydanticModelSerializer[YourModel]`
- Meta: `class Meta: base_model = YourModel`
- Instance: `PydanticModelSerializer(pydantic_model=YourModel)`

**Methods:**
- `validate(attrs)`: Returns validated Pydantic model instance
- `create(validated_data)`: Returns the Pydantic model instance
- `update(instance, validated_data)`: Merges and returns updated instance
- `to_representation(instance)`: Converts to JSON-compatible dict

### PydanticDataclassSerializer

Serializer for Pydantic dataclasses.

**Configuration:**
- Meta: `class Meta: pydantic_dataclass = YourDataclass`
- Instance: `PydanticDataclassSerializer(pydantic_dataclass=YourDataclass)`

**Methods:** Same as `PydanticModelSerializer`

## Requirements

- Python 3.10+
- Django 4.0+
- Django REST Framework 3.14+
- Pydantic 2.0+

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a PR.
