"""OnShape extrusion feature"""

from typing import TYPE_CHECKING, override
from onpy.api.model import Feature, FeatureAddResponse
from onpy.features.base import Feature, Extrudable
import onpy.api.model as model

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Extrude(Feature):

    def __init__(
        self,
        partstudio: "PartStudio",
        targets: list[Extrudable],
        distance: float,
        name: str = "Extrusion",
    ) -> None:
        self.targets = targets
        self._id: str | None = None
        self._partstudio = partstudio
        self._name = name
        self.distance = distance

    @property
    @override
    def id(self) -> str | None:
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
            query_dict = {
                "btType": target._extrusion_parameter_bt_type,
                target._extrusion_query_key: target._extrusion_query,
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
                    "parameterId": "operationType",
                },
                {
                    "btType": "BTMParameterQueryList-148",
                    "queries": self._list_queries(),
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

    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
