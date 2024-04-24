"""OnShape extrusion feature"""

from typing import TYPE_CHECKING, override
from pyshape.api.model import Feature, FeatureAddResponse
from pyshape.features.base import Feature, Extrudable
import pyshape.api.model as model

if TYPE_CHECKING:
    from pyshape.elements.partstudio import PartStudio


class Extrude(Feature):

    def __init__(self, partstudio: "PartStudio", targets: list[Extrudable], distance: float, name: str="Extrusion") -> None:
        self.targets = targets
        self._id: str|None = None 
        self._partstudio = partstudio
        self._name = name
        self.distance = distance

    @property
    @override
    def id(self) -> str|None:
        return self._id 
    
    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio
    
    @property
    @override
    def name(self) -> str:
        return self._name 
    
    def _list_queries(self) -> list[dict[str, str]]:
        """Gets a list of queries. Used to build model"""

        queries = []

        for target in self.targets:
            query_dict ={
                "btType": target._extrusion_parameter_bt_type,
                target._extrusion_query_key: target._extrusion_query
            }
            queries.append(query_dict)

        return queries

    @override
    def _to_model(self) -> model.Extrude:
        
        return model.Extrude(
            name=self.name,
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
                "parameterId": "operationType"
                },
                {
                "btType": "BTMParameterQueryList-148",
                "queries": self._list_queries(),
                "parameterId": "entities"
                },
                {
                "btType": "BTMParameterEnum-145",
                "enumName": "BoundingType",
                "value": "BLIND",
                "parameterId": "endBound"
                },
                {
                "btType": "BTMParameterQuantity-147",
                "expression": f"{self.distance} in", # TODO: Add a unit system
                "parameterId": "depth"
                },
                # {
                # "btType": "BTMParameterEnum-145",
                # "parameterId": "domain"
                # },
                # {
                # "btType": "BTMParameterEnum-145",
                # "parameterId": "surfaceOperationType"
                # },
                # {
                # "btType": "BTMParameterEnum-145",
                # "parameterId": "flatOperationType"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "surfaceEntities"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "wallShape"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "midplane"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "thickness1"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "flipWall"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "thickness2"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "thickness"
                # },
                # {
                # "btType": "BTMParameterEnum-145",
                # "parameterId": "endBound"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "oppositeDirection"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "endBoundEntityFace"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "endBoundEntityBody"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "endBoundEntityVertex"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "hasOffset"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "offsetDistance"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "offsetOppositeDirection"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "hasExtrudeDirection"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "extrudeDirection"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "startOffset"
                # },
                # {
                # "btType": "BTMParameterEnum-145",
                # "parameterId": "startOffsetBound"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "startOffsetDistance"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "startOffsetOppositeDirection"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "startOffsetEntity"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "symmetric"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "hasDraft"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "draftAngle"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "draftPullDirection"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "hasSecondDirection"
                # },
                # {
                # "btType": "BTMParameterEnum-145",
                # "parameterId": "secondDirectionBound"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "secondDirectionOppositeDirection"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "secondDirectionDepth"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "secondDirectionBoundEntityFace"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "secondDirectionBoundEntityBody"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "secondDirectionBoundEntityVertex"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "hasSecondDirectionOffset"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "secondDirectionOffsetDistance"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "secondDirectionOffsetOppositeDirection"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "hasSecondDirectionDraft"
                # },
                # {
                # "btType": "BTMParameterQuantity-147",
                # "parameterId": "secondDirectionDraftAngle"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "secondDirectionDraftPullDirection"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "defaultScope"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "booleanScope"
                # },
                # {
                # "btType": "BTMParameterBoolean-144",
                # "parameterId": "defaultSurfaceScope"
                # },
                # {
                # "btType": "BTMParameterQueryList-148",
                # "parameterId": "booleanSurfaceScope"
                # }
            ]
        )
    
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
