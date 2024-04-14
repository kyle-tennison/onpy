"""Abstract base element class"""

import pyshape.api.model as model

from abc import abstractmethod, ABC
from typing import Self, TYPE_CHECKING

if TYPE_CHECKING:
    from pyshape.client import Client
    from pyshape.document import Document


class Element(ABC, model.NameIdFetchable):
    """An abstract base class for OnShape elements"""

    def __init__(
        self, client: "Client", model: model.ApiModel, document: "Document"
    ) -> None:
        self._client = client
        self._model = model

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
