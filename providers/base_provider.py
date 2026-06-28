from abc import ABC, abstractmethod

from kaomy.models.resource_state import ResourceState


class BaseProvider(ABC):
    """
    Base class for all Kaomy providers.

    A provider is responsible for communicating with an external source
    and returning a normalized ResourceState.
    """

    def __init__(self, name: str, simulation: bool = False):
        self.name = name
        self.simulation = simulation

    @abstractmethod
    def authenticate(self) -> None:
        """
        Authenticate against the external provider.
        """
        pass

    @abstractmethod
    def collect(self) -> ResourceState:
        """
        Collect data from the provider and return a ResourceState.
        """
        pass

    def healthcheck(self) -> bool:
        """
        Return provider availability status.

        Default implementation returns True.
        Providers can override this when needed.
        """
        return True
