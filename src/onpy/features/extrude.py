"""

Interface to the Extrude Feature

This script defines the Extrude feature. Currently, only blind, solid extrusions
are supported.

OnPy - May 2024 - Kyle Tennison

"""


from typing import TYPE_CHECKING, override
from onpy.api.model import Feature, FeatureAddResponse
from onpy.features.base import Feature
import onpy.api.model as model
from onpy.util.misc import unwrap
from onpy.entities import EntityFilter
from onpy.entities.protocols import FaceEntityConvertible

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Extrude(Feature):

    def __init__(
        self,
        partstudio: "PartStudio",
        faces: FaceEntityConvertible,
        distance: float,
        name: str = "Extrusion",
    ) -> None:
        self.targets = faces._face_entities()
        self._id: str | None = None
        self._partstudio = partstudio
        self._name = name
        self.distance = distance

        self._upload_feature()

    @property
    @override
    def id(self) -> str | None:
        return unwrap(self._id, message="Extrude feature id unbound")

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
    def entities(self) -> EntityFilter:
        return EntityFilter(self, available=[])  # TODO: load with items

    @override
    def _to_model(self) -> model.Extrude:

        return model.Extrude(
            name=self.name,
            featureId=self._id,
            suppressed=False,
            parameters=[
                {
                    "btType": "BTMParameterEnum-145",
                    "parameterId": "bodyType",
                    "value": "SOLID",
                    "enumName": "ExtendedToolBodyType",
                },
                {
                    "btType": "BTMParameterEnum-145",
                    "value": "NEW",
                    "enumName": "NewBodyOperationType",
                    "parameterId": "operationType",
                },
                {
                    "btType": "BTMParameterQueryList-148",
                    "queries": [
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": [e.transient_id for e in self.targets],
                        }
                    ],
                    "parameterId": "entities",
                },
                {
                    "btType": "BTMParameterEnum-145",
                    "enumName": "BoundingType",
                    "value": "BLIND",
                    "parameterId": "endBound",
                },
                {
                    "btType": "BTMParameterQuantity-147",
                    "expression": f"{self.distance} {self._client.units.extension}",
                    "parameterId": "depth",
                },
            ],
        )

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
