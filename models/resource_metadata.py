from dataclasses import dataclass


@dataclass
class ResourceMetadata:
    """
    Metadata describing a Kaomy resource.
    """

    provider: str
    collector: str
    resource: str
    location: str
    unit: str

    currency: str | None = None
    device_class: str | None = None
    icon: str | None = None

    last_sync: str = ""
    last_reading: str = ""
    version: str = "1.0"
