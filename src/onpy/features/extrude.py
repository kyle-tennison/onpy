"""OnShape extrusion feature"""

from typing import TYPE_CHECKING, override
from onpy.api.model import Feature, FeatureAddResponse
from onpy.features.base import Feature, Extrudable
import onpy.api.model as model
from onpy.util.misc import unwrap
from onpy.features.query.list import QueryList

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Extrude(Feature):

    def __init__(
        self,
        partstudio: "PartStudio",
        targets: QueryList | list[Extrudable],
        distance: float,
        name: str = "Extrusion",
    ) -> None:
        self.targets = targets if isinstance(targets, list) else targets._available
        self._id: str | None = None
        self._partstudio = partstudio
        self._name = name
        self.distance = distance

        self._upload_feature()

    @property
    @override
    def id(self) -> str | None:
        return unwrap(self._id, message="Feature id unbound")

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
    def entities(self) -> list:
        return (
            []
        )  # TODO: entities are only really relevant on sketches and actual bodies, not features

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

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
