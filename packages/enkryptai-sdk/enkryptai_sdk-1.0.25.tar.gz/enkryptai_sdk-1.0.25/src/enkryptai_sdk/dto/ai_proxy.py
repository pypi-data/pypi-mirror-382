from .base import BaseDTO
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Optional


@dataclass
class ChatCompletionMessage(BaseDTO):
    role: str
    content: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionMessage":
        return cls(
            role=data.get("role", ""),
            content=data.get("content", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class ChatCompletionRequest(BaseDTO):
    model: str
    messages: List[ChatCompletionMessage]
    enkrypt_context: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    n: Optional[int] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionRequest":
        messages_data = data.get("messages", [])
        
        # Create a copy of the data without the fields we're explicitly processing
        extra_fields = {k: v for k, v in data.items() 
                       if k not in ["messages", "model", "enkrypt_context", 
                                   "temperature", "top_p", "max_tokens", 
                                   "presence_penalty", "frequency_penalty", "n"]}
        
        return cls(
            messages=[ChatCompletionMessage.from_dict(msg) for msg in messages_data],
            model=data.get("model", ""),
            enkrypt_context=data.get("enkrypt_context", None),
            temperature=data.get("temperature", None),
            top_p=data.get("top_p", None),
            max_tokens=data.get("max_tokens", None),
            presence_penalty=data.get("presence_penalty", None),
            frequency_penalty=data.get("frequency_penalty", None),
            n=data.get("n", 1),
            _extra_fields=extra_fields
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "messages": [message.to_dict() for message in self.messages],
            "model": self.model
        }
        
        # Add optional fields only if they are not None or default values
        if self.enkrypt_context is not None:
            result["enkrypt_context"] = self.enkrypt_context
        if self.temperature is not None:
            result["temperature"] = self.temperature
        if self.top_p is not None:
            result["top_p"] = self.top_p
        if self.max_tokens is not None:
            result["max_tokens"] = self.max_tokens
        if self.presence_penalty is not None:
            result["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty is not None:
            result["frequency_penalty"] = self.frequency_penalty
        if self.n is not None:
            result["n"] = self.n
            
        # Add any extra fields that weren't explicitly defined
        result.update(self._extra_fields)
        return result


@dataclass
class ChatCompletionResponseMessage(BaseDTO):
    role: str
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionResponseMessage":
        return cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            tool_calls=data.get("tool_calls", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "role": self.role,
            "content": self.content
        }
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


@dataclass
class ChatCompletionChoice(BaseDTO):
    index: int
    message: ChatCompletionResponseMessage
    finish_reason: Optional[str] = None
    seed: Optional[int] = None
    logprobs: Optional[Any] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChoice":
        return cls(
            index=data.get("index", 0),
            message=ChatCompletionResponseMessage.from_dict(data.get("message", {})),
            finish_reason=data.get("finish_reason", None),
            seed=data.get("seed", None),
            logprobs=data.get("logprobs", None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "index": self.index,
            "message": self.message.to_dict()
        }
        if self.finish_reason is not None:
            result["finish_reason"] = self.finish_reason
        if self.seed is not None:
            result["seed"] = self.seed
        if self.logprobs is not None:
            result["logprobs"] = self.logprobs
        return result


@dataclass
class ChatCompletionUsage(BaseDTO):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionUsage":
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }


@dataclass
class ChatCompletionResponse(BaseDTO):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage
    prompt: List[Any] = field(default_factory=list)
    enkrypt_policy_detections: Dict[str, Any] = field(default_factory=dict)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionResponse":
        # Extract fields we're explicitly handling
        choices_data = data.get("choices", [])
        usage_data = data.get("usage", {})
        
        # Create a copy of the data without the fields we're explicitly processing
        extra_fields = {k: v for k, v in data.items() 
                       if k not in ["id", "object", "created", "model", 
                                    "choices", "usage", "prompt", "enkrypt_policy_detections"]}
        
        return cls(
            id=data.get("id", ""),
            object=data.get("object", ""),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=[ChatCompletionChoice.from_dict(choice) for choice in choices_data],
            usage=ChatCompletionUsage.from_dict(usage_data),
            prompt=data.get("prompt", []),
            enkrypt_policy_detections=data.get("enkrypt_policy_detections", {}),
            _extra_fields=extra_fields
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [choice.to_dict() for choice in self.choices],
            "usage": self.usage.to_dict(),
            "prompt": self.prompt,
            "enkrypt_policy_detections": self.enkrypt_policy_detections
        }
        
        # Add any extra fields
        result.update(self._extra_fields)
        return result


@dataclass
class ChatCompletionError(BaseDTO):
    code: str
    param: Optional[str] = None
    type: Optional[str] = None
    message: Optional[str] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionError":
        # If data is string, then parse the json
        if isinstance(data, str):
            import json
            data = json.loads(data)
        # Create a copy of the data without the fields we're explicitly processing
        extra_fields = {k: v for k, v in data.items() 
                       if k not in ["code", "param", "type", "message"]}
        
        return cls(
            code=data.get("code", ""),
            param=data.get("param", None),
            type=data.get("type", None),
            message=data.get("message", None),
            _extra_fields=extra_fields
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "code": self.code
        }
        
        # Add optional fields only if they are not None
        if self.param is not None:
            result["param"] = self.param
        if self.type is not None:
            result["type"] = self.type
        if self.message is not None:
            result["message"] = self.message
            
        # Add any extra fields
        result.update(self._extra_fields)
        return result


@dataclass
class ChatCompletionErrorResponse(BaseDTO):
    error: ChatCompletionError
    enkrypt_policy_detections: Dict[str, Any] = field(default_factory=dict)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionErrorResponse":
        error_data = data.get("error", {})
        
        # Create a copy of the data without the fields we're explicitly processing
        extra_fields = {k: v for k, v in data.items() 
                       if k not in ["error", "enkrypt_policy_detections"]}
        
        return cls(
            error=ChatCompletionError.from_dict(error_data),
            enkrypt_policy_detections=data.get("enkrypt_policy_detections", {}),
            _extra_fields=extra_fields
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "error": self.error.to_dict(),
            "enkrypt_policy_detections": self.enkrypt_policy_detections
        }
        
        # Add any extra fields
        result.update(self._extra_fields)
        return result


@dataclass
class ChatCompletionDirectErrorResponse(BaseDTO):
    error: str
    message: str
    request_id: Optional[str] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionDirectErrorResponse":
        # Create a copy of the data without the fields we're explicitly processing
        extra_fields = {k: v for k, v in data.items() 
                       if k not in ["error", "message", "request_id"]}
        
        return cls(
            error=data.get("error", None),
            message=data.get("message", None),
            request_id=data.get("request_id", None),
            _extra_fields=extra_fields
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            # "message": self.message
        }
        
        # Add optional fields only if they are not None
        if self.error is not None:
            result["error"] = self.error
        if self.message is not None:
            result["message"] = self.message
        if self.request_id is not None:
            result["request_id"] = self.request_id
        
        # Add any extra fields
        result.update(self._extra_fields)
        return result
