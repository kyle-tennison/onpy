"""Base class for sketches"""

import pyshape.api.model as model
from pyshape.util.exceptions import PyshapeParameterError

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from pyshape.client import Client
    from pyshape.document import Document
    from pyshape.elements.partstudio import PartStudio
    from pyshape.features.plane import Plane


class Feature(ABC):
    """An abstract base class for OnShape elements"""

    @property 
    @abstractmethod
    def partstudio(self) -> "PartStudio":
        """A reference to the owning PartStudio"""

    @property
    def document(self) -> "Document":
        """A reference to the owning document"""
        return self.partstudio.document

    @property
    def _client(self) -> "Client":
        """A reference to the underlying client"""
        return self.document._client

    @property
    @abstractmethod
    def id(self) -> str|None:
        """The id of the feature"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the feature"""
        ...


class FeatureList:
    
    def __init__(self, features: list[Feature]):
        self._features = features

    def __len__(self) -> int:
        """Returns the number of items"""
        return len(self._features)
    
    def __getitem__(self, name: str) -> Feature:
        """Gets an item by its name"""

        matches = [f for f in self._features if f.name == name]

        if len(matches) == 0:
            raise PyshapeParameterError(f"No feature named '{name}'")
        elif len(matches) > 1:
            raise PyshapeParameterError(f"Multiple '{name}' features. Use .get(id=...)")
        else:
            return matches[0] # type: ignore
    
    def __str__(self) -> str:
        msg = "FeatureList(\n"
        for f in self._features:
            msg += f"  {f}\n"
        msg += ")"
        return msg


    @property
    def front_plane(self) -> "Plane":
        return self["Front Plane"] # type: ignore
    
    @property
    def top_plane(self) -> "Plane":
        return self["Top Plane"] # type: ignore
    
    @property
    def right_plane(self) -> "Plane":
        return self["Right Plane"] # type: ignore

        
    