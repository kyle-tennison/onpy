"""Interface to OnShape Sketches"""

from typing import TYPE_CHECKING, override
from pyshape.features.base import Feature, Extrudable
from pyshape.features.entities.base import Entity
from pyshape.features.entities.sketch_entities import SketchCircle
import pyshape.api.model as model
from pyshape.util.misc import unwrap_type, unwrap

if TYPE_CHECKING:
    from pyshape.elements.partstudio import PartStudio
    from pyshape.features.plane import Plane


class Sketch(Feature, Extrudable):

    def __init__(
        self, partstudio: "PartStudio", plane: "Plane", name: str = "New Sketch"
    ) -> None:
        self.plane = plane
        self._partstudio = partstudio
        self._name = name
        self._id: str | None = None
        self._entities: list[Entity] = []

    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio

    @property
    @override
    def id(self) -> str | None:
        return self._id

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
    
    @override
    def _load_response(self, response: model.FeatureAddResponse) -> None:
        """Loads the feature id from the response"""
        self._id = unwrap(response.feature.featureId)

    @property
    @override 
    def _extrusion_query(self) -> str:
        return unwrap(self.id, "Unable to extrude sketch before adding as a feature") 

    @property
    @override
    def _extrusion_parameter_bt_type(self) -> str:
        return "BTMIndividualSketchRegionQuery-140"
    
    @property
    @override 
    def _extrusion_query_key(self) -> str:
        return "featureId"
    

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f'Sketch("{self.name}")'
