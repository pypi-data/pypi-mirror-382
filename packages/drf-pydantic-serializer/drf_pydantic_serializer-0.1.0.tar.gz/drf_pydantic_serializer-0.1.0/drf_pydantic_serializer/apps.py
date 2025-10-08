import importlib
from django.apps import AppConfig


class DRFPydanticSerializerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_pydantic_serializer"

    def ready(self):
        if importlib.util.find_spec("drf_spectacular") is not None:
            pass
