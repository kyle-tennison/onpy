"""Interface to OnShape Sketches"""

from typing import TYPE_CHECKING, override
from pyshape.features.base import Feature
from pyshape.features.entities.base import Entity
from pyshape.features.entities.sketch_entities import SketchCircle
import pyshape.api.model as model

if TYPE_CHECKING:
    from pyshape.elements.partstudio import PartStudio
    from pyshape.features.plane import Plane


class Sketch(Feature):

    def __init__(
        self, partstudio: "PartStudio", plane: "Plane", name: str = "New Sketch"
    ) -> None:
        self.plane = plane
        self._partstudio = partstudio
        self._name = name
        self._sketch_id: str | None = None
        self._entities: list[Entity] = []

    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio

    @property
    @override
    def id(self) -> str | None:
        return self._sketch_id

    @property
    def name(self) -> str:
        return self._name

    def add_circle(self, center: tuple[float, float], radius: float) -> None:
        """Adds a circle to the sketch

        Args:
            center: An (x,y) pair of the center of the circle
            radius: The radius of the circle
        """

        # TODO: Add a unit definition system. I'm converting to inches
        # temporarily

        center = (center[0] / 39.37, center[1] / 39.37)
        radius /= 39.37

        entity = SketchCircle(radius, center)
        self._entities.append(entity)

    @override
    def _to_model(self) -> model.Sketch:
        return model.Sketch(
            name=self.name,
            # namespace="",
            featureType="newSketch",
            suppressed=False,
            parameters=[
                model.FeatureParameterQueryList(
                    queries=[
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": [self.plane.id],
                        }
                    ],
                    parameterId="sketchPlane",
                ).model_dump(exclude_none=True)
            ],
            entities=[
                e.to_model().model_dump(exclude_none=True) for e in self._entities
            ],
        )

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"<Sketch on {self.plane}>"
