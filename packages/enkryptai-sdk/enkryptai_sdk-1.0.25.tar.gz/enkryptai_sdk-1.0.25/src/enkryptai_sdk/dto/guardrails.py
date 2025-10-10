from enum import Enum
from .base import BaseDTO
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Optional, BinaryIO

class GuardrailsPIIModes(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"


@dataclass
class GuardrailsHealthResponse(BaseDTO):
    status: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsHealthResponse":
        return cls(
            status=data.get("status", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status
        }


@dataclass
class GuardrailsModelsResponse(BaseDTO):
    models: List[str] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsModelsResponse":
        return cls(
            models=data.get("models", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "models": self.models
        }


# -------------------------------------
# Guardrails Detect Request
# -------------------------------------


@dataclass
class TopicDetector(BaseDTO):
    enabled: bool = False
    topic: List[str] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopicDetector":
        return cls(
            enabled=data.get("enabled", False),
            topic=data.get("topic", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "topic": self.topic
        }


@dataclass
class NSFWDetector(BaseDTO):
    enabled: bool = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NSFWDetector":
        return cls(
            enabled=data.get("enabled", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled
        }


@dataclass
class ToxicityDetector(BaseDTO):
    enabled: bool = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToxicityDetector":
        return cls(
            enabled=data.get("enabled", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled
        }


@dataclass
class PIIDetector(BaseDTO):
    enabled: bool = False
    entities: List[str] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PIIDetector":
        return cls(
            enabled=data.get("enabled", False),
            entities=data.get("entities", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "entities": self.entities
        }


@dataclass
class InjectionAttackDetector(BaseDTO):
    enabled: bool = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InjectionAttackDetector":
        return cls(
            enabled=data.get("enabled", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled
        }


@dataclass
class KeywordDetector(BaseDTO):
    enabled: bool = False
    banned_keywords: List[str] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeywordDetector":
        return cls(
            enabled=data.get("enabled", False),
            banned_keywords=data.get("banned_keywords", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "banned_keywords": self.banned_keywords
        }


@dataclass
class PolicyViolationDetector(BaseDTO):
    enabled: bool = False
    policy_text: str = ""
    need_explanation: bool = False
    coc_policy_name: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyViolationDetector":
        return cls(
            enabled=data.get("enabled", False),
            policy_text=data.get("policy_text", ""),
            need_explanation=data.get("need_explanation", False),
            coc_policy_name=data.get("coc_policy_name", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        res_dict = {
            "enabled": self.enabled,
            "need_explanation": self.need_explanation
        }

        if self.policy_text:
            res_dict["policy_text"] = self.policy_text
        if self.coc_policy_name:
            res_dict["coc_policy_name"] = self.coc_policy_name

        return res_dict


@dataclass
class BiasDetector(BaseDTO):
    enabled: bool = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BiasDetector":
        return cls(
            enabled=data.get("enabled", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled
        }


@dataclass
class CopyrightIPDetector(BaseDTO):
    enabled: bool = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CopyrightIPDetector":
        return cls(
            enabled=data.get("enabled", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled
        }


@dataclass
class SystemPromptDetector(BaseDTO):
    enabled: bool = False
    index: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemPromptDetector":
        return cls(
            enabled=data.get("enabled", False),
            index=data.get("index", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "index": self.index
        }


@dataclass
class SpongeAttackDetector(BaseDTO):
    enabled: bool = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpongeAttackDetector":
        return cls(
            enabled=data.get("enabled", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled
        }


class GuardrailDetectorsEnum(str, Enum):
    TOPIC_DETECTOR = "topic_detector"
    NSFW = "nsfw"
    TOXICITY = "toxicity"
    PII = "pii"
    INJECTION_ATTACK = "injection_attack"
    KEYWORD_DETECTOR = "keyword_detector"
    POLICY_VIOLATION = "policy_violation"
    BIAS = "bias"
    COPYRIGHT_IP = "copyright_ip"
    SYSTEM_PROMPT = "system_prompt"
    SPONGE_ATTACK = "sponge_attack"


@dataclass
class GuardrailDetectors(BaseDTO):
    topic_detector: TopicDetector = field(default_factory=TopicDetector)
    nsfw: NSFWDetector = field(default_factory=NSFWDetector)
    toxicity: ToxicityDetector = field(default_factory=ToxicityDetector)
    pii: PIIDetector = field(default_factory=PIIDetector)
    injection_attack: InjectionAttackDetector = field(default_factory=InjectionAttackDetector)
    keyword_detector: KeywordDetector = field(default_factory=KeywordDetector)
    policy_violation: PolicyViolationDetector = field(default_factory=PolicyViolationDetector)
    bias: BiasDetector = field(default_factory=BiasDetector)
    copyright_ip: CopyrightIPDetector = field(default_factory=CopyrightIPDetector)
    system_prompt: SystemPromptDetector = field(default_factory=SystemPromptDetector)
    sponge_attack: SpongeAttackDetector = field(default_factory=SpongeAttackDetector)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailDetectors":
        return cls(
            topic_detector=TopicDetector.from_dict(data.get("topic_detector", {})),
            nsfw=NSFWDetector.from_dict(data.get("nsfw", {})),
            toxicity=ToxicityDetector.from_dict(data.get("toxicity", {})),
            pii=PIIDetector.from_dict(data.get("pii", {})),
            injection_attack=InjectionAttackDetector.from_dict(data.get("injection_attack", {})),
            keyword_detector=KeywordDetector.from_dict(data.get("keyword_detector", {})),
            policy_violation=PolicyViolationDetector.from_dict(data.get("policy_violation", {})),
            bias=BiasDetector.from_dict(data.get("bias", {})),
            copyright_ip=CopyrightIPDetector.from_dict(data.get("copyright_ip", {})),
            system_prompt=SystemPromptDetector.from_dict(data.get("system_prompt", {})),
            sponge_attack=SpongeAttackDetector.from_dict(data.get("sponge_attack", {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic_detector": self.topic_detector.to_dict(),
            "nsfw": self.nsfw.to_dict(),
            "toxicity": self.toxicity.to_dict(),
            "pii": self.pii.to_dict(),
            "injection_attack": self.injection_attack.to_dict(),
            "keyword_detector": self.keyword_detector.to_dict(),
            "policy_violation": self.policy_violation.to_dict(),
            "bias": self.bias.to_dict(),
            "copyright_ip": self.copyright_ip.to_dict(),
            "system_prompt": self.system_prompt.to_dict(),
            "sponge_attack": self.sponge_attack.to_dict()
        }


@dataclass
class GuardrailsDetectRequest(BaseDTO):
    text: str
    detectors: GuardrailDetectors = field(default_factory=GuardrailDetectors)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsDetectRequest":
        detectors_data = data.get("detectors", {})
        return cls(
            text=data.get("text", ""),
            detectors=GuardrailDetectors.from_dict(detectors_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "detectors": self.detectors.to_dict()
        }


@dataclass
class GuardrailsBatchDetectRequest(BaseDTO):
    texts: List[str] = field(default_factory=list)
    detectors: GuardrailDetectors = field(default_factory=GuardrailDetectors)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsBatchDetectRequest":
        detectors_data = data.get("detectors", {})
        return cls(
            texts=data.get("texts", []),
            detectors=GuardrailDetectors.from_dict(detectors_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "texts": self.texts,
            "detectors": self.detectors.to_dict()
        }


@dataclass
class GuardrailsPolicyDetectRequest(BaseDTO):
    text: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPolicyDetectRequest":
        return cls(
            text=data.get("text", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text
        }
    

# -------------------------------------
# Guardrails Detect Response
# -------------------------------------


@dataclass
class TopicDetectorDetail(BaseDTO):
    _extra_fields: Dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopicDetectorDetail":
        obj = cls()
        obj._extra_fields = {k: float(v) for k, v in data.items()}
        return obj
    
    def to_dict(self) -> Dict[str, Any]:
        return self._extra_fields


@dataclass
class NSFWDetail(BaseDTO):
    sfw: float = 0.0
    nsfw: float = 0.0
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NSFWDetail":
        return cls(
            sfw=float(data.get("sfw", 0.0)),
            nsfw=float(data.get("nsfw", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "sfw": self.sfw,
            "nsfw": self.nsfw
        }
        result.update(self._extra_fields)
        return result


@dataclass
class ToxicityDetail(BaseDTO):
    toxicity: float = 0.0
    severe_toxicity: float = 0.0
    obscene: float = 0.0
    threat: float = 0.0
    insult: float = 0.0
    identity_hate: float = 0.0
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToxicityDetail":
        return cls(
            toxicity=float(data.get("toxicity", 0.0)),
            severe_toxicity=float(data.get("severe_toxicity", 0.0)),
            obscene=float(data.get("obscene", 0.0)),
            threat=float(data.get("threat", 0.0)),
            insult=float(data.get("insult", 0.0)),
            identity_hate=float(data.get("identity_hate", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "toxicity": self.toxicity,
            "severe_toxicity": self.severe_toxicity,
            "obscene": self.obscene,
            "threat": self.threat,
            "insult": self.insult,
            "identity_hate": self.identity_hate
        }
        result.update(self._extra_fields)
        return result


@dataclass
class PIIEntityDetail(BaseDTO):
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PIIEntityDetail":
        obj = cls()
        obj._extra_fields = data
        return obj
    
    def to_dict(self) -> Dict[str, Any]:
        return self._extra_fields


@dataclass
class PIIDetail(BaseDTO):
    pii: PIIEntityDetail = field(default_factory=PIIEntityDetail)
    secrets: PIIEntityDetail = field(default_factory=PIIEntityDetail)
    ip_address: PIIEntityDetail = field(default_factory=PIIEntityDetail)
    url: PIIEntityDetail = field(default_factory=PIIEntityDetail)
    person: PIIEntityDetail = field(default_factory=PIIEntityDetail)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PIIDetail":
        return cls(
            pii=PIIEntityDetail.from_dict(data.get("pii", {})),
            secrets=PIIEntityDetail.from_dict(data.get("secrets", {})),
            ip_address=PIIEntityDetail.from_dict(data.get("ip_address", {})),
            url=PIIEntityDetail.from_dict(data.get("url", {})),
            person=PIIEntityDetail.from_dict(data.get("person", {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "pii": self.pii.to_dict(),
            "secrets": self.secrets.to_dict(),
            "ip_address": self.ip_address.to_dict(),
            "url": self.url.to_dict(),
            "person": self.person.to_dict()
        }
        result.update(self._extra_fields)
        return result


@dataclass
class InjectionAttackDetail(BaseDTO):
    safe: str = "0.0"
    attack: str = "0.0"
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InjectionAttackDetail":
        return cls(
            safe=data.get("safe", "0.0"),
            attack=data.get("attack", "0.0")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "safe": self.safe,
            "attack": self.attack
        }
        result.update(self._extra_fields)
        return result


@dataclass
class KeywordDetectorDetail(BaseDTO):
    detected_keywords: List[str] = field(default_factory=list)
    detected_counts: Dict[str, int] = field(default_factory=dict)
    redacted_text: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeywordDetectorDetail":
        return cls(
            detected_keywords=data.get("detected_keywords", []),
            detected_counts=data.get("detected_counts", {}),
            redacted_text=data.get("redacted_text", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "detected_keywords": self.detected_keywords,
            "detected_counts": self.detected_counts,
            "redacted_text": self.redacted_text
        }
        result.update(self._extra_fields)
        return result


@dataclass
class PolicyViolationDetail(BaseDTO):
    violating_policy: str = ""
    explanation: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyViolationDetail":
        return cls(
            violating_policy=data.get("violating_policy", ""),
            explanation=data.get("explanation", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "violating_policy": self.violating_policy,
            "explanation": self.explanation
        }
        result.update(self._extra_fields)
        return result


@dataclass
class BiasDetail(BaseDTO):
    bias_detected: bool = False
    debiased_text: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BiasDetail":
        return cls(
            bias_detected=data.get("bias_detected", False),
            debiased_text=data.get("debiased_text", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "bias_detected": self.bias_detected,
            "debiased_text": self.debiased_text
        }
        result.update(self._extra_fields)
        return result


@dataclass
class CopyrightIPDetail(BaseDTO):
    similarity_score: float = 0.0
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CopyrightIPDetail":
        return cls(
            similarity_score=float(data.get("similarity_score", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "similarity_score": self.similarity_score
        }
        result.update(self._extra_fields)
        return result


@dataclass
class SystemPromptDetail(BaseDTO):
    similarity_score: float = 0.0
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemPromptDetail":
        return cls(
            similarity_score=float(data.get("similarity_score", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "similarity_score": self.similarity_score
        }
        result.update(self._extra_fields)
        return result


@dataclass
class SpongeAttackDetail(BaseDTO):
    sponge_attack_detected: bool = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpongeAttackDetail":
        return cls(
            sponge_attack_detected=data.get("sponge_attack_detected", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "sponge_attack_detected": self.sponge_attack_detected
        }
        result.update(self._extra_fields)
        return result


@dataclass
class DetectResponseSummary(BaseDTO):
    on_topic: int = 0
    nsfw: int = 0
    toxicity: List[str] = field(default_factory=list)
    pii: int = 0
    injection_attack: int = 0
    keyword_detected: int = 0
    policy_violation: int = 0
    bias: int = 0
    copyright_ip_similarity: int = 0
    system_prompt_similarity: int = 0
    sponge_attack: int = 0
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectResponseSummary":
        return cls(
            on_topic=data.get("on_topic", 0),
            nsfw=data.get("nsfw", 0),
            toxicity=data.get("toxicity", []),
            pii=data.get("pii", 0),
            injection_attack=data.get("injection_attack", 0),
            keyword_detected=data.get("keyword_detected", 0),
            policy_violation=data.get("policy_violation", 0),
            bias=data.get("bias", 0),
            copyright_ip_similarity=data.get("copyright_ip_similarity", 0),
            system_prompt_similarity=data.get("system_prompt_similarity", 0),
            sponge_attack=data.get("sponge_attack", 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "on_topic": self.on_topic,
            "nsfw": self.nsfw,
            "toxicity": self.toxicity,
            "pii": self.pii,
            "injection_attack": self.injection_attack,
            "keyword_detected": self.keyword_detected,
            "policy_violation": self.policy_violation,
            "bias": self.bias,
            "copyright_ip_similarity": self.copyright_ip_similarity,
            "system_prompt_similarity": self.system_prompt_similarity,
            "sponge_attack": self.sponge_attack
        }
        result.update(self._extra_fields)
        return result


@dataclass
class DetectResponseDetails(BaseDTO):
    topic_detector: TopicDetectorDetail = field(default_factory=TopicDetectorDetail)
    nsfw: NSFWDetail = field(default_factory=NSFWDetail)
    toxicity: ToxicityDetail = field(default_factory=ToxicityDetail)
    pii: PIIDetail = field(default_factory=PIIDetail)
    injection_attack: InjectionAttackDetail = field(default_factory=InjectionAttackDetail)
    keyword_detector: KeywordDetectorDetail = field(default_factory=KeywordDetectorDetail)
    policy_violation: PolicyViolationDetail = field(default_factory=PolicyViolationDetail)
    bias: BiasDetail = field(default_factory=BiasDetail)
    copyright_ip: CopyrightIPDetail = field(default_factory=CopyrightIPDetail)
    system_prompt: SystemPromptDetail = field(default_factory=SystemPromptDetail)
    sponge_attack: SpongeAttackDetail = field(default_factory=SpongeAttackDetail)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectResponseDetails":
        return cls(
            topic_detector=TopicDetectorDetail.from_dict(data.get("topic_detector", {})),
            nsfw=NSFWDetail.from_dict(data.get("nsfw", {})),
            toxicity=ToxicityDetail.from_dict(data.get("toxicity", {})),
            pii=PIIDetail.from_dict(data.get("pii", {})),
            injection_attack=InjectionAttackDetail.from_dict(data.get("injection_attack", {})),
            keyword_detector=KeywordDetectorDetail.from_dict(data.get("keyword_detector", {})),
            policy_violation=PolicyViolationDetail.from_dict(data.get("policy_violation", {})),
            bias=BiasDetail.from_dict(data.get("bias", {})),
            copyright_ip=CopyrightIPDetail.from_dict(data.get("copyright_ip", {})),
            system_prompt=SystemPromptDetail.from_dict(data.get("system_prompt", {})),
            sponge_attack=SpongeAttackDetail.from_dict(data.get("sponge_attack", {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "topic_detector": self.topic_detector.to_dict(),
            "nsfw": self.nsfw.to_dict(),
            "toxicity": self.toxicity.to_dict(),
            "pii": self.pii.to_dict(),
            "injection_attack": self.injection_attack.to_dict(),
            "keyword_detector": self.keyword_detector.to_dict(),
            "policy_violation": self.policy_violation.to_dict(),
            "bias": self.bias.to_dict(),
            "copyright_ip": self.copyright_ip.to_dict(),
            "system_prompt": self.system_prompt.to_dict(),
            "sponge_attack": self.sponge_attack.to_dict()
        }
        result.update(self._extra_fields)
        return result


@dataclass
class GuardrailsDetectResponse(BaseDTO):
    summary: DetectResponseSummary
    details: DetectResponseDetails
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsDetectResponse":
        summary_data = data.get("summary", {})
        details_data = data.get("details", {})
        
        return cls(
            summary=DetectResponseSummary.from_dict(summary_data),
            details=DetectResponseDetails.from_dict(details_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "summary": self.summary.to_dict(),
            "details": self.details.to_dict()
        }
        result.update(self._extra_fields)
        return result

    def has_violations(self) -> bool:
        """
        Check if any detectors found violations in the content.
        
        Returns:
            bool: True if any detector reported a violation (score > 0), False otherwise
        """
        summary = self.summary.to_dict()
        for key, value in summary.items():
            if key == "toxicity" and isinstance(value, list) and len(value) > 0:
                return True
            elif isinstance(value, (int, float)) and value > 0:
                return True
        return False
    
    def get_violations(self) -> list[str]:
        """
        Get a list of detector names that found violations.
        
        Returns:
            list[str]: Names of detectors that reported violations
        """
        summary = self.summary.to_dict()
        violations = []
        for detector, value in summary.items():
            if detector == "toxicity" and isinstance(value, list) and len(value) > 0:
                violations.append(detector)
            elif isinstance(value, (int, float)) and value > 0:
                violations.append(detector)
        return violations

    def is_safe(self) -> bool:
        """
        Check if the content is safe (no violations detected).
        
        Returns:
            bool: True if no violations were detected, False otherwise
        """
        return not self.has_violations()
    
    def is_attack(self) -> bool:
        """
        Check if the content is attacked (violations detected).
        
        Returns:
            bool: True if violations were detected, False otherwise
        """
        return self.has_violations()
    
    def __str__(self) -> str:
        """
        String representation of the response.
        
        Returns:
            str: A formatted string showing summary and violation status
        """
        violations = self.get_violations()
        status = "UNSAFE" if violations else "SAFE"
        
        if violations:
            violation_str = f"Violations detected: {', '.join(violations)}"
        else:
            violation_str = "No violations detected"
            
        return f"Response Status: {status}\n{violation_str}"


@dataclass
class BatchDetectResponseItem(BaseDTO):
    text: str
    summary: DetectResponseSummary
    details: DetectResponseDetails
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchDetectResponseItem":
        return cls(
            text=data.get("text", ""),
            summary=DetectResponseSummary.from_dict(data.get("summary", {})),
            details=DetectResponseDetails.from_dict(data.get("details", {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "text": self.text,
            "summary": self.summary.to_dict(),
            "details": self.details.to_dict()
        }
        result.update(self._extra_fields)
        return result

    def has_violations(self) -> bool:
        """
        Check if any detectors found violations in the content.
        
        Returns:
            bool: True if any detector reported a violation (score > 0), False otherwise
        """
        summary = self.summary.to_dict()
        for key, value in summary.items():
            if key == "toxicity" and isinstance(value, list) and len(value) > 0:
                return True
            elif isinstance(value, (int, float)) and value > 0:
                return True
        return False
    
    def get_violations(self) -> list[str]:
        """
        Get a list of detector names that found violations.
        
        Returns:
            list[str]: Names of detectors that reported violations
        """
        summary = self.summary.to_dict()
        violations = []
        for detector, value in summary.items():
            if detector == "toxicity" and isinstance(value, list) and len(value) > 0:
                violations.append(detector)
            elif isinstance(value, (int, float)) and value > 0:
                violations.append(detector)
        return violations

    def is_safe(self) -> bool:
        """
        Check if the content is safe (no violations detected).
        
        Returns:
            bool: True if no violations were detected, False otherwise
        """
        return not self.has_violations()
    
    def is_attack(self) -> bool:
        """
        Check if the content is attacked (violations detected).
        
        Returns:
            bool: True if violations were detected, False otherwise
        """
        return self.has_violations()
    
    def __str__(self) -> str:
        """
        String representation of the response.
        
        Returns:
            str: A formatted string showing summary and violation status
        """
        violations = self.get_violations()
        status = "UNSAFE" if violations else "SAFE"
        
        if violations:
            violation_str = f"Violations detected: {', '.join(violations)}"
        else:
            violation_str = "No violations detected"
            
        return f"Response Status: {status}\n{violation_str}"


@dataclass
class GuardrailsBatchDetectResponse(BaseDTO):
    batch_detections: List[BatchDetectResponseItem] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "GuardrailsBatchDetectResponse":
        return cls(
            batch_detections=[BatchDetectResponseItem.from_dict(item) for item in data]
        )
    
    def to_dict(self) -> List[Dict[str, Any]]:
        return [response.to_dict() for response in self.batch_detections]

    def has_violations(self) -> bool:
        """
        Check if any detectors found violations in any of the batch_detections.
        
        Returns:
            bool: True if any detector reported a violation, False otherwise
        """
        for detection in self.batch_detections:         
            summary = detection.summary.to_dict()
            for key, value in summary.items():
                if key == "toxicity" and isinstance(value, list) and len(value) > 0:
                    return True
                elif isinstance(value, (int, float)) and value > 0:
                    return True
        return False
    
    def get_violations(self) -> List[str]:
        """
        Get a list of texts that have violations.
        
        Returns:
            List[str]: List of texts that have violations
        """
        violations = set()
        for detection in self.batch_detections:
            summary = detection.summary.to_dict()
            for detector, value in summary.items():
                if detector == "toxicity" and isinstance(value, list) and len(value) > 0:
                    violations.add(detector)
                elif isinstance(value, (int, float)) and value > 0:
                    violations.add(detector)
        return list(violations)

    def is_safe(self) -> bool:
        """
        Check if all content is safe (no violations detected).
        
        Returns:
            bool: True if no violations were detected in any response, False otherwise
        """
        return not self.has_violations()
    
    def is_attack(self) -> bool:
        """
        Check if any content is attacked (violations detected).
        
        Returns:
            bool: True if violations were detected in any response, False otherwise
        """
        return self.has_violations()
    
    def __str__(self) -> str:
        """
        String representation of the batch response.
        
        Returns:
            str: A formatted string showing violation status for all batch_detections
        """
        violations = self.get_violations()
        status = "UNSAFE" if violations else "SAFE"
        
        if violations:
            violation_str = f"Violations detected in texts:\n" + "\n".join(f"- {text}" for text in violations)
        else:
            violation_str = "No violations detected in any text"
            
        return f"Batch Response Status: {status}\n{violation_str}"


# -------------------------------------
# Guardrails PII
# -------------------------------------


@dataclass
class GuardrailsPIIRequest(BaseDTO):
    text: str
    # mode: GuardrailsPIIModes = GuardrailsPIIModes.REQUEST
    mode: str = "request"
    key: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPIIRequest":
        return cls(
            text=data.get("text", ""),
            # mode=data.get("mode", GuardrailsPIIModes.REQUEST),
            mode=data.get("mode", "request"),
            key=data.get("key", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "mode": self.mode,
            "key": self.key
        }


@dataclass
class GuardrailsPIIResponse(BaseDTO):
    text: str
    key: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPIIResponse":
        return cls(
            text=data.get("text", ""),
            key=data.get("key", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "key": self.key
        }


# -------------------------------------
# Guardrails Hallucination
# -------------------------------------

@dataclass
class GuardrailsHallucinationRequest(BaseDTO):
    request_text: str
    response_text: str
    context: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsHallucinationRequest":
        return cls(
            request_text=data.get("request_text", ""),
            response_text=data.get("response_text", ""),
            context=data.get("context", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_text": self.request_text,
            "response_text": self.response_text,
            "context": self.context
        }


@dataclass
class HallucinationSummary(BaseDTO):
    is_hallucination: int
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HallucinationSummary":
        return cls(
            is_hallucination=data.get("is_hallucination", 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_hallucination": self.is_hallucination
        }


@dataclass
class HallucinationDetails(BaseDTO):
    prompt_based: float
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HallucinationDetails":
        return cls(
            prompt_based=float(data.get("prompt_based", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_based": self.prompt_based
        }


@dataclass
class GuardrailsHallucinationResponse(BaseDTO):
    summary: HallucinationSummary
    details: HallucinationDetails
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsHallucinationResponse":
        summary_data = data.get("summary", {})
        details_data = data.get("details", {})
        
        return cls(
            summary=HallucinationSummary.from_dict(summary_data),
            details=HallucinationDetails.from_dict(details_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "details": self.details.to_dict()
        }


# -------------------------------------
# Guardrails Adherence
# -------------------------------------


@dataclass
class GuardrailsAdherenceRequest(BaseDTO):
    llm_answer: str
    context: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsAdherenceRequest":
        return cls(
            llm_answer=data.get("llm_answer", ""),
            context=data.get("context", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "llm_answer": self.llm_answer,
            "context": self.context
        }


@dataclass
class AdherenceSummary(BaseDTO):
    adherence_score: float
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdherenceSummary":
        return cls(
            adherence_score=float(data.get("adherence_score", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "adherence_score": self.adherence_score
        }


@dataclass
class AdherenceDetails(BaseDTO):
    atomic_facts: List[str] = field(default_factory=list)
    adherence_list: List[int] = field(default_factory=list)
    adherence_response: str = ""
    adherence_latency: float = 0.0
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdherenceDetails":
        return cls(
            atomic_facts=data.get("atomic_facts", []),
            adherence_list=data.get("adherence_list", []),
            adherence_response=data.get("adherence_response", ""),
            adherence_latency=float(data.get("adherence_latency", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atomic_facts": self.atomic_facts,
            "adherence_list": self.adherence_list,
            "adherence_response": self.adherence_response,
            "adherence_latency": self.adherence_latency
        }


@dataclass
class GuardrailsAdherenceResponse(BaseDTO):
    summary: AdherenceSummary
    details: AdherenceDetails
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsAdherenceResponse":
        summary_data = data.get("summary", {})
        details_data = data.get("details", {})
        
        return cls(
            summary=AdherenceSummary.from_dict(summary_data),
            details=AdherenceDetails.from_dict(details_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "details": self.details.to_dict()
        }


# -------------------------------------
# Guardrails Relevancy
# -------------------------------------

@dataclass
class GuardrailsRelevancyRequest(BaseDTO):
    question: str
    llm_answer: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsRelevancyRequest":
        return cls(
            question=data.get("question", ""),
            llm_answer=data.get("llm_answer", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "llm_answer": self.llm_answer
        }


@dataclass
class RelevancySummary(BaseDTO):
    relevancy_score: float
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelevancySummary":
        return cls(
            relevancy_score=float(data.get("relevancy_score", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "relevancy_score": self.relevancy_score
        }


@dataclass
class RelevancyDetails(BaseDTO):
    atomic_facts: List[str] = field(default_factory=list)
    relevancy_list: List[int] = field(default_factory=list)
    relevancy_response: str = ""
    relevancy_latency: float = 0.0
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelevancyDetails":
        return cls(
            atomic_facts=data.get("atomic_facts", []),
            relevancy_list=data.get("relevancy_list", []),
            relevancy_response=data.get("relevancy_response", ""),
            relevancy_latency=float(data.get("relevancy_latency", 0.0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atomic_facts": self.atomic_facts,
            "relevancy_list": self.relevancy_list,
            "relevancy_response": self.relevancy_response,
            "relevancy_latency": self.relevancy_latency
        }


@dataclass
class GuardrailsRelevancyResponse(BaseDTO):
    summary: RelevancySummary
    details: RelevancyDetails
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsRelevancyResponse":
        summary_data = data.get("summary", {})
        details_data = data.get("details", {})
        
        return cls(
            summary=RelevancySummary.from_dict(summary_data),
            details=RelevancyDetails.from_dict(details_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "details": self.details.to_dict()
        }


# -------------------------------------
# Guardrails Policy Request
# -------------------------------------


@dataclass
class GuardrailsPolicyRequest(BaseDTO):
    name: str
    detectors: GuardrailDetectors = field(default_factory=GuardrailDetectors)
    description: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPolicyRequest":
        detectors_data = data.get("detectors", {})
        return cls(
            name=data.get("name", ""),
            detectors=GuardrailDetectors.from_dict(detectors_data),
            description=data.get("description", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "detectors": self.detectors.to_dict(),
            "description": self.description
        }


# -------------------------------------
# Guardrails Policy Response
# -------------------------------------


@dataclass
class GuardrailsPolicyData(BaseDTO):
    created_at: str
    name: str
    updated_at: str
    created_by: str
    updated_by: str
    description: str
    policy_id: int
    project_name: str = ""
    is_sample: bool = False
    detectors: GuardrailDetectors = field(default_factory=GuardrailDetectors)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPolicyData":
        detectors_data = data.get("detectors", {})
        return cls(
            created_at=data.get("created_at", ""),
            name=data.get("name", ""),
            updated_at=data.get("updated_at", ""),
            created_by=data.get("created_by", ""),
            updated_by=data.get("updated_by", ""),
            description=data.get("description", ""),
            policy_id=data.get("policy_id", 0),
            project_name=data.get("project_name", ""),
            detectors=GuardrailDetectors.from_dict(detectors_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "created_at": self.created_at,
            "name": self.name,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "description": self.description,
            "policy_id": self.policy_id,
            "project_name": self.project_name,
            "detectors": self.detectors.to_dict(),
        }
        result.update(self._extra_fields)
        return result


@dataclass
class GuardrailsPolicyResponse(BaseDTO):
    message: str
    data: GuardrailsPolicyData
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPolicyResponse":
        policy_data = data.get("data", {})
        return cls(
            message=data.get("message", ""),
            data=GuardrailsPolicyData.from_dict(policy_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "message": self.message,
            "data": self.data.to_dict()
        }
        result.update(self._extra_fields)
        return result


@dataclass
class GuardrailsDeletePolicyData(BaseDTO):
    policy_id: int
    project_name: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsDeletePolicyData":
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
class GuardrailsDeletePolicyResponse(BaseDTO):
    message: str
    data: GuardrailsDeletePolicyData
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsDeletePolicyResponse":
        policy_data = data.get("data", {})
        return cls(
            message=data.get("message", ""),
            data=GuardrailsDeletePolicyData.from_dict(policy_data)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "message": self.message,
            "data": self.data.to_dict()
        }
        result.update(self._extra_fields)
        return result


@dataclass
class GuardrailsPolicyListItem(BaseDTO):
    policy_id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    created_by: str
    updated_by: str
    project_name: str = "default"
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPolicyListItem":
        return cls(
            policy_id=data.get("policy_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            created_by=data.get("created_by", ""),
            updated_by=data.get("updated_by", ""),
            project_name=data.get("project_name", "default")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "project_name": self.project_name
        }
        result.update(self._extra_fields)
        return result


@dataclass
class GuardrailsListPoliciesResponse(BaseDTO):
    policies: List[GuardrailsPolicyListItem] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsListPoliciesResponse":
        policies_data = data.get("policies", [])
        return cls(
            policies=[GuardrailsPolicyListItem.from_dict(policy) for policy in policies_data]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "policies": [policy.to_dict() for policy in self.policies]
        }
        result.update(self._extra_fields)
        return result


# -------------------------------------
# Guardrails Policy Atomizer
# -------------------------------------

@dataclass
class GuardrailsPolicyAtomizerRequest(BaseDTO):
    text: Optional[str] = None
    file: Optional[BinaryIO] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPolicyAtomizerRequest":
        return cls(
            file=data.get("file", None),
            text=data.get("text", None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.file:
            result["file"] = self.file
        if self.text:
            result["text"] = self.text
        result.update(self._extra_fields)
        return result

    def validate(self) -> bool:
        """
        Validate that either file or text is provided, but not both.
        
        Returns:
            bool: True if valid, False otherwise
        """
        return bool(self.file) != bool(self.text)  # XOR - only one should be True


@dataclass
class GuardrailsPolicyAtomizerResponse(BaseDTO):
    status: str = ""
    message: str = ""
    source: str = ""
    filename: str = ""
    total_rules: int = 0
    policy_rules: str = ""
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsPolicyAtomizerResponse":
        return cls(
            status=data.get("status", "success"),
            message=data.get("message", ""),
            source=data.get("source", ""),
            filename=data.get("filename", ""),
            total_rules=data.get("total_rules", 0),
            policy_rules=data.get("policy_rules", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "status": self.status,
            "message": self.message,
            "source": self.source,
            "filename": self.filename,
            "total_rules": self.total_rules,
            "policy_rules": self.policy_rules
        }
        result.update(self._extra_fields)
        return result

    def is_successful(self) -> bool:
        """
        Check if the atomization was successful.
        
        Returns:
            bool: True if status is "success", False otherwise
        """
        return self.status == "success"

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
            str: A formatted string showing the atomization results
        """
        source_info = f"File: {self.filename}" if self.source == "upload" else "Source: Text input"
        return (
            f"Policy Atomizer Response:\n"
            f"Status: {self.status}\n"
            f"{source_info}\n"
            f"Total Rules: {self.total_rules}\n"
            f"Message: {self.message}"
        )


@dataclass
class GuardrailsViolation(BaseDTO):
    unsafe_content: str
    chunk_type: str
    triggered_detectors: List[str]
    guardrails_result: Dict[str, Any]
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsViolation":
        return cls(
            unsafe_content=data.get("unsafe_content", ""),
            chunk_type=data.get("chunk_type", ""),
            triggered_detectors=data.get("triggered_detectors", []),
            guardrails_result=data.get("guardrails_result", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "unsafe_content": self.unsafe_content,
            "chunk_type": self.chunk_type,
            "triggered_detectors": self.triggered_detectors,
            "guardrails_result": self.guardrails_result
        }
        result.update(self._extra_fields)
        return result


@dataclass
class GuardrailsScanUrlResponse(BaseDTO):
    url: str
    violations: List[GuardrailsViolation]
    combined_highlight_url: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsScanUrlResponse":
        violations_data = data.get("violations", [])
        violations = [GuardrailsViolation.from_dict(violation) for violation in violations_data]
        
        return cls(
            url=data.get("url", ""),
            violations=violations,
            combined_highlight_url=data.get("combined_highlight_url", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "url": self.url,
            "violations": [violation.to_dict() for violation in self.violations],
            "combined_highlight_url": self.combined_highlight_url
        }
        result.update(self._extra_fields)
        return result

    def has_violations(self) -> bool:
        """
        Check if any detectors found violations in the URL content.
        
        Returns:
            bool: True if any violations were detected, False otherwise
        """
        return len(self.violations) > 0
    
    def get_violations(self) -> List[str]:
        """
        Get a list of detector names that found violations.
        
        Returns:
            List[str]: Names of detectors that reported violations
        """
        triggered_detectors = []
        for violation in self.violations:
            triggered_detectors.extend(violation.triggered_detectors)
        # Remove duplicates while preserving order
        return list(dict.fromkeys(triggered_detectors))

    def is_safe(self) -> bool:
        """
        Check if the URL content is safe (no violations detected).
        
        Returns:
            bool: True if no violations were detected, False otherwise
        """
        return not self.has_violations()
    
    def is_attack(self) -> bool:
        """
        Check if the URL content is attacked (violations detected).
        
        Returns:
            bool: True if violations were detected, False otherwise
        """
        return self.has_violations()
    
    def __str__(self) -> str:
        """
        String representation of the response.
        
        Returns:
            str: A formatted string showing URL, violations and status
        """
        violations = self.get_violations()
        status = "UNSAFE" if violations else "SAFE"
        
        if violations:
            violation_str = f"Violations detected: {', '.join(violations)}"
        else:
            violation_str = "No violations detected"
            
        return f"URL Scan Result for {self.url}\nStatus: {status}\n{violation_str}"

