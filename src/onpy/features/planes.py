"""

Interface to OnShape Planes

There are multiple types of planes in OnShape, all of which are defined here.
There is an abstract plane class used to reconcile these multiple classes.

OnPy - May 2024 - Kyle Tennison

"""

from enum import Enum
from functools import cache
from textwrap import dedent
from abc import abstractmethod
from typing import TYPE_CHECKING, override

import onpy.api.model as model
from onpy.util.misc import unwrap
from onpy.entities import EntityFilter
from onpy.features.base import Feature
from onpy.api.versioning import WorkspaceWVM
from onpy.entities.protocols import FaceEntityConvertible

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Plane(Feature):
    """Abstract Base Class for all Planes"""

    @property
    @override
    def entities(self):
        """NOTE: Plane cannot contain entities, this will always be empty"""
        return EntityFilter(self.partstudio, available=[])

    @property
    @abstractmethod
    def transient_id(self) -> str:
        """Gets the transient ID of the plane"""
        ...

    def __repr__(self) -> str:
        return f'Plane("{self.name}")'

    def __str__(self) -> str:
        return repr(self)


class DefaultPlaneOrientation(Enum):
    """The different orientations that the DefaultPlane can be"""

    TOP = "Top"
    FRONT = "Front"
    RIGHT = "Right"


class DefaultPlane(Plane):
    """Used to reference the default planes that OnShape generates"""

    def __init__(self, partstudio: "PartStudio", orientation: DefaultPlaneOrientation):
        self._partstudio = partstudio
        self.orientation = orientation

    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio

    @property
    @override
    def id(self) -> str:
        return self.transient_id  # we don't need the feature id of the default plane

    @property
    @override
    @cache
    def transient_id(self) -> str:
        return self._load_plane_id()

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

        plane_id = unwrap(
            response.result, message="Featurescript failed to load default plane"
        )["value"][0]["value"]
        return plane_id

    @override
    def _to_model(self):
        raise NotImplementedError("Default planes cannot be converted to a model")

    @override
    def _load_response(self, response: model.FeatureAddResponse) -> None:
        raise NotImplementedError("DefaultPlane should not receive a response object")


class OffsetPlane(Plane):
    """Represents a linearly offset plane"""

    def __init__(
        self,
        partstudio: "PartStudio",
        owner: Plane | FaceEntityConvertible,
        distance: float,
        name: str = "Offset Plane",
    ):
        self._partstudio = partstudio
        self._owner = owner
        self._name = name

        self._id: str | None = None
        self.distance = distance

        self._upload_feature()

    @property
    def owner(self) -> Plane | FaceEntityConvertible:
        return self._owner

    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio

    @property
    @override
    def name(self) -> str:
        return self._name

    @property
    @override
    def id(self) -> str:
        return unwrap(self._id, "Plane id unbound")

    @property
    @override
    def transient_id(self) -> str:

        script = dedent(
            f"""

        function(context is Context, queries) {{

            var feature_id = makeId("{self.id}");
            var face = evaluateQuery(context, qCreatedBy(feature_id, EntityType.FACE))[0];
            return transientQueriesToStrings(face);

        }}
            """
        )

        response = self._client._api.endpoints.eval_featurescript(
            document_id=self.document.id,
            version=WorkspaceWVM(self.document.default_workspace.id),
            element_id=self.partstudio.id,
            script=script,
            return_type=model.FeaturescriptResponse,
        )

        plane_id = unwrap(
            response.result,
            message="Featurescript failed to load offset plane transient id",
        )["value"]
        return plane_id

    def _get_owner_transient_ids(self) -> list[str]:
        """Gets the transient id(s) of the owner"""

        if isinstance(self.owner, Plane):
            return [self.owner.transient_id]
        else:
            return [e.transient_id for e in self.owner._face_entities()]

    @override
    def _to_model(self) -> model.Plane:
        return model.Plane(
            name=self.name,
            parameters=[
                {
                    "btType": "BTMParameterQueryList-148",
                    "queries": [
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": self._get_owner_transient_ids(),
                        }
                    ],
                    "parameterId": "entities",
                },
                {
                    "btType": "BTMParameterEnum-145",
                    "namespace": "",
                    "enumName": "CPlaneType",
                    "value": "OFFSET",
                    "parameterId": "cplaneType",
                },
                {
                    "btType": "BTMParameterQuantity-147",
                    "isInteger": False,
                    "value": 0,
                    "units": "",
                    "expression": f"{abs(self.distance)} {self._client.units.extension}",
                    "parameterId": "offset",
                },
                {
                    "btType": "BTMParameterBoolean-144",
                    "value": self.distance < 0,
                    "nodeId": "MMaw54aRdL0c7OmQp",
                    "parameterId": "oppositeDirection",
                },
            ],
            suppressed=False,
        )

    @override
    def _load_response(self, response: model.FeatureAddResponse) -> None:
        self._id = response.feature.featureId
