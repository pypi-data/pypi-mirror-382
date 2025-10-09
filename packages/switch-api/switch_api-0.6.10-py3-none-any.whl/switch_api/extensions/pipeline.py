from abc import ABC, abstractmethod
import uuid

from .helpers import HasExtensionClsAttributeName


class ExtensionTask(ABC):
    """An Abstract Base Class called ExtensionTask for providing extension functionality to the Task classes.

    Attributes
    ----------
    id : uuid.UUID
        Unique identifier of the task. This is an abstract property that needs to be overwritten when sub-classing.
        A new unique identifier can be created using uuid.uuid4()
    description : str
        Brief description of the extension.
    author : str
        The author of the extension.
    version : str
        The version of the extension.

    """

    def __init__(self):
        # Set attribute on the class to identify that it is an extension
        if not hasattr(self, HasExtensionClsAttributeName):
            setattr(self, HasExtensionClsAttributeName, True)

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:
        """Unique identifier of the task. Create a new unique identifier using uuid.uuid4() """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of the task"""
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        """"The author of the task."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """The version of the task"""
        pass