"""PartStudio element interface"""

from loguru import logger
from onpy.elements.base import Element
import onpy.api.model as model
from onpy.features.base import Feature, FeatureList, Extrudable
from onpy.features.default_planes import DefaultPlane, DefaultPlaneOrientation
from onpy.api.versioning import WorkspaceWVM
from onpy.util.exceptions import PyshapeFeatureError
from onpy.util.misc import unwrap
from onpy.features import Sketch, Extrude, Plane
from onpy.features.query.list import QueryList

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from onpy.client import Client
    from onpy.document import Document


class PartStudio(Element):

    def __init__(
        self,
        document: "Document",
        model: model.Element,
    ) -> None:
        self._model = model
        self._document = document
        self._features: list[Feature] = []

        self._features.extend(self._get_default_planes())

    @property
    @override
    def document(self) -> "Document":
        return self._document

    @property
    @override
    def id(self) -> str:
        """The element id of the PartStudio"""
        return self._model.id

    @property
    @override
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

    def add_sketch(self, plane: Plane, name: str = "New Sketch") -> Sketch:
        """Adds a new sketch to the partstudio

        Args:
            plane: The plane to base the sketch off of
            name: An optional name for the sketch
        """
        return Sketch(partstudio=self, plane=plane, name=name)

    def add_extrude(
        self,
        targets: QueryList | list[Extrudable],
        distance: float,
        name: str = "New Extrude",
    ) -> Extrude:
        """Adds a new blind extrude feature to the partstudio

        Args:
            targets: The targets to extrude
            distance: The distance to extrude
            name: An optional name for the extrusion
        """
        return Extrude(partstudio=self, targets=targets, distance=distance, name=name)

    def wipe(self) -> None:
        """Removes all features from the current partstudio. Stores in another version"""

        self.document.create_version()

        features = self._api.endpoints.list_features(
            document_id=self._document.id,
            version=WorkspaceWVM(self._document.default_workspace.id),
            element_id=self.id,
        )

        for feature in features:
            self._api.endpoints.delete_feature(
                document_id=self._document.id,
                workspace_id=self._document.default_workspace.id,
                element_id=self.id,
                feature_id=unwrap(feature.featureId),
            )

    def __repr__(self) -> str:
        return super().__repr__()
