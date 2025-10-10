from enum import Enum
from .base import BaseDTO
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Optional, BinaryIO


@dataclass
class CoCPolicyData(BaseDTO):
    created_at: str
    created_by: str
    updated_by: str
    name: str
    updated_at: str
    policy_id: int
    project_name: str = "default"
    policy_rules: str = ""
    total_rules: int = 0
    pdf_name: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoCPolicyData":
        return cls(
            created_at=data.get("created_at", ""),
            created_by=data.get("created_by", ""),
            updated_by=data.get("updated_by", ""),
            name=data.get("name", ""),
            updated_at=data.get("updated_at", ""),
            policy_id=data.get("policy_id", 0),
            project_name=data.get("project_name", "default"),
            policy_rules=data.get("policy_rules", ""),
            total_rules=data.get("total_rules", 0),
            pdf_name=data.get("pdf_name", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "name": self.name,
            "updated_at": self.updated_at,
            "policy_id": self.policy_id,
            "project_name": self.project_name,
            "policy_rules": self.policy_rules,
            "total_rules": self.total_rules,
            "pdf_name": self.pdf_name
        }
        result.update(self._extra_fields)
        return result
    
    def get_rules_list(self) -> List[str]:
        """
        Get the policy rules as a list of strings.
        
        Returns:
            List[str]: List of individual policy rules
        """
        if not self.policy_rules:
            return []
        return [rule.strip() for rule in self.policy_rules.split('\n') if rule.strip()]
    
    def __str__(self) -> str:
        """
        String representation of the response.
        
        Returns:
            str: A formatted string 
        """
        return (
            f"Policy Name: {self.name}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}\n"
            f"Created By: {self.created_by}\n"
            f"Updated By: {self.updated_by}\n"
            f"Policy ID: {self.policy_id}\n"
            f"total_rules: {self.total_rules}\n"
        )


@dataclass
class CoCPolicyResponse(BaseDTO):
    message: str
    data: CoCPolicyData
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoCPolicyResponse":
        policy_data = data.get("data", {})
        return cls(
            message=data.get("message", ""),
            data=CoCPolicyData.from_dict(policy_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "message": self.message,
            "data": self.data.to_dict()
        }
        result.update(self._extra_fields)
        return result


@dataclass
class CoCDeletePolicyData(BaseDTO):
    policy_id: int
    project_name: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoCDeletePolicyData":
        return cls(
            policy_id=data.get("policy_id", 0),
            project_name=data.get("project_name", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "policy_id": self.policy_id,
            "project_name": self.project
        }
        result.update(self._extra_fields)
        return result


@dataclass
class CoCDeletePolicyResponse(BaseDTO):
    message: str
    data: CoCDeletePolicyData
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoCDeletePolicyResponse":
        policy_data = data.get("data", {})
        return cls(
            message=data.get("message", ""),
            data=CoCDeletePolicyData.from_dict(policy_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "message": self.message,
            "data": self.data.to_dict()
        }
        result.update(self._extra_fields)
        return result


@dataclass
class CoCListPoliciesResponse(BaseDTO):
    policies: List[CoCPolicyData] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoCListPoliciesResponse":
        policies_data = data.get("policies", [])
        return cls(
            policies=[CoCPolicyData.from_dict(policy) for policy in policies_data]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "policies": [policy.to_dict() for policy in self.policies]
        }
        result.update(self._extra_fields)
        return result

