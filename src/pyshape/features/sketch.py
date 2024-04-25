"""Interface to OnShape Sketches"""

from typing import TYPE_CHECKING, override
from pyshape.features.base import Feature, Extrudable
from pyshape.features.entities.base import Entity
from pyshape.features.entities.sketch_entities import SketchCircle
import pyshape.api.model as model
from pyshape.util.misc import unwrap_type, unwrap, Point2D, UnitSystem

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
        center_point = Point2D.from_pair(center)

        # API expects metric values
        if self._client.units is UnitSystem.INCH:
            center_point *= 0.0254
            radius *= 0.0254

        entity = SketchCircle(
            radius=radius, center=center_point, units=self._client.units
        )
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

    def query_point(self, point: tuple[float, float, float]) -> "SketchRegionQuery":
        """Gets the sketch region at a specific point"""

        return SketchRegionQuery(self, point)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f'Sketch("{self.name}")'


class SketchRegionQuery(Extrudable):

    def __init__(self, sketch: Sketch, point: tuple[float, float, float]) -> None:
        self.point = point
        self.sketch = sketch

    @property
    @override
    def _extrusion_query(self) -> str:
        return (
            f'query = qContainsPoint(qSketchRegion(makeId("{self.sketch.id}"), false), '
            f" vector([{self.point[0]},{self.point[1]},{self.point[2]}])"
            + ("* inch" if self.sketch._client.units is UnitSystem.INCH else "")
            + ");"
        )

    @property
    @override
    def _extrusion_parameter_bt_type(self) -> str:
        return "BTMIndividualQuery-138"

    @property
    @override
    def _extrusion_query_key(self) -> str:
        return "queryString"
