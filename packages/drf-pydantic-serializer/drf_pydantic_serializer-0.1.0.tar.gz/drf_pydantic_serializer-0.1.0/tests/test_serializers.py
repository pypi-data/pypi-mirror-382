from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass as pydantic_dataclass
import pytest


from drf_pydantic_serializer.serializers import (
    PydanticModelSerializer,
    PydanticDataclassSerializer,
)


class Person(BaseModel):
    name: str
    age: int
    email: str | None = None


class Product(BaseModel):
    id: int
    title: str
    price: float
    description: str | None = Field(None, description="Product description")


@pydantic_dataclass
class PersonDataclass:
    name: str
    age: int
    email: str | None = None


@pydantic_dataclass
class ProductDataclass:
    id: int
    title: str
    price: float
    description: str | None = None


class PersonSerializer(PydanticModelSerializer[Person]):
    pass


class ProductSerializerWithMeta(PydanticModelSerializer):
    class Meta:
        base_model = Product


class PersonDataclassSerializer(PydanticDataclassSerializer):
    class Meta:
        pydantic_dataclass = PersonDataclass


@pytest.fixture
def person_data():
    return {"name": "John Doe", "age": 30, "email": "john@example.com"}


@pytest.fixture
def product_data():
    return {"id": 1, "title": "Widget", "price": 19.99, "description": "A great widget"}


def test_model_serializer_validation_success(person_data):
    serializer = PersonSerializer(data=person_data)
    assert serializer.is_valid()
    assert serializer.validated_data.name == "John Doe"
    assert serializer.validated_data.age == 30


def test_model_serializer_validation_failure():
    serializer = PersonSerializer(data={"name": "John", "age": "invalid"})
    assert not serializer.is_valid()
    assert "age" in serializer.errors


def test_model_serializer_create(person_data):
    serializer = PersonSerializer(data=person_data)
    assert serializer.is_valid()
    person = serializer.save()
    assert isinstance(person, Person)
    assert person.name == "John Doe"
    assert person.age == 30


def test_model_serializer_update():
    person = Person(name="John", age=25, email="john@old.com")
    serializer = PersonSerializer(
        person, data={"name": "John", "age": 26, "email": "john@old.com"}
    )
    assert serializer.is_valid()
    updated = serializer.save()
    assert updated.age == 26
    assert updated.email == "john@old.com"


def test_model_serializer_to_representation():
    person = Person(name="Jane", age=28)
    serializer = PersonSerializer(person)
    data = serializer.data
    assert data["name"] == "Jane"
    assert data["age"] == 28
    assert data["email"] is None


def test_model_serializer_with_meta(product_data):
    serializer = ProductSerializerWithMeta(data=product_data)
    assert serializer.is_valid()
    product = serializer.save()
    assert product.title == "Widget"
    assert product.price == 19.99


def test_model_serializer_optional_fields():
    serializer = PersonSerializer(data={"name": "Bob", "age": 35})
    assert serializer.is_valid()
    person = serializer.save()
    assert person.email is None


def test_dataclass_serializer_validation_success(person_data):
    serializer = PersonDataclassSerializer(data=person_data)
    assert serializer.is_valid()
    assert serializer.validated_data.name == "John Doe"
    assert serializer.validated_data.age == 30


def test_dataclass_serializer_validation_failure():
    serializer = PersonDataclassSerializer(data={"name": "John", "age": "invalid"})
    assert not serializer.is_valid()
    assert "age" in serializer.errors


def test_dataclass_serializer_create(person_data):
    serializer = PersonDataclassSerializer(data=person_data)
    assert serializer.is_valid()
    person = serializer.save()
    assert isinstance(person, PersonDataclass)
    assert person.name == "John Doe"
    assert person.age == 30


def test_dataclass_serializer_update():
    person = PersonDataclass(name="John", age=25, email="john@old.com")
    serializer = PersonDataclassSerializer(
        person, data={"name": "John", "age": 26, "email": "john@old.com"}
    )
    assert serializer.is_valid()
    updated = serializer.save()
    assert updated.age == 26
    assert updated.email == "john@old.com"


def test_dataclass_serializer_to_representation():
    person = PersonDataclass(name="Jane", age=28, email=None)
    serializer = PersonDataclassSerializer(person)
    data = serializer.data
    assert data["name"] == "Jane"
    assert data["age"] == 28
    assert data["email"] is None


def test_dataclass_serializer_optional_fields():
    serializer = PersonDataclassSerializer(data={"name": "Bob", "age": 35})
    assert serializer.is_valid()
    person = serializer.save()
    assert person.email is None


def test_model_serializer_no_config_raises():
    with pytest.raises(AssertionError, match="Pydantic model not configured"):
        PydanticModelSerializer(data={})


def test_dataclass_serializer_no_config_raises():
    with pytest.raises(AssertionError, match="Pydantic dataclass not configured"):
        PydanticDataclassSerializer(data={})
