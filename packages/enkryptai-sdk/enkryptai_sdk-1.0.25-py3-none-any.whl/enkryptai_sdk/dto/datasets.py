from .base import BaseDTO
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Tool(BaseDTO):
    name: str
    description: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tool":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description
        }


@dataclass
class DatasetConfig(BaseDTO):
    system_description: str = None
    dataset_name: str = None
    policy_description: str = None
    risk_categories: str = None
    tools: List[Tool] = None
    info_pdf_url: str = None
    max_prompts: int = 100
    scenarios: int = 2
    categories: int = 2
    depth: int = 2
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetCollection(BaseDTO):
    datasets: List[str] = field(default_factory=list)


@dataclass
class DatasetSummary(BaseDTO):
    test_types: List[str] = field(default_factory=list)


@dataclass
class DatasetDataPoint(BaseDTO):
    test_type: str
    scenario: str
    category: str
    prompt: str
    source: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetResponse(BaseDTO):
    dataset: List[DatasetDataPoint] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetResponse":
        dataset_items = [DatasetDataPoint.from_dict(item) for item in data.get("dataset", [])]
        return cls(dataset=dataset_items)

    def to_dict(self) -> Dict[str, Any]:
        return {"dataset": [item.to_dict() for item in self.dataset]}


@dataclass
class DatasetContent(BaseDTO):
    description: str
    test_types: dict
    scenarios: dict
    categories: dict
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetContent":
        return cls(
            description=data.get("description", ""),
            test_types=data.get("test_types", {}),
            scenarios=data.get("scenarios", {}),
            categories=data.get("categories", {}),
        )


@dataclass
class DatasetTaskData(BaseDTO):
    dataset_name: str
    created_at: str
    created_by: str
    started_at: str
    status: str
    system_description: str
    scenarios: int
    categories: int
    depth: int
    policy_description: str
    project_name: str
    info_pdf_url: str
    tools: list
    task_id: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetTaskData":
        return cls(
            dataset_name=data.get("dataset_name", ""),
            created_at=data.get("created_at", ""),
            created_by=data.get("created_by", ""),
            started_at=data.get("started_at", ""),
            status=data.get("status", ""),
            system_description=data.get("system_description", ""),
            scenarios=data.get("scenarios", 0),
            categories=data.get("categories", 0),
            depth=data.get("depth", 0),
            policy_description=data.get("policy_description", ""),
            project_name=data.get("project_name", ""),
            info_pdf_url=data.get("info_pdf_url", ""),
            tools=data.get("tools", []),
            task_id=data.get("task_id", ""),
        )


@dataclass
class DatasetCard(BaseDTO):
    datacard: DatasetContent
    dataset_name: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetCard":
        datacard_content = DatasetContent.from_dict(data.get("datacard", {}))
        return cls(datacard=datacard_content, dataset_name=data.get("dataset_name", ""))

    def to_dict(self) -> Dict[str, Any]:
        return {"datacard": self.datacard.to_dict(), "dataset_name": self.dataset_name}


@dataclass
class DatasetTaskStatus(BaseDTO):
    status: str
    dataset_name: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetTaskStatus":
        return cls(status=data.get("status", ""), dataset_name=data.get("dataset_name", ""))

    def to_dict(self) -> Dict[str, Any]:
        return {"status": self.status, "dataset_name": self.dataset_name}


@dataclass
class DatasetTask(BaseDTO):
    data: DatasetTaskData
    dataset_name: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetTask":
        task_data = DatasetTaskData.from_dict(data.get("data", {}))
        return cls(data=task_data, dataset_name=data.get("dataset_name", ""))

    def to_dict(self) -> Dict[str, Any]:
        return {"data": self.data.to_dict(), "dataset_name": self.dataset_name}


@dataclass
class DatasetAddTaskResponse(BaseDTO):
    task_id: str
    message: Optional[str] = None
