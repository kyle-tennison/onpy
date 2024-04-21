"""PartStudio element interface"""

from pyshape.elements.base import Element
import pyshape.api.model as model
from pyshape.features.base import Feature, FeatureList
from pyshape.features.default_planes import DefaultPlane, DefaultPlaneOrientation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyshape.client import Client
    from pyshape.document import Document


class PartStudio(Element):

    def __init__(
        self, client: "Client", model: model.Element, document: "Document"
    ) -> None:
        super().__init__(client, model, document)
        self._model = model
        self._features: list[Feature] = []

        self._features.extend(self._get_default_planes())

    @property
    def id(self) -> str:
        """The element id of the PartStudio"""
        return self._model.id

    @property
    def name(self) -> str:
        """The name of the PartStudio"""
        return self._model.name

    @property
    def features(self) -> FeatureList:
        """A list of the partstudio's features"""
        return FeatureList(self._features)

    def _get_default_planes(self) -> list[DefaultPlane]:
        """Gets the default planes from the PartStudio"""

        default_planes: list[DefaultPlane] = []

        for orientation in DefaultPlaneOrientation:
            default_planes.append(DefaultPlane(self, orientation))

        return default_planes

    def __repr__(self) -> str:
        return super().__repr__()
