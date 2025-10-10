import pandas as pd
from enum import Enum
from .base import BaseDTO
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from .datasets import DatasetConfig
from .models import ModelConfig
from .guardrails import GuardrailDetectors
from .common import ModelAuthTypeEnum, CustomHeader, ModelJwtConfig

# The risk mitigation do not support all detectors, so we need to create a separate enum for them.
class RiskGuardrailDetectorsEnum(str, Enum):
    NSFW = "nsfw"
    TOXICITY = "toxicity"
    INJECTION_ATTACK = "injection_attack"
    POLICY_VIOLATION = "policy_violation"
    BIAS = "bias"
    # Topic, Keyword, PII are not supported by Risk Mitigation
    # Below are not yet supported by Guardrails. So, also not supported by Risk Mitigation.
    # COPYRIGHT_IP = "copyright_ip"
    # SYSTEM_PROMPT = "system_prompt"
    # SPONGE_ATTACK = "sponge_attack"


@dataclass
class RedteamHealthResponse(BaseDTO):
    status: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedteamHealthResponse":
        return cls(
            status=data.get("status", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status
        }


@dataclass
class RedTeamResponse(BaseDTO):
    status: Optional[str] = None
    task_id: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamResponse":
        return cls(
            task_id=data.get("task_id"),
            message=data.get("message"),
            data=data.get("data"),
        )
    
    def to_dict(self) -> Dict:
        return super().to_dict()


@dataclass
class RedTeamTaskStatus(BaseDTO):
    status: Optional[str] = None


@dataclass
class RedTeamTaskDetailsModelConfig(BaseDTO):
    system_prompt: Optional[str] = None
    model_version: Optional[str] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamTaskDetailsModelConfig":
        return cls(
            system_prompt=data.get("system_prompt"),
            model_version=data.get("model_version"),
        )
    
    def to_dict(self) -> Dict:
        return {
            "system_prompt": self.system_prompt,
            "model_version": self.model_version,
        }


@dataclass
class RedTeamTaskDetails(BaseDTO):
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    model_saved_name: Optional[str] = None
    model_name: Optional[str] = None
    status: Optional[str] = None
    test_name: Optional[str] = None
    task_id: Optional[str] = None
    model_config: Optional[RedTeamTaskDetailsModelConfig] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamTaskDetails":
        # print(f"RedTeamTaskDetails data: {data}")
        return cls(
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
            model_saved_name=data.get("model_saved_name"),
            model_name=data.get("model_name"),
            status=data.get("status"),
            test_name=data.get("test_name"),
            task_id=data.get("task_id"),
            model_config=RedTeamTaskDetailsModelConfig.from_dict(data.get("model_config", {})),
        )
    
    def to_dict(self) -> Dict:
        return {
            "created_at": self.created_at,
            "created_by": self.created_by,
            "model_saved_name": self.model_saved_name,
            "model_name": self.model_name,
            "status": self.status,
            "test_name": self.test_name,
            "task_id": self.task_id,
            "model_config": self.model_config.to_dict(),
        }


@dataclass
class StatisticItem(BaseDTO):
    success_percentage: float
    total: int
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "StatisticItem":
        return cls(
            success_percentage=data.get("success(%)", 0.0), total=data.get("total", 0)
        )

    def to_dict(self) -> Dict:
        d = super().to_dict()
        # Special handling for success percentage key
        d["success(%)"] = d.pop("success_percentage")
        return d


@dataclass
class StatisticItemWithTestType(BaseDTO):
    success_percentage: float
    total: int
    test_type: Optional[str] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "StatisticItemWithTestType":
        return cls(
            success_percentage=data.get("success(%)", 0.0),
            total=data.get("total", 0),
            test_type=data.get("test_type", None),
        )

    def to_dict(self) -> Dict:
        d = super().to_dict()
        # Special handling for success percentage key
        d["success(%)"] = d.pop("success_percentage")
        return d


@dataclass
class ResultSummary(BaseDTO):
    test_date: str
    test_name: str
    dataset_name: str
    model_endpoint_url: str
    model_source: str
    model_provider: str
    risk_score: float
    model_name: Optional[str]
    test_type: Dict[str, StatisticItem]
    nist_category: Dict[str, StatisticItem]
    scenario: Dict[str, StatisticItem]
    category: Dict[str, StatisticItemWithTestType]
    attack_method: Dict[str, StatisticItem]
    custom_test_category_risks: Dict[str, StatisticItem] = field(default_factory=dict)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "ResultSummary":
        def convert_stat_list(stat_list: List[Dict]) -> Dict[str, StatisticItem]:
            result = {}
            for item in stat_list:
                for key, value in item.items():
                    result[key] = StatisticItem.from_dict(value)
            return result
        
        def convert_stat_test_type_list(stat_list: List[Dict]) -> Dict[str, StatisticItemWithTestType]:
            result = {}
            for item in stat_list:
                for key, value in item.items():
                    result[key] = StatisticItemWithTestType.from_dict(value)
            return result

        return cls(
            test_date=data.get("test_date", ""),
            test_name=data.get("test_name", ""),
            dataset_name=data.get("dataset_name", ""),
            model_name=data.get("model_name", ""),
            model_endpoint_url=data.get("model_endpoint_url", ""),
            model_source=data.get("model_source", ""),
            model_provider=data.get("model_provider", ""),
            risk_score=data.get("risk_score", 0.0),
            test_type=convert_stat_list(data.get("test_type", [])),
            nist_category=convert_stat_list(data.get("nist_category", [])),
            scenario=convert_stat_list(data.get("scenario", [])),
            category=convert_stat_test_type_list(data.get("category", [])),
            attack_method=convert_stat_list(data.get("attack_method", [])),
            custom_test_category_risks=convert_stat_list(
                data.get("custom_test_category_risks", [])
            ),
        )

    def to_dict(self) -> Dict:
        def convert_stat_dict(stat_dict: Dict[str, StatisticItem]) -> List[Dict]:
            return [{key: value.to_dict()} for key, value in stat_dict.items()]
        
        def convert_stat_test_type_dict(stat_dict: Dict[str, StatisticItemWithTestType]) -> List[Dict]:
            return [{key: value.to_dict()} for key, value in stat_dict.items()]

        d = super().to_dict()
        # Convert stat dictionaries to lists of dictionaries
        d["test_type"] = convert_stat_dict(self.test_type)
        d["nist_category"] = convert_stat_dict(self.nist_category)
        d["scenario"] = convert_stat_dict(self.scenario)
        d["category"] = convert_stat_test_type_dict(self.category)
        d["attack_method"] = convert_stat_dict(self.attack_method)
        d["custom_test_category_risks"] = convert_stat_dict(
            self.custom_test_category_risks
        )
        return d


@dataclass
class RedTeamResultSummary(BaseDTO):
    summary: ResultSummary
    task_status: Optional[str] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamResultSummary":
        if not data or "summary" not in data:
            return cls(summary=ResultSummary.from_dict({}))
        
        if "task_status" in data:
            return cls(summary=ResultSummary.from_dict({}), task_status=data["task_status"])

        return cls(summary=ResultSummary.from_dict(data["summary"]))

    def to_dict(self) -> Dict:
        return {"summary": self.summary.to_dict()}


@dataclass
class TestEvalTokens(BaseDTO):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult(BaseDTO):
    prompt: str
    category: str
    test_type: str
    nist_category: str
    source: str
    attack_method: str
    jailbreak_prompt: str
    response: str
    success: str
    reasoning: str
    detected_language: str
    eval_latency: float
    eval_tokens: TestEvalTokens
    test_name: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RedTeamResultDetails(BaseDTO):
    details: List[TestResult]
    task_status: Optional[str] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamResultDetails":
        if not data or "details" not in data:
            return cls(details=[])
        
        if "task_status" in data:
            return cls(details=[], task_status=data["task_status"])

        # details = []
        # for result in data["details"]:
            # Convert eval_tokens dict to TestEvalTokens object
            # eval_tokens = TestEvalTokens(**result["eval_tokens"])

            # Create a copy of the result dict and replace eval_tokens
            # result_copy = dict(result["details"])
            # result_copy["eval_tokens"] = eval_tokens

            # Create TestResult object
            # test_result = TestResult(**result_copy)
            # details.append(test_result)

        return cls(details=data["details"])

    def to_dict(self) -> Dict:
        return {
            # "details": [
            #     {**result.to_dict(), "eval_tokens": result.eval_tokens.to_dict()}
            #     for result in self.details
            # ]
            "details": self.details
        }

    # def to_dataframe(self) -> pd.DataFrame:
    #     data = [
    #         {**result.to_dict(), "eval_tokens": result.eval_tokens.to_dict()}
    #         for result in self.details
    #     ]
    #     return pd.DataFrame(data)


@dataclass
class AttackMethods(BaseDTO):
    basic: List[str] = field(default_factory=lambda: ["basic"])
    advanced: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "static": ["masking", "figstep", "hades","encoding", "single_shot", "echo", "speed", "pitch", "reverb", "noise" ],
            "dynamic": ["iterative","jood"]
        }
    )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class TestConfig(BaseDTO):
    sample_percentage: int = 5
    attack_methods: AttackMethods = field(default_factory=AttackMethods)

    def to_dict(self) -> dict:
        return {
            "sample_percentage": self.sample_percentage,
            "attack_methods": self.attack_methods.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        attack_methods = AttackMethods.from_dict(data.pop("attack_methods", {}))
        return cls(**data, attack_methods=attack_methods)


@dataclass
class CompetitorTestConfig(BaseDTO):
    system_description: str
    competitors_list: List[str]
    sample_percentage: int = 1
    attack_methods: AttackMethods = field(default_factory=AttackMethods)

    def to_dict(self) -> dict:
        return {
            "sample_percentage": self.sample_percentage,
            "competitors_list": self.competitors_list,
            "system_description": self.system_description,
            "attack_methods": self.attack_methods.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        attack_methods = AttackMethods.from_dict(data.pop("attack_methods", {}))
        return cls(**data, attack_methods=attack_methods)


@dataclass
class RedTeamTestConfigurations(BaseDTO):
    # Basic tests
    bias_test: TestConfig = field(default=None)
    cbrn_test: TestConfig = field(default=None)
    csem_test: TestConfig = field(default=None)
    insecure_code_test: TestConfig = field(default=None)
    toxicity_test: TestConfig = field(default=None)
    harmful_test: TestConfig = field(default=None)
    pii_test: TestConfig = field(default=None)
    copyright_test: TestConfig = field(default=None)
    misinformation_test: TestConfig = field(default=None)
    system_prompt_extractions_test: TestConfig = field(default=None)
    sponge_test: TestConfig = field(default=None)
    competitor_test: CompetitorTestConfig = field(default=None)
    # Advanced tests
    adv_info_test: TestConfig = field(default=None)
    adv_bias_test: TestConfig = field(default=None)
    adv_tool_test: TestConfig = field(default=None)
    adv_command_test: TestConfig = field(default=None)
    adv_pii_test: TestConfig = field(default=None)
    adv_competitor_test: TestConfig = field(default=None)
    # Custom tests
    custom_test: TestConfig = field(default=None)
    # Agents tests
    alignment_and_governance_test: TestConfig = field(default=None)
    input_and_content_integrity_test: TestConfig = field(default=None)
    infrastructure_and_integration_test: TestConfig = field(default=None)
    security_and_privacy_test: TestConfig = field(default=None)
    human_factors_and_societal_impact_test: TestConfig = field(default=None)
    access_control_test: TestConfig = field(default=None)
    physical_and_actuation_safety_test: TestConfig = field(default=None)
    reliability_and_monitoring_test: TestConfig = field(default=None)
    governance_test: TestConfig = field(default=None)
    agent_output_quality_test: TestConfig = field(default=None)
    tool_misuse_test: TestConfig = field(default=None)
    privacy_test: TestConfig = field(default=None)
    reliability_and_observability_test: TestConfig = field(default=None)
    agent_behaviour_test: TestConfig = field(default=None)
    access_control_and_permissions_test: TestConfig = field(default=None)
    tool_extraction_test: TestConfig = field(default=None)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: TestConfig.from_dict(v) for k, v in data.items()})


class InputModality(str, Enum):
    text = "text"
    image = "image"
    audio = "audio"
    # video = "video"
    # code = "code"


class OutputModality(str, Enum):
    text = "text"
    # image = "image"
    # audio = "audio"
    # video = "video"
    # code = "code"
    

@dataclass
class TargetModelConfiguration(BaseDTO):
    testing_for: str = "foundationModels"
    system_prompt: str = ""
    model_source: str = ""
    model_provider: str = "openai"
    model_endpoint_url: str = "https://api.openai.com/v1/chat/completions"
    rate_per_min: int = 20
    model_name: Optional[str] = "gpt-4o-mini"
    model_version: Optional[str] = None
    model_auth_type: Optional[ModelAuthTypeEnum] = ModelAuthTypeEnum.APIKEY
    model_jwt_config: Optional[ModelJwtConfig] = None
    model_api_key: Optional[str] = None
    input_modalities: List[InputModality] = field(default_factory=list)
    output_modalities: List[OutputModality] = field(default_factory=list)
    custom_curl_command: Optional[str] = None
    custom_headers: List[CustomHeader] = field(default_factory=list)
    custom_payload: Dict[str, Any] = field(default_factory=dict)
    custom_response_content_type: Optional[str] = ""
    custom_response_format: Optional[str] = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        if "custom_headers" in data:
            data["custom_headers"] = [CustomHeader.from_dict(header) for header in data["custom_headers"]]
        if "model_auth_type" in data:
            data["model_auth_type"] = ModelAuthTypeEnum(data["model_auth_type"])
        if "model_jwt_config" in data:
            data["model_jwt_config"] = ModelJwtConfig.from_dict(data["model_jwt_config"])
        return cls(**data)
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d["model_auth_type"] = self.model_auth_type.value
        if self.model_jwt_config:
            d["model_jwt_config"] = self.model_jwt_config.to_dict()
        d["custom_headers"] = [header.to_dict() for header in self.custom_headers]
        return d


@dataclass
class RedTeamModelHealthConfig(BaseDTO):
    target_model_configuration: TargetModelConfiguration = field(
        default_factory=TargetModelConfiguration
    )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["target_model_configuration"] = self.target_model_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        target_config = TargetModelConfiguration.from_dict(
            data.pop("target_model_configuration", {})
        )
        return cls(
            # **data,
            target_model_configuration=target_config,
        )


@dataclass
class RedTeamModelHealthConfigV3(BaseDTO):
    """
    V3 format for model health check that accepts endpoint_configuration
    similar to add_custom_task.
    """
    endpoint_configuration: ModelConfig = field(
        default_factory=ModelConfig
    )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["endpoint_configuration"] = self.endpoint_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        endpoint_config = ModelConfig.from_dict(
            data.pop("endpoint_configuration", {})
        )
        return cls(
            endpoint_configuration=endpoint_config,
        )
    
    def to_target_model_configuration(self) -> TargetModelConfiguration:
        """
        Convert endpoint_configuration to target_model_configuration format.
        This enables the V3 format to be compatible with the existing backend API.
        """
        model_config = self.endpoint_configuration.model_config
        
        return TargetModelConfiguration(
            testing_for=self.endpoint_configuration.testing_for,
            system_prompt=model_config.system_prompt,
            model_source=model_config.model_source,
            model_provider=model_config.model_provider.value if hasattr(model_config.model_provider, 'value') else model_config.model_provider,
            model_endpoint_url=model_config.endpoint_url,
            rate_per_min=model_config.rate_per_min,
            model_name=self.endpoint_configuration.model_name,
            model_version=self.endpoint_configuration.model_version,
            model_auth_type=model_config.model_auth_type,
            model_jwt_config=model_config.model_jwt_config,
            model_api_key=model_config.apikey,
            input_modalities=[InputModality(m) if isinstance(m, str) else m for m in model_config.input_modalities],
            output_modalities=[OutputModality(m) if isinstance(m, str) else m for m in model_config.output_modalities],
            custom_curl_command=model_config.custom_curl_command,
            custom_headers=model_config.custom_headers,
            custom_payload=model_config.custom_payload,
            custom_response_content_type=model_config.custom_response_content_type,
            custom_response_format=model_config.custom_response_format,
        )


@dataclass
class RedteamModelHealthResponse(BaseDTO):
    status: str
    message: str
    error: str
    data: Optional[Dict[str, Any]] = field(default_factory=dict)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedteamModelHealthResponse":
        return cls(
            status=data.get("status", ""),
            message=data.get("message", ""),
            data=data.get("data", {}),
            error=data.get("error", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "error": self.error
        }


@dataclass
class RedTeamConfig(BaseDTO):
    test_name: str = "Test Name"
    dataset_name: str = "standard"

    redteam_test_configurations: RedTeamTestConfigurations = field(
        default_factory=RedTeamTestConfigurations
    )
    target_model_configuration: TargetModelConfiguration = field(
        default_factory=TargetModelConfiguration
    )

    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
        d["target_model_configuration"] = self.target_model_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        test_configs = RedTeamTestConfigurations.from_dict(
            data.pop("redteam_test_configurations", {})
        )
        target_config = TargetModelConfiguration.from_dict(
            data.pop("target_model_configuration", {})
        )
        return cls(
            **data,
            redteam_test_configurations=test_configs,
            target_model_configuration=target_config,
        )


@dataclass
class RedTeamConfigWithSavedModel(BaseDTO):
    test_name: str = "Test Name"
    dataset_name: str = "standard"
    model_saved_name: str = "gpt-4o-mini"
    model_version: str = "v1"

    redteam_test_configurations: RedTeamTestConfigurations = field(
        default_factory=RedTeamTestConfigurations
    )

    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        test_configs = RedTeamTestConfigurations.from_dict(
            data.pop("redteam_test_configurations", {})
        )
        return cls(
            **data,
            redteam_test_configurations=test_configs,
        )


@dataclass
class RedTeamCustomConfig(BaseDTO):
    test_name: str = "Test Name"
    frameworks: List[str] = field(default_factory=list)

    redteam_test_configurations: RedTeamTestConfigurations = field(
        default_factory=RedTeamTestConfigurations
    )
    dataset_configuration: DatasetConfig = field(
        default_factory=DatasetConfig
    )
    endpoint_configuration: ModelConfig = field(
        default_factory=ModelConfig
    )

    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
        d["dataset_configuration"] = self.dataset_configuration.to_dict()
        d["endpoint_configuration"] = self.endpoint_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        test_configs = RedTeamTestConfigurations.from_dict(
            data.pop("redteam_test_configurations", {})
        )
        dataset_config = DatasetConfig.from_dict(
            data.pop("dataset_configuration", {})
        )
        endpoint_config = ModelConfig.from_dict(
            data.pop("endpoint_configuration", {})
        )
        return cls(
            **data,
            redteam_test_configurations=test_configs,
            dataset_configuration=dataset_config,
            endpoint_configuration=endpoint_config,
        )

@dataclass
class RedTeamCustomConfigWithSavedModel(BaseDTO):
    test_name: str = "Test Name"
    frameworks: List[str] = field(default_factory=list)

    redteam_test_configurations: RedTeamTestConfigurations = field(
        default_factory=RedTeamTestConfigurations
    )
    dataset_configuration: DatasetConfig = field(
        default_factory=DatasetConfig
    )

    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
        d["dataset_configuration"] = self.dataset_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        test_configs = RedTeamTestConfigurations.from_dict(
            data.pop("redteam_test_configurations", {})
        )
        dataset_config = DatasetConfig.from_dict(
            data.pop("dataset_configuration", {})
        )
        return cls(
            **data,
            redteam_test_configurations=test_configs,
            dataset_configuration=dataset_config,
        )


@dataclass
class RedTeamTaskList(BaseDTO):
    tasks: List[RedTeamTaskDetails] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        data = [task for task in self.tasks]
        return pd.DataFrame(data)
    

@dataclass
class RedTeamRiskMitigationGuardrailsPolicyConfig(BaseDTO):
    # required_detectors: List[RiskGuardrailDetectorsEnum] = field(default_factory=list)
    redteam_summary: ResultSummary = field(default_factory=ResultSummary)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        summary = ResultSummary.from_dict(data.pop("redteam_summary", {}))
        return cls(
            # required_detectors=[RiskGuardrailDetectorsEnum(detector) for detector in data.get("required_detectors", [])],
            redteam_summary=summary,
            _extra_fields=data,
        )

    def to_dict(self) -> dict:
        return {
            # "required_detectors": [detector.value for detector in self.required_detectors],
            "redteam_summary": self.redteam_summary.to_dict(),
        }


@dataclass
class RedTeamRiskMitigationGuardrailsPolicyResponse(BaseDTO):
    analysis: str = ""
    guardrails_policy: GuardrailDetectors = field(default_factory=GuardrailDetectors)
    message: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        policy_data = data.get("guardrails_policy", {})

        return cls(
            analysis=data.get("analysis", ""),
            guardrails_policy=GuardrailDetectors.from_dict(policy_data),
            message=data.get("message", ""),
        )

    def to_dict(self) -> dict:
        policy_dict = self.guardrails_policy.to_dict()
        
        # Remove detector entries that are disabled and have no other config
        final_policy_dict = {}
        for key, value in policy_dict.items():
            if isinstance(value, dict):
                # Check if 'enabled' is the only key and its value is False
                if list(value.keys()) == ['enabled'] and not value['enabled']:
                    continue
                # Check for empty detectors that only have 'enabled': False
                if not value.get("enabled", True) and len(value) == 1:
                    continue
                # check for other empty values
                if not any(v for k, v in value.items() if k != 'enabled'):
                     if not value.get('enabled'):
                         continue
                final_policy_dict[key] = value

        return {
            "analysis": self.analysis,
            "guardrails_policy": final_policy_dict,
            "message": self.message,
        }


@dataclass
class RedTeamRiskMitigationSystemPromptConfig(BaseDTO):
    system_prompt: str = "You are a helpful AI Assistant"
    redteam_summary: ResultSummary = field(default_factory=ResultSummary)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        summary = ResultSummary.from_dict(data.pop("redteam_summary", {}))
        return cls(
            system_prompt=data.get("system_prompt", ""),
            redteam_summary=summary,
            _extra_fields=data,
        )

    def to_dict(self) -> dict:
        return {
            "system_prompt": self.system_prompt,
            "redteam_summary": self.redteam_summary.to_dict(),
        }


@dataclass
class RedTeamRiskMitigationSystemPromptResponse(BaseDTO):
    analysis: str = ""
    system_prompt: str = ""
    message: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            analysis=data.get("analysis", ""),
            system_prompt=data.get("system_prompt", ""),
            message=data.get("message", ""),
        )

    def to_dict(self) -> dict:
        return {
            "analysis": self.analysis,
            "system_prompt": self.system_prompt,
            "message": self.message,
        }

@dataclass
class RedTeamKeyFinding(BaseDTO):
    text: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedTeamKeyFinding":
        return cls(
            text=data.get("text", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "text": self.text
        }
        result.update(self._extra_fields)
        return result


@dataclass
class RedTeamFindingsResponse(BaseDTO):
    key_findings: List[RedTeamKeyFinding] = field(default_factory=list)
    message: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedTeamFindingsResponse":
        key_findings_data = data.get("key_findings", [])
        key_findings = [RedTeamKeyFinding.from_dict(finding) for finding in key_findings_data]
        
        return cls(
            key_findings=key_findings,
            message=data.get("message", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "key_findings": [finding.to_dict() for finding in self.key_findings],
            "message": self.message
        }
        result.update(self._extra_fields)
        return result


@dataclass
class RedTeamDownloadLinkResponse(BaseDTO):
    link: str = ""
    expiry: str = ""
    expires_at: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedTeamDownloadLinkResponse":
        return cls(
            link=data.get("link", ""),
            expiry=data.get("expiry", ""),
            expires_at=data.get("expires_at", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "link": self.link,
            "expiry": self.expiry,
            "expires_at": self.expires_at
        }
        result.update(self._extra_fields)
        return result


# V3 Attack Methods and Test Configurations
@dataclass
class AttackMethodsV3(BaseDTO):
    """
    V3 format for attack methods with nested structure:
    {
        "method_category": {
            "method_name": {
                "params": {}
            }
        }
    }
    """
    _data: Dict[str, Dict[str, Dict[str, Any]]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return self._data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(_data=data)


@dataclass
class TestConfigV3(BaseDTO):
    sample_percentage: int = 5
    attack_methods: AttackMethodsV3 = field(default_factory=AttackMethodsV3)

    def to_dict(self) -> dict:
        return {
            "sample_percentage": self.sample_percentage,
            "attack_methods": self.attack_methods.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        attack_methods = AttackMethodsV3.from_dict(data.get("attack_methods", {}))
        return cls(
            sample_percentage=data.get("sample_percentage", 5),
            attack_methods=attack_methods
        )


@dataclass
class RedTeamTestConfigurationsV3(BaseDTO):
    """V3 format for red team test configurations with nested attack methods"""
    # Basic tests
    bias_test: TestConfigV3 = field(default=None)
    cbrn_test: TestConfigV3 = field(default=None)
    csem_test: TestConfigV3 = field(default=None)
    insecure_code_test: TestConfigV3 = field(default=None)
    toxicity_test: TestConfigV3 = field(default=None)
    harmful_test: TestConfigV3 = field(default=None)
    pii_test: TestConfigV3 = field(default=None)
    copyright_test: TestConfigV3 = field(default=None)
    misinformation_test: TestConfigV3 = field(default=None)
    system_prompt_extractions_test: TestConfigV3 = field(default=None)
    sponge_test: TestConfigV3 = field(default=None)
    # Advanced tests
    adv_info_test: TestConfigV3 = field(default=None)
    adv_bias_test: TestConfigV3 = field(default=None)
    adv_tool_test: TestConfigV3 = field(default=None)
    adv_command_test: TestConfigV3 = field(default=None)
    adv_pii_test: TestConfigV3 = field(default=None)
    adv_competitor_test: TestConfigV3 = field(default=None)
    # Custom tests
    custom_test: TestConfigV3 = field(default=None)
    # Agents tests
    alignment_and_governance_test: TestConfigV3 = field(default=None)
    input_and_content_integrity_test: TestConfigV3 = field(default=None)
    infrastructure_and_integration_test: TestConfigV3 = field(default=None)
    security_and_privacy_test: TestConfigV3 = field(default=None)
    human_factors_and_societal_impact_test: TestConfigV3 = field(default=None)
    access_control_test: TestConfigV3 = field(default=None)
    physical_and_actuation_safety_test: TestConfigV3 = field(default=None)
    reliability_and_monitoring_test: TestConfigV3 = field(default=None)
    governance_test: TestConfigV3 = field(default=None)
    agent_output_quality_test: TestConfigV3 = field(default=None)
    tool_misuse_test: TestConfigV3 = field(default=None)
    privacy_test: TestConfigV3 = field(default=None)
    reliability_and_observability_test: TestConfigV3 = field(default=None)
    agent_behaviour_test: TestConfigV3 = field(default=None)
    access_control_and_permissions_test: TestConfigV3 = field(default=None)
    tool_extraction_test: TestConfigV3 = field(default=None)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: TestConfigV3.from_dict(v) if isinstance(v, dict) else v for k, v in data.items()})


@dataclass
class RedTeamCustomConfigV3(BaseDTO):
    test_name: str = "Test Name"
    frameworks: List[str] = field(default_factory=list)

    redteam_test_configurations: RedTeamTestConfigurationsV3 = field(
        default_factory=RedTeamTestConfigurationsV3
    )
    dataset_configuration: DatasetConfig = field(
        default_factory=DatasetConfig
    )
    endpoint_configuration: ModelConfig = field(
        default_factory=ModelConfig
    )

    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
        d["dataset_configuration"] = self.dataset_configuration.to_dict()
        d["endpoint_configuration"] = self.endpoint_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        test_configs = RedTeamTestConfigurationsV3.from_dict(
            data.pop("redteam_test_configurations", {})
        )
        dataset_config = DatasetConfig.from_dict(
            data.pop("dataset_configuration", {})
        )
        endpoint_config = ModelConfig.from_dict(
            data.pop("endpoint_configuration", {})
        )
        return cls(
            **data,
            redteam_test_configurations=test_configs,
            dataset_configuration=dataset_config,
            endpoint_configuration=endpoint_config,
        )


@dataclass
class RedTeamCustomConfigWithSavedModelV3(BaseDTO):
    test_name: str = "Test Name"
    frameworks: List[str] = field(default_factory=list)

    redteam_test_configurations: RedTeamTestConfigurationsV3 = field(
        default_factory=RedTeamTestConfigurationsV3
    )
    dataset_configuration: DatasetConfig = field(
        default_factory=DatasetConfig
    )

    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
        d["dataset_configuration"] = self.dataset_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        test_configs = RedTeamTestConfigurationsV3.from_dict(
            data.pop("redteam_test_configurations", {})
        )
        dataset_config = DatasetConfig.from_dict(
            data.pop("dataset_configuration", {})
        )
        return cls(
            **data,
            redteam_test_configurations=test_configs,
            dataset_configuration=dataset_config,
        )


# Default configurations
DEFAULT_REDTEAM_CONFIG = RedTeamConfig()
DEFAULT_REDTEAM_CONFIG_WITH_SAVED_MODEL = RedTeamConfigWithSavedModel()

DEFAULT_CUSTOM_REDTEAM_CONFIG = RedTeamCustomConfig()
DEFAULT_CUSTOM_REDTEAM_CONFIG_WITH_SAVED_MODEL = RedTeamCustomConfigWithSavedModel()

DEFAULT_CUSTOM_REDTEAM_CONFIG_V3 = RedTeamCustomConfigV3()
DEFAULT_CUSTOM_REDTEAM_CONFIG_WITH_SAVED_MODEL_V3 = RedTeamCustomConfigWithSavedModelV3()
