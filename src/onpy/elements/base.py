"""

Abstract base class for OnShape elements

In OnShape, each "tab" you see in the GUI is an "element." For instance,
a partstudio is an element, so is an assembly, and so is a drawing. This script
is the abstract base class for these OnShape elements.

OnPy - May 2024 - Kyle Tennison

"""

from typing import TYPE_CHECKING
from abc import abstractmethod, ABC

import onpy.api.model as model

if TYPE_CHECKING:
    from onpy.client import Client
    from onpy.document import Document
    from onpy.api.rest_api import RestApi


class Element(ABC, model.NameIdFetchable):
    """An abstract base class for OnShape elements"""

    @property
    @abstractmethod
    def document(self) -> "Document":
        """A reference to the current document"""
        ...

    @property
    def _client(self) -> "Client":
        """A reference tot he current client"""
        return self.document._client

    @property
    def _api(self) -> "RestApi":
        """A reference tot he current api"""
        return self._client._api

    @property
    @abstractmethod
    def id(self) -> str:
        """The id of the element"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the element"""
        ...

    @abstractmethod
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    def __str__(self) -> str:
        return repr(self)

    def __eq__(self, other) -> bool:

        if hasattr(other, "id"):
            return other.id == self.id and type(other) is type(self)
        else:
            return False
