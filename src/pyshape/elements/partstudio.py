"""PartStudio element interface"""

from pprint import pprint
from loguru import logger
from pyshape.elements.base import Element
import pyshape.api.model as model
from pyshape.features.base import Feature, FeatureList
from pyshape.features.default_planes import DefaultPlane, DefaultPlaneOrientation
from pyshape.api.versioning import WorkspaceWVM
from pyshape.util.exceptions import PyshapeFeatureError

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from pyshape.client import Client
    from pyshape.document import Document


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

    def add_feature(self, feature: Feature):
        """Adds a feature to the partstudio

        Args:
            feature: The feature to add

        Raises:
            PyshapeFeatureError if the feature fails to load
        """

        fm = feature._to_model()

        pprint(fm.model_dump(exclude_none=True))

        response = self._api.endpoints.add_feature(
            document_id=self.document.id,
            version=WorkspaceWVM(self.document.default_workspace.id),
            element_id=self.id,
            feature=feature._to_model(),
        )

        if response.featureState.featureStatus != "OK":
            raise PyshapeFeatureError("Feature has error")
        else:
            logger.info(f"Successfully added feature '{feature.name}'")

    def __repr__(self) -> str:
        return super().__repr__()
