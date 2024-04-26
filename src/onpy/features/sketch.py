"""Interface to OnShape Sketches"""

from typing import TYPE_CHECKING, override

from loguru import logger
from onpy.features.base import Feature, Extrudable
from onpy.features.entities.base import Entity
from onpy.features.entities.sketch_entities import SketchCircle, SketchLine
import onpy.api.model as model
from onpy.util.misc import unwrap_type, unwrap, Point2D, UnitSystem

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio
    from onpy.features.plane import Plane


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

        logger.info(f"Added circle to sketch: {entity}")

        self._entities.append(entity)

    def add_line(self, start: tuple[float, float], end: tuple[float, float]) -> None:
        """Adds a line to the sketch

        Args:
            start: The starting point of the line
            end: The ending point of the line
        """

        start_point = Point2D.from_pair(start)
        end_point = Point2D.from_pair(end)

        entity = SketchLine(start_point, end_point, self._client.units)

        logger.info(f"Added line to sketch: {entity}")

        self._entities.append(entity)

    def trace_points(
        self, *points: tuple[float, float], end_connect: bool = True
    ) -> None:
        """Traces a series of points

        Args:
            points: A list of points to trace. Uses list order for line
            end_connect: Connects end points of the trace with an extra segment
                to create a closed loop. Defaults to True.
        """

        segments: list[tuple[Point2D, Point2D]] = []

        for idx in range(1, len(points)):

            p1 = Point2D.from_pair(points[idx - 1])
            p2 = Point2D.from_pair(points[idx])

            segments.append((p1, p2))

        if end_connect:
            segments.append(
                (Point2D.from_pair(points[0]), Point2D.from_pair(points[-1]))
            )

        for p1, p2 in segments:
            self.add_line(p1.as_tuple, p2.as_tuple)

    def add_corner_rectangle(
        self, corner_1: tuple[float, float], corner_2: tuple[float, float]
    ) -> None:
        """Adds a corner rectangle to the sketch

        Args:
            corner_1: The point of the first corner
            corner_2: The point of the corner opposite to corner 1
        """

        p1 = Point2D.from_pair(corner_1)
        p2 = Point2D.from_pair(corner_2)

        self.trace_points((p1.x, p1.y), (p2.x, p1.y), (p2.x, p2.y), (p1.x, p2.y))

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
