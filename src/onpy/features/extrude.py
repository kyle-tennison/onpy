"""Interface to the Extrude Feature.

This script defines the Extrude feature. Currently, only blind, solid extrusions
are supported.

OnPy - May 2024 - Kyle Tennison

"""

from typing import TYPE_CHECKING, override

from onpy.api import schema
from onpy.api.schema import FeatureAddResponse
from onpy.entities import EntityFilter
from onpy.entities.protocols import BodyEntityConvertible, FaceEntityConvertible
from onpy.features.base import Feature
from onpy.part import Part
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Extrude(Feature):
    """Represents an extrusion feature."""

    def __init__(
        self,
        partstudio: "PartStudio",
        faces: FaceEntityConvertible,
        distance: float,
        name: str = "Extrusion",
        merge_with: BodyEntityConvertible | None = None,
        subtract_from: BodyEntityConvertible | None = None,
    ) -> None:
        """Construct an extrude feature.

        Args:
            partstudio: The owning partstudio
            faces: The faces to extrude
            distance: The distance to extrude the faces.
            name: The name of the extrusion feature
            merge_with: Optional body to merge the extrude with.
            subtract_from: Optional body to subtract the extrude volume from.
                Makes the extrusion act as a subtraction.

        """
        self.targets = faces._face_entities()
        self._id: str | None = None
        self._partstudio = partstudio
        self._name = name
        self.distance = distance
        self._merge_with = merge_with
        self._subtract_from = subtract_from

        self._upload_feature()

    def get_created_parts(self) -> list[Part]:
        """Get a list of the parts this feature created."""
        return self._get_created_parts_inner()

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
        # TODO @kyle-tennison: Not currently implemented. Load with items
        return EntityFilter(self.partstudio, available=[])

    @property
    def _extrude_bool_type(self) -> str:
        """Get the boolean type of the extrude. Can be NEW, ADD, or REMOVE."""
        if self._subtract_from is not None:
            return "REMOVE"

        if self._merge_with is not None:
            return "ADD"

        return "NEW"

    @property
    def _boolean_scope(self) -> list[str]:
        """Returns a list of transient ids that define the boolean scope of
        the extrude.
        """
        if self._subtract_from is not None:
            return [e.transient_id for e in self._subtract_from._body_entities()]

        if self._merge_with is not None:
            return [e.transient_id for e in self._merge_with._body_entities()]

        return []

    @override
    def _to_model(self) -> schema.Extrude:
        return schema.Extrude(
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
                    "value": self._extrude_bool_type,
                    "enumName": "NewBodyOperationType",
                    "parameterId": "operationType",
                },
                {
                    "btType": "BTMParameterQueryList-148",
                    "queries": [
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": [e.transient_id for e in self.targets],
                        },
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
                {
                    "btType": "BTMParameterQueryList-148",
                    "queries": [
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": self._boolean_scope,
                        },
                    ],
                    "parameterId": "booleanScope",
                },
            ],
        )

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
