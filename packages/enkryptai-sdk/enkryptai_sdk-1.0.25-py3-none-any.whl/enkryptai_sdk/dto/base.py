import json
from dataclasses import dataclass, field
from typing import Type, Dict, Any, TypeVar

T = TypeVar("T", bound="BaseDTO")


@dataclass
class BaseDTO:
    """Base class for all DTO classes with common serialization methods."""

    def __getattr__(self, name):
        """Called when an attribute is not found in the normal places."""
        try:
            extra_fields = object.__getattribute__(self, "_extra_fields")
            if name in extra_fields:
                return extra_fields[name]
        except AttributeError:
            pass

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name, value):
        """Handle setting attributes, storing unknown ones in _extra_fields."""
        if name in self.__class__.__annotations__ or name == "_extra_fields":
            super().__setattr__(name, value)
        else:
            self._extra_fields[name] = value

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an instance from a dictionary."""
        known_fields = cls.__annotations__.keys()
        base_data = {k: v for k, v in data.items() if k in known_fields}
        extra_fields = {
            k: v
            for k, v in data.items()
            if k not in known_fields and k != "_extra_fields"
        }

        instance = cls(**base_data)
        instance._extra_fields = extra_fields
        return instance

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create an instance from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the instance to a dictionary."""
        d = {}
        for k, v in self.__dict__.items():
            if k == "_extra_fields":
                continue
            if hasattr(v, "to_dict"):
                d[k] = v.to_dict()
            elif isinstance(v, list):
                d[k] = [item.to_dict() if hasattr(item, "to_dict") else item for item in v]
            elif isinstance(v, dict):
                d[k] = {key: val.to_dict() if hasattr(val, "to_dict") else val for key, val in v.items()}
            else:
                d[k] = v
        d.update(self._extra_fields)
        return d

    def to_json(self) -> str:
        """Convert the instance to a JSON string."""
        return json.dumps(self.to_dict())

    def get_all_fields(self) -> Dict[str, Any]:
        """Safely get all fields including extra fields."""
        regular_fields = {k: v for k, v in vars(self).items() if not k.startswith("_")}
        extra_fields = vars(self).get("_extra_fields", {})

        result = regular_fields.copy()
        result.update(extra_fields)
        return result
