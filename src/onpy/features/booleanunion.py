"""Interface to the Boolean Union Feature.

This script defines the Boolean - Union

OnPy - May 2025 - David Burns

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


class BooleanUnion(Feature):
    """Represents an translation feature."""

    def __init__(
        self,
        parts: Part,
        partstudio: "PartStudio",
        keep_tools: bool,
        name: str = "BooleanUnion",
    ) -> None:
        """Construct an boolean union feature.

        Args:
            partstudio: The owning partstudio
            parts: An array of parts to be unioned
            name: The name of the boolean union feature
            keep_tools: Bool to indicate if tools to be kept (same as GUI checkbox)

        """
        self._id: str | None = None
        self.parts = parts
        self._partstudio = partstudio
        self._name = name
        self.keep_tools = keep_tools

        self._upload_feature()


    @property
    @override
    def id(self) -> str | None:
        return unwrap(self._id, message="BooleanUnion feature id unbound")

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

    @override
    def _to_model(self) -> schema.Translate:

        part_ids = [p.id for p in self.parts]

        return schema.Translate(
            name=self.name,
            featureId=self._id,
            featureType="booleanBodies",
            suppressed=False,
            parameters=[


                {
                    "btType": "BTMParameterEnum-145",
                    "enumName": "BooleanOperationType",
                    "value": "UNION",
                    "parameterId": "operationType"
                },
                {
                    "btType": "BTMParameterQueryList-148",
                    "parameterId": "tools",
                    "queries": [
                        {"btType": "BTMIndividualQuery-138", "deterministicIds": part_ids}
                    ]
                },
                {"btType": "BTMParameterBoolean-144", "value": self.keep_tools, "parameterId": "keepTools"}


            ],
        )

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
