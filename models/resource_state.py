from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from kaomy.models.resource_metadata import ResourceMetadata


@dataclass
class ResourceState:
    """
    Normalized state returned by Kaomy providers and used by collectors.
    """

    metadata: ResourceMetadata
    measurements: Dict[str, Any] = field(default_factory=dict)
    analysis: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.__dict__,
            "measurements": self.measurements,
            "analysis": self.analysis,
            "attributes": self.attributes,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceState":
        return cls(
            metadata=ResourceMetadata(**data.get("metadata", {})),
            measurements=data.get("measurements", {}),
            analysis=data.get("analysis", {}),
            attributes=data.get("attributes", {}),
            history=data.get("history", []),
        )

    @staticmethod
    def now_iso() -> str:
        return datetime.now().isoformat(timespec="seconds")
