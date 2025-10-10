# custom_type_registry.py
from pydantic import BaseModel

from intuned_browser.helpers.types import Attachment


class CustomTypeRegistry:
    """Registry for custom JSON Schema types to Pydantic model mappings."""

    def __init__(self, register_intuned_types: bool = True):
        self._registry: dict[str, type[BaseModel]] = {}
        self._reverse_registry: dict[type[BaseModel], str] = {}
        if register_intuned_types:
            self.__register_intuned_types()

    def __register_intuned_types(self):
        self.register("attachment", Attachment)

    def register(self, type_name: str, model: type[BaseModel]):
        """Register a custom type mapping."""
        if type_name in self._registry:
            del self._reverse_registry[self._registry[type_name]]

        self._registry[type_name] = model
        self._reverse_registry[model] = type_name

    def get(self, type_name: str) -> type[BaseModel] | None:
        """Retrieve Pydantic model for a custom type (case insensitive)."""

        type_name_lower = type_name.lower()
        for registered_name, model in self._registry.items():
            if registered_name.lower() == type_name_lower:
                return model

        return None

    def get_type_name(self, model: type[BaseModel]) -> str | None:
        """Get the custom type name for a Pydantic model."""
        return self._reverse_registry.get(model)

    def is_custom_type(self, type_name: str) -> bool:
        """Check if type is registered as custom (case insensitive)."""
        # First try exact match
        if type_name in self._registry:
            return True

        # Then try case insensitive match
        type_name_lower = type_name.lower()
        for registered_name in self._registry:
            if registered_name.lower() == type_name_lower:
                return True

        return False

    def is_custom_model(self, model: type) -> bool:
        """Check if a model is registered as custom."""
        return model in self._reverse_registry
