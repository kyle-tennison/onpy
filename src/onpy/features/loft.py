"""OnShape extrusion feature"""

from typing import TYPE_CHECKING, override
from onpy.api.model import Feature, FeatureAddResponse
from onpy.features.base import Feature, Extrudable
import onpy.api.model as model
from onpy.util.misc import unwrap
from onpy.entities import EntityFilter

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Loft(Feature):
    """Interface to lofting between two 2D profiles"""

    def __init__(
        self,
        partstudio: "PartStudio",
        start_face: EntityFilter,
        end_face: EntityFilter,
        name: str = "Loft",
    ) -> None:

        self._partstudio = partstudio
        self._id: str | None = None
        self._name = name

        self.start_face = start_face
        self.end_face = end_face

        self._upload_feature()

    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio

    @property
    @override
    def id(self) -> str:
        return unwrap(self._id, "Loft feature id unbound")

    @property
    @override
    def name(self) -> str:
        return self._name

    @property
    @override
    def entities(self) -> EntityFilter:
        return EntityFilter(self, available=[]) # TODO: load with items

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId

    @override
    def _to_model(self) -> model.Loft:

        return model.Loft(
            name=self.name,
            suppressed=False,
            parameters=[
                {
                    "btType": "BTMParameterEnum-145",
                    "namespace": "",
                    "enumName": "ToolBodyType",
                    "value": "SOLID",
                    "parameterId": "bodyType",
                },
                {
                    "btType": "BTMParameterEnum-145",
                    "namespace": "",
                    "enumName": "NewBodyOperationType",
                    "value": "NEW",
                    "parameterId": "operationType",
                },
                {
                    "btType": "BTMParameterEnum-145",
                    "namespace": "",
                    "enumName": "NewSurfaceOperationType",
                    "value": "NEW",
                    "parameterId": "surfaceOperationType",
                },
                {
                    "btType": "BTMParameterArray-2025",
                    "items": [
                        {
                            "btType": "BTMArrayParameterItem-1843",
                            "parameters": [
                                {
                                    "btType": "BTMParameterQueryList-148",
                                    "queries": [
                                        {
                                            "btType": "BTMIndividualQuery-138",
                                            "deterministicIds": [
                                                e.transient_id
                                                for e in self.start_face._available
                                            ],
                                        }
                                    ],
                                    "parameterId": "sheetProfileEntities",
                                }
                            ],
                        },
                        {
                            "btType": "BTMArrayParameterItem-1843",
                            "parameters": [
                                {
                                    "btType": "BTMParameterQueryList-148",
                                    "queries": [
                                        {
                                            "btType": "BTMIndividualQuery-138",
                                            "deterministicIds": [
                                                e.transient_id
                                                for e in self.end_face._available
                                            ],
                                        }
                                    ],
                                    "parameterId": "sheetProfileEntities",
                                }
                            ],
                        },
                    ],
                    "parameterId": "sheetProfilesArray",
                },
            ],
        )
