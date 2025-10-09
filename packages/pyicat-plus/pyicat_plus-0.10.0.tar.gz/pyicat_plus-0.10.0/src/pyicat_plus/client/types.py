import dataclasses
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional
from typing import TypedDict


@dataclasses.dataclass(frozen=True)
class DatasetId:
    name: str
    path: str


@dataclasses.dataclass(frozen=True)
class DatasetMetadata:
    file_count: int


@dataclasses.dataclass(frozen=True)
class Dataset:
    dataset_id: DatasetId
    icat_dataset_id: int
    dataset_metadata: DatasetMetadata

    def as_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dataset":
        """Factory method to create a Dataset instance from a dictionary."""
        data = data.copy()
        data["dataset_id"] = DatasetId(**data["dataset_id"])
        data["dataset_metadata"] = DatasetMetadata(**data["dataset_metadata"])
        return cls(**data)


class ArchiveStatusType(Enum):
    ARCHIVING = "archiving"
    RESTORATION = "restoration"


class ArchiveStatusLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SampleMetadata(TypedDict):
    """
    Sample metadata information
    """

    id: str
    name: str
    linkedSampleAFormName: Optional[str]  # noqa: N815
