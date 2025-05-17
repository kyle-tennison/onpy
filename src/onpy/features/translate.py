"""Interface to the Translate Feature.

This script defines the Transform - Translate by XYZ feature.

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


class Translate(Feature):
    """Represents an translation feature."""

    def __init__(
        self,
        partstudio: "PartStudio",
        move_x: float,
        move_y: float,
        move_z: float,
        copy_part: bool,
        name: str = "Translation",
    ) -> None:
        """Construct an translate feature.

        Args:
            partstudio: The owning partstudio
            name: The name of the translation feature
            move_x: The distance to move in x direction
            move_y: The distance to move in y direction
            move_z: The distance to move in z direction
            copy_part: Bool to indicate part should be copied

        """
        self._id: str | None = None
        self._partstudio = partstudio
        self._name = name
        self.move_x = move_x
        self._move_y = move_y
        self._move_z = move_z
        self._copy_part = copy_part

        self._upload_feature()


    @property
    @override
    def id(self) -> str | None:
        return unwrap(self._id, message="Translate feature id unbound")

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
        return schema.Translate(
            name=self.name,
            featureId=self._id,
            featureType="transform",
            suppressed=False,
            parameters=[

                {
                    "btType": "BTMParameterQueryList-148",
                    "parameterId": "entities",
                    "queries": [
                    {
                        "btType": "BTMIndividualQuery-138",
                        "deterministicIds": [self.part_id]
                    }
                    ]
                },
                {
                    "btType": "BTMParameterEnum-145",
                    "namespace": "",
                    "enumName": "TransformType",
                    "value": "TRANSLATION_3D",
                    "parameterId": "transformType"
                },
                {
                    "btType": "BTMParameterQuantity-147",
                    "value": self.move_x,
                    "parameterId": "dx"
                },
                {
                    "btType": "BTMParameterQuantity-147",
                    "value": self.move_y,
                    "parameterId": "dy"
                },
                {
                    "btType": "BTMParameterQuantity-147",
                    "value": self.move_z,
                    "parameterId": "dz"
                },
                {
                    "btType": "BTMParameterBoolean-144",
                    "value": self.make_copy,
                    "parameterId": "makeCopy"
                }

            ],
        )

    @override
    def _load_response(self, response: FeatureAddResponse) -> None:
        self._id = response.feature.featureId
