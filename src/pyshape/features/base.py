"""Base class for sketches"""

import pyshape.api.model as model

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyshape.client import Client
    from pyshape.document import Document
    from pyshape.elements.partstudio import PartStudio


class Feature(ABC):
    """An abstract base class for OnShape elements"""

    def __init__(self, partstudio: "PartStudio", model: model.ApiModel) -> None:
        self._model = model
        self.partstudio = partstudio

    @property
    @abstractmethod
    def document(self) -> "Document":
        """A reference to the owning document"""
        return self.partstudio.document

    @property
    def _client(self) -> "Client":
        """A reference to the underlying client"""
        return self.document._client

    @property
    @abstractmethod
    def id(self) -> str:
        """The id of the feature"""
        ...