"""Used to reference the default planes that OnShape generates"""

from enum import Enum
from textwrap import dedent
from typing import TYPE_CHECKING, override
from onpy.features.base import Feature
from onpy.features.plane import Plane
from onpy.api.versioning import WorkspaceWVM
import onpy.api.model as model

if TYPE_CHECKING:
    from onpy.document import Document
    from onpy.elements.partstudio import PartStudio


class DefaultPlaneOrientation(Enum):
    TOP = "Top"
    FRONT = "Front"
    RIGHT = "Right"


class DefaultPlane(Plane):

    def __init__(self, partstudio: "PartStudio", orientation: DefaultPlaneOrientation):
        self._partstudio = partstudio
        self.orientation = orientation

        self._id = self._load_plane_id()

    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio

    @property
    @override
    def id(self) -> str:
        return self._id

    @property
    @override
    def name(self) -> str:
        return f"{self.orientation.value} Plane"

    def _load_plane_id(self) -> str:
        """Loads the plane id

        Returns:
            The plane ID
        """

        plane_script = dedent(
            """
            function(context is Context, queries) {
                return transientQueriesToStrings(evaluateQuery(context, qCreatedBy(makeId("ORIENTATION"), EntityType.FACE))); 
            }
            """.replace(
                "ORIENTATION", self.orientation.value
            )
        )

        response = self._client._api.endpoints.eval_featurescript(
            document_id=self.document.id,
            version=WorkspaceWVM(self.document.default_workspace.id),
            element_id=self.partstudio.id,
            script=plane_script,
            return_type=model.FeaturescriptResponse,
        )

        # TODO: proper error handling
        plane_id = response.result["value"][0]["value"]
        return plane_id

    @override
    def _to_model(self):
        raise NotImplementedError("Default planes cannot be converted to a model")

    @override
    def _load_response(self, response: model.FeatureAddResponse) -> None:
        raise NotImplementedError("DefaultPlane should not receive a response object")

    def __repr__(self) -> str:
        return f'Plane("{self.name}")'

    def __str__(self) -> str:
        return repr(self)
