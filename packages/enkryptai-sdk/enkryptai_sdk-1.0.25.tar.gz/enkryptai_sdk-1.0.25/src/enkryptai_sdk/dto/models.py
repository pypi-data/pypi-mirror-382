import json
import pandas as pd
from enum import Enum
from .base import BaseDTO
from tabulate import tabulate
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Set, Dict, Any
from .common import ModelAuthTypeEnum, CustomHeader, ModelJwtConfig


# class Modality(Enum):
#     TEXT = "text"
#     IMAGE = "image"
#     AUDIO = "audio"
#     VIDEO = "video"

#     def to_dict(self):
#         return self.value


class ModelProviders(str, Enum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    MISTRAL = "mistral"
    LLAMA = "llama"
    BEDROCK = "bedrock"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"
    GROQ = "groq"
    AI21 = "ai21"
    FIREWORKS = "fireworks"
    ALIBABA = "alibaba"
    PORTKEY = "portkey"
    DEEPSEEK = "deepseek"
    OPENAI_COMPATIBLE = "openai_compatible"
    COHERE_COMPATIBLE = "cohere_compatible"
    ANTHROPIC_COMPATIBLE = "anthropic_compatible"
    CUSTOM = "custom"
    HR = "hr"
    URL = "url"
    ENKRYPTAI = "enkryptai"
    BOXAI = "boxai"


@dataclass
class ModelResponse(BaseDTO):
    message: Optional[str] = None
    data: Optional[Dict] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class EndpointConfig(BaseDTO):
    scheme: str = "https"
    host: str = "api.openai.com"
    port: int = 443
    base_path: str = "v1"


@dataclass
class PathsConfig(BaseDTO):
    completions: str = "/chat/completions"
    chat: str = "chat/completions"
    vision: str = "images"
    embeddings: str = "embeddings"


@dataclass
class AuthData(BaseDTO):
    header_name: str = "Authorization"
    header_prefix: str = "Bearer"
    space_after_prefix: bool = True
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class BoxAIAuthData(AuthData):
    """BoxAI-specific authentication data."""
    boxai_client_id: Optional[str] = None
    boxai_client_secret: Optional[str] = None
    boxai_user_id: Optional[str] = None
    boxai_default_file_id: Optional[str] = None
    
    def __post_init__(self):
        # Store BoxAI fields in extra_fields for backward compatibility
        if self.boxai_client_id:
            self._extra_fields["boxai_client_id"] = self.boxai_client_id
        if self.boxai_client_secret:
            self._extra_fields["boxai_client_secret"] = self.boxai_client_secret
        if self.boxai_user_id:
            self._extra_fields["boxai_user_id"] = self.boxai_user_id
        if self.boxai_default_file_id:
            self._extra_fields["boxai_default_file_id"] = self.boxai_default_file_id
    
    @classmethod
    def from_dict(cls, data: dict):
        # Extract BoxAI fields from extra_fields if they exist
        boxai_data = {}
        if "_extra_fields" in data:
            extra_fields = data["_extra_fields"]
            for field in ["boxai_client_id", "boxai_client_secret", "boxai_user_id", "boxai_default_file_id"]:
                if field in extra_fields:
                    boxai_data[field] = extra_fields[field]
        
        # Merge with direct field values
        for field in ["boxai_client_id", "boxai_client_secret", "boxai_user_id", "boxai_default_file_id"]:
            if field in data:
                boxai_data[field] = data[field]
        
        # Create the instance
        return cls(**boxai_data)


@dataclass
class ModelDetailConfig:
    model_source: str = ""
    # model_provider: str = "openai"
    model_provider: ModelProviders = ModelProviders.OPENAI
    system_prompt: str = ""
    endpoint_url: str = ""
    auth_data: AuthData = field(default_factory=AuthData)
    metadata: Dict[str, Any] = field(default_factory=dict)
    api_keys: Set[Optional[str]] = field(default_factory=lambda: {None})
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetailModelConfig:
    model_saved_name: str = "Model Name"
    model_version: str = "v1"
    testing_for: str = "foundationModels"
    model_name: Optional[str] = "gpt-4o-mini"
    # modality: Modality = Modality.TEXT
    model_config: ModelDetailConfig = field(default_factory=ModelDetailConfig)


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
class ModelConfigDetails(BaseDTO):
    model_id: str = None
    model_source: str = None
    # model_provider: str = "openai"
    model_provider: ModelProviders = ModelProviders.OPENAI
    model_api_value: str = ""
    model_bearer_token: str = ""
    model_auth_type: str = ""
    model_api_key: str = ""
    model_endpoint_url: str = ""
    rate_per_min: int = 20
    testing_for: str = "foundationModels"
    headers: str = ""
    system_prompt: str = ""
    hosting_type: str = "External"
    endpoint_url: str = ""
    model_name: Optional[str] = ""
    apikey: Optional[str] = None
    paths: Optional[PathsConfig] = None
    tools: List[Dict[str, str]] = field(default_factory=list)
    model_auth_type: Optional[ModelAuthTypeEnum] = ModelAuthTypeEnum.APIKEY
    model_jwt_config: Optional[ModelJwtConfig] = None
    auth_data: AuthData = field(default_factory=AuthData)
    input_modalities: List[InputModality] = field(default_factory=list)
    output_modalities: List[OutputModality] = field(default_factory=list)
    custom_curl_command: Optional[str] = None
    custom_headers: List[CustomHeader] = field(default_factory=list)
    custom_payload: Dict[str, Any] = field(default_factory=dict)
    custom_response_content_type: Optional[str] = ""
    custom_response_format: Optional[str] = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    default_request_options: Dict[str, Any] = field(default_factory=dict)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        # Create a copy of the data to avoid modifying the original
        data = data.copy()

        if "custom_headers" in data:
            data["custom_headers"] = [CustomHeader.from_dict(h) for h in data["custom_headers"]]

        if "model_auth_type" in data:
            data["model_auth_type"] = ModelAuthTypeEnum(data["model_auth_type"])

        if "model_jwt_config" in data:
            data["model_jwt_config"] = ModelJwtConfig.from_dict(data["model_jwt_config"])

        # Convert input_modalities strings to enum values
        if "input_modalities" in data:
            data["input_modalities"] = [InputModality(m) for m in data["input_modalities"]]
        
        # Convert output_modalities strings to enum values
        if "output_modalities" in data:
            data["output_modalities"] = [OutputModality(m) for m in data["output_modalities"]]

        # Validate model_provider if present
        if "model_provider" in data:
            provider = data["model_provider"]
            # If it's a string, try to convert it to enum
            if isinstance(provider, str):
                try:
                    data["model_provider"] = ModelProviders(provider)
                except ValueError:
                    valid_providers = [p.value for p in ModelProviders]
                    raise ValueError(f"Invalid model_provider: '{provider}'. Must be one of: {valid_providers}")
            # If it's already an enum instance, keep it as is
            elif not isinstance(provider, ModelProviders):
                valid_providers = [p.value for p in ModelProviders]
                raise ValueError(f"Invalid model_provider type. Valid values: {valid_providers}")

        # # Remove known fields that we don't want in our model
        # unwanted_fields = ["queryParams"]
        # for field in unwanted_fields:
        #     data.pop(field, None)

        # Handle apikeys to apikey conversion
        if "apikeys" in data:
            apikeys = data.pop("apikeys")
            if apikeys and not data.get("apikey"):
                data["apikey"] = apikeys[0]

        # Convert endpoint dict to endpoint_url if present and endpoint_url is not already set
        if "endpoint" in data and not data.get("endpoint_url"):
            endpoint = data.pop("endpoint")
            scheme = endpoint.get("scheme", "https")
            host = endpoint.get("host", "")
            port = endpoint.get("port", "")
            base_path = endpoint.get("base_path", "")

            endpoint_url = f"{scheme}://{host}"
            if port and port not in [80, 443]:
                endpoint_url += f":{port}"
            if base_path:
                base_path = "/" + base_path.strip("/")
                endpoint_url += base_path

            data["endpoint_url"] = endpoint_url

        # Handle nested AuthData
        auth_data = data.pop("auth_data", {})
        auth_data_obj = AuthData.from_dict(auth_data)

        # Handle nested PathsConfig only if present in data
        paths_data = data.pop("paths", None)
        paths_obj = (
            PathsConfig.from_dict(paths_data) if paths_data is not None else None
        )

        return cls(**data, auth_data=auth_data_obj, paths=paths_obj)

    def to_dict(self):
        d = super().to_dict()
        d["model_auth_type"] = self.model_auth_type.value
        if self.model_jwt_config:
            d["model_jwt_config"] = self.model_jwt_config.to_dict()
        # Handle AuthData specifically
        d["auth_data"] = self.auth_data.to_dict()
        # Handle CustomHeader list
        d["custom_headers"] = [header.to_dict() for header in self.custom_headers]
        # Handle ModelProviders enum
        if isinstance(d["model_provider"], ModelProviders):
            d["model_provider"] = d["model_provider"].value
        # Handle input/output modalities
        d["input_modalities"] = [m.value for m in self.input_modalities]
        d["output_modalities"] = [m.value for m in self.output_modalities]
        return d

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(json.loads(json_str))


@dataclass
class ModelConfig(BaseDTO):
    created_at: str = None
    updated_at: str = None
    created_by: str = None
    updated_by: str = None
    model_id: str = None
    model_saved_name: str = None
    model_version: str = None
    testing_for: str = "foundationModels"
    # modality: Modality = Modality.TEXT
    project_name: str = None
    model_name: Optional[str] = "gpt-4o-mini"
    certifications: List[str] = field(default_factory=list)
    model_config: ModelConfigDetails = field(default_factory=ModelConfigDetails)
    is_sample: Optional[bool] = False
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        """Create a ModelConfig instance from a dictionary."""
        # Handle nested ModelConfigDetails
        model_config_data = data.pop("model_config", {})
        try:
            model_config = ModelConfigDetails.from_dict(model_config_data)
        except ValueError as e:
            raise ValueError(f"Error in model_config: {str(e)}")

        # # Handle Modality enum
        # modality_value = data.pop("modality", "text")
        # modality = Modality(modality_value)

        return cls(**data, model_config=model_config)

    def to_dict(self) -> dict:
        """Convert the ModelConfig instance to a dictionary."""
        d = super().to_dict()
        # Handle nested ModelConfigDetails
        d["model_config"] = self.model_config.to_dict()
        return d

    @classmethod
    def __str__(self):
        """String representation of the ModelConfig."""
        return f"ModelConfig(name={self.model_saved_name}, version={self.model_version}, model={self.model_name})"

    def __repr__(self):
        """Detailed string representation of the ModelConfig."""
        return (
            f"ModelConfig({', '.join(f'{k}={v!r}' for k, v in self.to_dict().items())})"
        )


@dataclass
class ModelCollection(BaseDTO):
    models: List[ModelConfig] = field(default_factory=list)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        """Create a ModelCollection instance from a dictionary."""
        models_data = data.get("models", [])
        models = [ModelConfig.from_dict(model_data) for model_data in models_data]
        return cls(models=models)

    def to_dict(self) -> dict:
        return {"models": [model.to_dict() for model in self.models]}

    def to_json(self) -> str:
        """Convert the ModelCollection instance to a JSON string."""
        return json.dumps(self.to_dict())

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the model collection to a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing model data
        """
        data = [model.get_all_fields() for model in self.models]
        return pd.DataFrame(data)

    def display_table(self, style: str = "default") -> str:
        """
        Create a formatted table representation using pandas.

        Args:
            style (str): Style of the output. Options:
                - 'default': Standard pandas HTML table
                - 'styled': Styled HTML table with custom formatting
                - 'markdown': Markdown formatted table

        Returns:
            str: Formatted table string
        """
        if not self.models:
            return "No models available"

        try:
            df = self.to_dataframe()

            if style == "styled":
                styled_df = df.style.set_properties(
                    **{
                        "text-align": "left",
                        "padding": "8px",
                        "border": "1px solid #ddd",
                    }
                )
                styled_df = styled_df.set_table_styles(
                    [
                        {
                            "selector": "thead th",
                            "props": [
                                ("background-color", "#f4f4f4"),
                                ("color", "black"),
                                ("font-weight", "bold"),
                                ("padding", "10px"),
                                ("border", "1px solid #ddd"),
                            ],
                        },
                        {
                            "selector": "tbody tr:nth-child(even)",
                            "props": [("background-color", "#f8f8f8")],
                        },
                    ]
                )
                return styled_df.hide(axis="index").to_html()

            elif style == "markdown":
                return df.to_markdown(index=False)

            else:  # default
                return df.to_html(index=False, classes="model-table")

        except Exception as e:
            return f"Error creating table: {str(e)}"


@dataclass
class Task(BaseDTO):
    """Represents an individual task in a task list."""

    task_id: str
    status: str
    model_name: Optional[str] = None
    test_name: Optional[str] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskList(BaseDTO):
    """Represents a list of tasks."""

    tasks: List[Task] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a TaskList instance from a dictionary."""
        tasks_data = data.get("tasks", [])
        tasks = [Task.from_dict(task_data) for task_data in tasks_data]
        return cls(tasks=tasks)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the TaskList instance to a dictionary."""
        return {"tasks": [task.to_dict() for task in self.tasks]}


# Default configuration
DETAIL_MODEL_CONFIG = ModelConfig()
