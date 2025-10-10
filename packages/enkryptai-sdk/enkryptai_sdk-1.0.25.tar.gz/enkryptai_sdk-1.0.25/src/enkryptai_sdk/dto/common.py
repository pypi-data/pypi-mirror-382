# To avoid circular imports
from enum import Enum
from .base import BaseDTO
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


class ModelAuthTypeEnum(str, Enum):
    APIKEY = "apikey"
    JWT = "jwt"


class ModelJwtMethodEnum(str, Enum):
    POST = "POST"
    GET = "GET"


@dataclass
class CustomHeader(BaseDTO):
    key: str
    value: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomHeader":
        return cls(
            key=data.get("key", ""),
            value=data.get("value", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value
        }


@dataclass
class ModelJwtConfig(BaseDTO):
    jwt_method: ModelJwtMethodEnum = ModelJwtMethodEnum.POST
    jwt_url: str = ""
    jwt_headers: List[CustomHeader] = field(default_factory=list)
    jwt_body: str = ""
    jwt_response_key: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelJwtConfig":
        return cls(
            jwt_method=ModelJwtMethodEnum(data.get("jwt_method", ModelJwtMethodEnum.POST)),
            jwt_url=data.get("jwt_url", ""),
            jwt_headers=[CustomHeader.from_dict(header) for header in data.get("jwt_headers", [])],
            jwt_body=data.get("jwt_body", ""),
            jwt_response_key=data.get("jwt_response_key", ""),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jwt_method": self.jwt_method.value,
            "jwt_url": self.jwt_url,
            "jwt_headers": [header.to_dict() for header in self.jwt_headers],
            "jwt_body": self.jwt_body,
            "jwt_response_key": self.jwt_response_key,
        }

