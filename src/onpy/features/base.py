"""Base class for sketches"""

import onpy.api.model as model
from onpy.util.exceptions import PyshapeParameterError

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterator, Protocol

if TYPE_CHECKING:
    from onpy.client import Client
    from onpy.document import Document
    from onpy.elements.partstudio import PartStudio
    from onpy.features.plane import Plane


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
    def id(self) -> str | None:
        """The id of the feature"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the feature"""
        ...

    @abstractmethod
    def _to_model(self) -> model.Feature:
        """Converts the feature into the corresponding api model"""
        ...

    @abstractmethod
    def _load_response(self, response: model.FeatureAddResponse) -> None:
        """Load the feature add response to the feature metadata"""
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
            return matches[0]  # type: ignore

    def __str__(self) -> str:
        msg = "FeatureList(\n"
        for f in self._features:
            msg += f"  {f}\n"
        msg += ")"
        return msg

    @property
    def front_plane(self) -> "Plane":
        return self["Front Plane"]  # type: ignore

    @property
    def top_plane(self) -> "Plane":
        return self["Top Plane"]  # type: ignore

    @property
    def right_plane(self) -> "Plane":
        return self["Right Plane"]  # type: ignore


class Extrudable(Protocol):
    """Marks an object that can be extruded"""

    @property
    @abstractmethod
    def _extrusion_query(self) -> str:
        """The query used for extrusion"""
        ...

    @property
    @abstractmethod
    def _extrusion_query_key(self) -> str:
        """The JSON filed that points to the _extrusion_query"""
        ...

    @property
    @abstractmethod
    def _extrusion_parameter_bt_type(self) -> str:
        """The btType of the extrudable region. e.g., BTMIndividualSketchRegionQuery-140"""
        ...
