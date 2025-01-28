"""Interface to the Loft Feature.

This script defines the Loft feature. Lofts generate a solid between
two offset 2D regions

OnPy - May 2024 - Kyle Tennison

"""

from typing import TYPE_CHECKING, override

from onpy.api import schema
from onpy.api.schema import FeatureAddResponse
from onpy.entities import EntityFilter, FaceEntity
from onpy.entities.protocols import FaceEntityConvertible
from onpy.features.base import Feature
from onpy.part import Part
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Loft(Feature):
    """Interface to lofting between two 2D profiles."""

    def __init__(
        self,
        partstudio: "PartStudio",
        start_face: FaceEntityConvertible,
        end_face: FaceEntityConvertible,
        name: str = "Loft",
    ) -> None:
        """Construct a loft feature.

        Args:
            partstudio: The owning partstudio
            start_face: The face to start the loft on
            end_face: The face to end the loft on
            name: The name of the loft feature

        """
        self._partstudio = partstudio
        self._id: str | None = None
        self._name = name

        self.start_faces: list[FaceEntity] = start_face._face_entities()
        self.end_faces: list[FaceEntity] = end_face._face_entities()

        self._upload_feature()

    def get_created_parts(self) -> list[Part]:
        """Get a list of the parts this feature created."""
        return self._get_created_parts_inner()

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
        #  TODO @kyle-tennison: Not currently implemented. Need to load with items.
        return EntityFilter(self.partstudio, available=[])

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId

    @override
    def _to_model(self) -> schema.Loft:
        return schema.Loft(
            name=self.name,
            suppressed=False,
            parameters=[
                {
                    "btType": "BTMParameterEnum-145",
                    "namespace": "",
                    "enumName": "ExtendedToolBodyType",
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
                                                e.transient_id for e in self.start_faces
                                            ],
                                        },
                                    ],
                                    "parameterId": "sheetProfileEntities",
                                },
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
                                                e.transient_id for e in self.end_faces
                                            ],
                                        },
                                    ],
                                    "parameterId": "sheetProfileEntities",
                                },
                            ],
                        },
                    ],
                    "parameterId": "sheetProfilesArray",
                },
            ],
        )
