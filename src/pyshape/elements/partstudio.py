"""PartStudio element interface"""

from loguru import logger
from onpy.elements.base import Element
import onpy.api.model as model
from onpy.features.base import Feature, FeatureList
from onpy.features.default_planes import DefaultPlane, DefaultPlaneOrientation
from onpy.api.versioning import WorkspaceWVM
from onpy.util.exceptions import PyshapeFeatureError

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

    def add_feature(self, feature: Feature):
        """Adds a feature to the partstudio

        Args:
            feature: The feature to add

        Raises:
            PyshapeFeatureError if the feature fails to load
        """

        fm = feature._to_model()

        response = self._api.endpoints.add_feature(
            document_id=self.document.id,
            version=WorkspaceWVM(self.document.default_workspace.id),
            element_id=self.id,
            feature=feature._to_model(),
        )

        self._features.append(feature)

        if response.featureState.featureStatus != "OK":
            if response.featureState.featureStatus == "WARNING":
                logger.warning("Feature loaded with warning")
            else:
                raise PyshapeFeatureError("Feature has error")
        else:
            logger.info(f"Successfully added feature '{feature.name}'")

        feature._load_response(response)

    def __repr__(self) -> str:
        return super().__repr__()
