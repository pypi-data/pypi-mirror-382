from abc import ABC, abstractmethod
from typing import Generic, TypeVar

DataType = TypeVar("DataType")


class BaseProvider(ABC, Generic[DataType]):
    """
    Abstract base class for different types of providers.

    Properties:
        name (str): identifier of concrete provider
        provider_ctx (str): brief description of concrete provider

    Methods:
        run: abstract method to be defined by concrete class, retrieves data from provider
        arun: optional asynchronous method to be defined by concrete class
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the provider."""
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_ctx(self) -> str:
        """Get informational context about the provider."""
        raise NotImplementedError

    @abstractmethod
    def run(self, *args, **kwargs) -> DataType:
        """Synchronously run the provider and return the result."""
        raise NotImplementedError

    async def arun(self, *args, **kwargs) -> DataType:
        """Asynchronously run the provider and return the result."""
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> DataType:
        """Call the provider and return the result."""
        return self.run(*args, **kwargs)
