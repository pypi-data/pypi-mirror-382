from enum import Enum
from .base import BaseDTO
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field


class InputGuardrailBlockType(str, Enum):
    TOPIC_DETECTOR = "topic_detector"
    NSFW = "nsfw"
    TOXICITY = "toxicity"
    PII = "pii"
    INJECTION_ATTACK = "injection_attack"
    KEYWORD_DETECTOR = "keyword_detector"
    POLICY_VIOLATION = "policy_violation" 
    BIAS = "bias"
    SYSTEM_PROMPT = "system_prompt"
    COPYRIGHT_IP = "copyright_ip"
    SPONGE_ATTACK = "sponge_attack"


class OutputGuardrailBlockType(str, Enum):
    TOPIC_DETECTOR = "topic_detector"
    NSFW = "nsfw"
    TOXICITY = "toxicity"
    PII = "pii"
    INJECTION_ATTACK = "injection_attack"
    KEYWORD_DETECTOR = "keyword_detector"
    POLICY_VIOLATION = "policy_violation"
    BIAS = "bias"
    SYSTEM_PROMPT = "system_prompt"
    COPYRIGHT_IP = "copyright_ip"
    SPONGE_ATTACK = "sponge_attack"
    HALLUCINATION = "hallucination"
    ADHERENCE = "adherence"
    RELEVANCY = "relevancy"


@dataclass
class InputGuardrailsAdditionalConfig(BaseDTO):
    pii_redaction: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pii_redaction": self.pii_redaction
        }


@dataclass
class OutputGuardrailsAdditionalConfig(BaseDTO):
    hallucination: bool = False
    adherence: bool = False
    relevancy: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hallucination": self.hallucination,
            "adherence": self.adherence,
            "relevancy": self.relevancy
        }


@dataclass
class InputGuardrailsPolicy(BaseDTO):
    policy_name: str
    enabled: bool
    block: List[InputGuardrailBlockType] = field(default_factory=list)
    additional_config: InputGuardrailsAdditionalConfig = field(default_factory=InputGuardrailsAdditionalConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InputGuardrailsPolicy":
        # Convert string values to enum values
        block_items = []
        for item in data.get("block", []):
            try:
                block_items.append(InputGuardrailBlockType(item))
            except ValueError:
                raise ValueError(f"Invalid input guardrail block type: {item}")
                
        additional_config_data = data.get("additional_config", {})
        if not isinstance(additional_config_data, dict):
            additional_config_data = {}
            
        return cls(
            policy_name=data.get("policy_name", ""),
            enabled=data.get("enabled", False),
            block=block_items,
            additional_config=InputGuardrailsAdditionalConfig(
                pii_redaction=additional_config_data.get("pii_redaction", False)
            )
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "enabled": self.enabled,
            "block": [item.value for item in self.block],
            "additional_config": self.additional_config.to_dict()
        }


@dataclass
class OutputGuardrailsPolicy(BaseDTO):
    policy_name: str
    enabled: bool
    block: List[OutputGuardrailBlockType] = field(default_factory=list)
    additional_config: OutputGuardrailsAdditionalConfig = field(default_factory=OutputGuardrailsAdditionalConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OutputGuardrailsPolicy":
        # Convert string values to enum values
        block_items = []
        for item in data.get("block", []):
            try:
                block_items.append(OutputGuardrailBlockType(item))
            except ValueError:
                raise ValueError(f"Invalid output guardrail block type: {item}")
                
        additional_config_data = data.get("additional_config", {})
        if not isinstance(additional_config_data, dict):
            additional_config_data = {}
            
        return cls(
            policy_name=data.get("policy_name", ""),
            enabled=data.get("enabled", False),
            block=block_items,
            additional_config=OutputGuardrailsAdditionalConfig(
                hallucination=additional_config_data.get("hallucination", False),
                adherence=additional_config_data.get("adherence", False),
                relevancy=additional_config_data.get("relevancy", False)
            )
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "enabled": self.enabled,
            "block": [item.value for item in self.block],
            "additional_config": self.additional_config.to_dict()
        }


@dataclass
class DeploymentInput(BaseDTO):
    name: str
    model_saved_name: str
    model_version: str
    input_guardrails_policy: InputGuardrailsPolicy
    output_guardrails_policy: OutputGuardrailsPolicy
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeploymentInput":
        input_policy_data = data.get("input_guardrails_policy", {})
        output_policy_data = data.get("output_guardrails_policy", {})
        
        return cls(
            name=data.get("name", ""),
            model_saved_name=data.get("model_saved_name", ""),
            model_version=data.get("model_version", ""),
            input_guardrails_policy=InputGuardrailsPolicy.from_dict(input_policy_data),
            output_guardrails_policy=OutputGuardrailsPolicy.from_dict(output_policy_data)
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "model_saved_name": self.model_saved_name,
            "model_version": self.model_version,
            "input_guardrails_policy": self.input_guardrails_policy.to_dict(),
            "output_guardrails_policy": self.output_guardrails_policy.to_dict()
        }
        # result.update(self._extra_fields)
        return result


@dataclass
class GetDeploymentResponse(BaseDTO):
    name: str
    model_saved_name: str
    model_version: str
    input_guardrails_policy: InputGuardrailsPolicy
    output_guardrails_policy: OutputGuardrailsPolicy
    created_at: str
    updated_at: str
    created_by: str
    updated_by: str
    deployment_id: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetDeploymentResponse":
        input_policy_data = data.get("input_guardrails_policy", {})
        output_policy_data = data.get("output_guardrails_policy", {})
        
        return cls(
            name=data.get("name", ""),
            model_saved_name=data.get("model_saved_name", ""),
            model_version=data.get("model_version", ""),
            input_guardrails_policy=InputGuardrailsPolicy.from_dict(input_policy_data),
            output_guardrails_policy=OutputGuardrailsPolicy.from_dict(output_policy_data),
            updated_at=data.get("updated_at", ""),
            deployment_id=data.get("deployment_id", 0),
            created_at=data.get("created_at", ""),
            created_by=data.get("created_by", ""),
            updated_by=data.get("updated_by", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model_saved_name": self.model_saved_name,
            "model_version": self.model_version,
            "input_guardrails_policy": self.input_guardrails_policy.to_dict(),
            "output_guardrails_policy": self.output_guardrails_policy.to_dict(),
            "updated_at": self.updated_at,
            "deployment_id": self.deployment_id,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }


@dataclass
class DeploymentAddTaskResponse(BaseDTO):
    message: str
    data: GetDeploymentResponse
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeploymentAddTaskResponse":
        response_data = data.get("data", {})
        return cls(
            message=data.get("message", ""),
            data=GetDeploymentResponse.from_dict(response_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "data": self.data.to_dict()
        }


@dataclass
class ModifyDeploymentResponse(BaseDTO):
    message: str
    data: GetDeploymentResponse

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModifyDeploymentResponse":
        response_data = data.get("data", {})
        return cls(
            message=data.get("message", ""),
            data=GetDeploymentResponse.from_dict(response_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "data": self.data.to_dict()
        }


@dataclass
class DeleteDeploymentData(BaseDTO):
    deployment_id: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteDeploymentData":
        return cls(
            deployment_id=int(data.get("deployment_id", 0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployment_id": self.deployment_id
        }


@dataclass
class DeleteDeploymentResponse(BaseDTO):
    message: str
    data: DeleteDeploymentData
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteDeploymentResponse":
        response_data = data.get("data", {})
        return cls(
            message=data.get("message", ""),
            data=DeleteDeploymentData.from_dict(response_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "data": self.data.to_dict()
        }
    
    @property
    def deployment_id(self) -> int:
        """Convenience property to access the deployment_id directly."""
        return self.data.deployment_id


@dataclass
class DeploymentSummary(BaseDTO):
    deployment_id: int
    name: str
    created_at: str
    updated_at: str
    created_by: str
    updated_by: str
    model_saved_name: str
    model_version: str
    project_name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeploymentSummary":
        return cls(
            deployment_id=int(data.get("deployment_id", 0)),
            name=data.get("name", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            created_by=data.get("created_by", ""),
            updated_by=data.get("updated_by", ""),
            model_saved_name=data.get("model_saved_name", ""),
            model_version=data.get("model_version", ""),
            project_name=data.get("project_name", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployment_id": self.deployment_id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "model_saved_name": self.model_saved_name,
            "model_version": self.model_version,
            "project_name": self.project_name
        }


@dataclass
class DeploymentCollection(BaseDTO):
    deployments: List[DeploymentSummary] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeploymentCollection":
        deployments_data = data.get("deployments", [])
        return cls(
            deployments=[DeploymentSummary.from_dict(item) for item in deployments_data]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployments": [deployment.to_dict() for deployment in self.deployments]
        }
