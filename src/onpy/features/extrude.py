"""

Interface to the Extrude Feature

This script defines the Extrude feature. Currently, only blind, solid extrusions
are supported.

OnPy - May 2024 - Kyle Tennison

"""

from textwrap import dedent
import onpy.api.model as model
from onpy.part import Part
from onpy.util.misc import unwrap
from onpy.entities import EntityFilter
from onpy.features.base import Feature
from typing import TYPE_CHECKING, override
from onpy.api.versioning import WorkspaceWVM
from onpy.api.model import FeatureAddResponse
from onpy.entities.protocols import FaceEntityConvertible, BodyEntityConvertible

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Extrude(Feature):

    def __init__(
        self,
        partstudio: "PartStudio",
        faces: FaceEntityConvertible,
        distance: float,
        name: str = "Extrusion",
        merge_with: BodyEntityConvertible | None = None,
        subtract_from: BodyEntityConvertible | None = None,
    ) -> None:
        self.targets = faces._face_entities()
        self._id: str | None = None
        self._partstudio = partstudio
        self._name = name
        self.distance = distance
        self._merge_with = merge_with
        self._subtract_from = subtract_from

        self._upload_feature()

    def get_created_parts(self) -> list[Part]:
        """Gets a list of the parts this feature created"""
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
        return EntityFilter(self.partstudio, available=[])  # TODO: load with items
    
    @property
    def _extrude_bool_type(self) -> str:
        """Gets the boolean type of the extrude. Can be NEW, ADD, or REMOVE"""
        if self._subtract_from is not None:
            return "REMOVE"
        
        elif self._merge_with is not None:
            return "ADD"
        
        else:
            return "NEW"

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
                {
                    "btType": "BTMParameterQueryList-148",
                    "queries": [
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": (
                                []
                                if self._merge_with is None
                                else [
                                    e.transient_id
                                    for e in self._merge_with._body_entities()
                                ]
                            ),
                        }
                    ],
                    "parameterId": "booleanScope",
                },
            ],
        )

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
