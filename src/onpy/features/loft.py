"""OnShape extrusion feature"""

from typing import TYPE_CHECKING, override
from onpy.api.model import Feature, FeatureAddResponse
from onpy.features.base import Feature, Extrudable
import onpy.api.model as model
from onpy.util.misc import unwrap
from onpy.features.query.list import QueryList

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Loft(Feature):
    """Interface to lofting between two 2D profiles"""

    def __init__(self, partstudio: "PartStudio", start_face: QueryList, end_face: QueryList, name: str = "Loft") -> None:

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
    def entities(self):
        raise NotImplementedError()

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId

    @override
    def _to_model(self) -> model.Loft:

        return model.Loft(
            name=self.name,
            suppressed=False,
            parameters=[{
                "btType": "BTMParameterEnum-145",
                "namespace": "",
                "enumName": "ToolBodyType",
                "value": "SOLID",
                "parameterId": "bodyType"
            },
                {
                "btType": "BTMParameterEnum-145",
                "namespace": "",
                "enumName": "NewBodyOperationType",
                "value": "NEW",
                "parameterId": "operationType"
            },
                {
                "btType": "BTMParameterEnum-145",
                "namespace": "",
                "enumName": "NewSurfaceOperationType",
                "value": "NEW",
                "parameterId": "surfaceOperationType"
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
                                        "deterministicIds": [e.transient_id for e in self.start_face._available],
                                    }
                                ],
                                "parameterId": "sheetProfileEntities"
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
                                        "deterministicIds": [e.transient_id for e in self.end_face._available],
                                    }
                                ],
                                "parameterId": "sheetProfileEntities"
                            }
                        ],
                    }
                ],
                "parameterId": "sheetProfilesArray"
            },
            #     {
            #     "btType": "BTMParameterArray-2025",
            #     "items": [],
            #     "nodeId": "FKJRPR+5yp4LMoAx",
            #     "parameterId": "wireProfilesArray"
            # },
            #     {
            #     "btType": "BTMParameterEnum-145",
            #     "namespace": "",
            #     "nodeId": "behN71BhJsC1TJCj",
            #     "enumName": "LoftEndDerivativeType",
            #     "value": "DEFAULT",
            #     "parameterId": "startCondition"
            # },
            #     {
            #     "btType": "BTMParameterQueryList-148",
            #     "queries": [],
            #     "nodeId": "XALTjX0Z7V3uvrk+",
            #     "parameterId": "adjacentFacesStart"
            # },
            #     {
            #     "btType": "BTMParameterQuantity-147",
            #     "isInteger": True,
            #     "value": 0,
            #     "units": "",
            #     "expression": "1",
            #     "nodeId": "jjhTUvVAzWCyHO9O",
            #     "parameterId": "startMagnitude"
            # },
            #     {
            #     "btType": "BTMParameterEnum-145",
            #     "namespace": "",
            #     "nodeId": "k9UzS6QqXTbFmjj/",
            #     "enumName": "LoftEndDerivativeType",
            #     "value": "DEFAULT",
            #     "parameterId": "endCondition"
            # },
            #     {
            #     "btType": "BTMParameterQueryList-148",
            #     "queries": [],
            #     "nodeId": "pY4GxVbhuW8P+fxp",
            #     "parameterId": "adjacentFacesEnd"
            # },
            #     {
            #     "btType": "BTMParameterQuantity-147",
            #     "isInteger": false,
            #     "value": 0,
            #     "units": "",
            #     "expression": "1",
            #     "nodeId": "4dmMo1aEIsqbtXky",
            #     "parameterId": "endMagnitude"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": false,
            #     "nodeId": "GeUHQCA0ey6DRVCw",
            #     "parameterId": "trimProfiles"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": false,
            #     "nodeId": "b1zUIJ/uaPLZdwsH",
            #     "parameterId": "addGuides"
            # },
            #     {
            #     "btType": "BTMParameterArray-2025",
            #     "items": [],
            #     "nodeId": "R9I9xV34vlTavMmD",
            #     "parameterId": "guidesArray"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": true,
            #     "nodeId": "NSoaUDeErnixYecY",
            #     "parameterId": "trimGuidesByProfiles"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": false,
            #     "nodeId": "F9xSxguQBxYlluLW",
            #     "parameterId": "addSections"
            # },
            #     {
            #     "btType": "BTMParameterQueryList-148",
            #     "queries": [],
            #     "nodeId": "6/jn1yIVdT+7e0q0",
            #     "parameterId": "spine"
            # },
            #     {
            #     "btType": "BTMParameterQuantity-147",
            #     "isInteger": true,
            #     "value": 0,
            #     "units": "",
            #     "expression": "5",
            #     "nodeId": "PSRGlB3Jmbc+gQsl",
            #     "parameterId": "sectionCount"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": false,
            #     "nodeId": "o4pijFp72BLlI49v",
            #     "parameterId": "matchConnections"
            # },
            #     {
            #     "btType": "BTMParameterArray-2025",
            #     "items": [],
            #     "nodeId": "ZtABlux8KN7nmxyD",
            #     "parameterId": "connections"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": false,
            #     "nodeId": "JzCW9B1y84uUZKT6",
            #     "parameterId": "makePeriodic"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": false,
            #     "nodeId": "kt66UQx7d1QEW0tb",
            #     "parameterId": "showIsocurves"
            # },
            #     {
            #     "btType": "BTMParameterQuantity-147",
            #     "isInteger": true,
            #     "value": 0,
            #     "units": "",
            #     "expression": "10",
            #     "nodeId": "6ueOChp+6fUXCpO7",
            #     "parameterId": "curveCount"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": false,
            #     "nodeId": "t0CrK2eMA96Hu599",
            #     "parameterId": "defaultScope"
            # },
            #     {
            #     "btType": "BTMParameterQueryList-148",
            #     "queries": [],
            #     "nodeId": "3nRp2Je+rBZpc5BY",
            #     "parameterId": "booleanScope"
            # },
            #     {
            #     "btType": "BTMParameterBoolean-144",
            #     "value": true,
            #     "nodeId": "oJ7zfqBoUGns6IPa",
            #     "parameterId": "defaultSurfaceScope"
            # },
            #     {
            #     "btType": "BTMParameterQueryList-148",
            #     "queries": [],
            #     "nodeId": "Xk7PfGJxOsL3REpo",
            #     "parameterId": "booleanSurfaceScope"
            # }
            ]
        )
