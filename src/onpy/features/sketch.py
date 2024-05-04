"""Interface to OnShape Sketches"""

import math
from typing import TYPE_CHECKING, override

from loguru import logger
import numpy as np
from onpy.features.base import Feature, Extrudable
from onpy.features.entities.base import Entity
from onpy.features.entities.sketch_entities import SketchCircle, SketchLine, SketchArc
import onpy.api.model as model
from onpy.util.misc import unwrap, Point2D, UnitSystem
from onpy.features.query.list import QueryList
from onpy.util.exceptions import OnPyFeatureError

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

        self._upload_feature()

    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio

    @property
    @override
    def id(self) -> str:
        return unwrap(self._id, message="Feature id unbound")

    @property
    def name(self) -> str:
        return self._name

    @property
    @override
    def entities(self) -> list[Entity]:
        return self._entities

    def add_circle(self, center: tuple[float, float], radius: float, units: UnitSystem|None = None) -> SketchCircle:
        """Adds a circle to the sketch

        Args:
            center: An (x,y) pair of the center of the circle
            radius: The radius of the circle
            units: An optional other unit system to use
        """
        center_point = Point2D.from_pair(center)


        units = units if units else self._client.units

        # API expects metric values
        if units is UnitSystem.INCH:
            center_point *= 0.0254
            radius *= 0.0254

        entity = SketchCircle(
            sketch=self, radius=radius, center=center_point, units=self._client.units
        )

        logger.info(f"Added circle to sketch: {entity}")
        self._entities.append(entity)
        self._update_feature()

        return entity

    def add_line(
        self, start: tuple[float, float], end: tuple[float, float]
    ) -> SketchLine:
        """Adds a line to the sketch

        Args:
            start: The starting point of the line
            end: The ending point of the line
        """

        start_point = Point2D.from_pair(start)
        end_point = Point2D.from_pair(end)

        if self._client.units is UnitSystem.INCH:
            start_point *= 0.0254
            end_point *= 0.0254

        entity = SketchLine(self, start_point, end_point, self._client.units)

        logger.info(f"Added line to sketch: {entity}")

        self._entities.append(entity)
        self._update_feature()
        return entity

    def trace_points(
        self, *points: tuple[float, float], end_connect: bool = True
    ) -> list[SketchLine]:
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


        lines = []

        for p1, p2 in segments:
            lines.append(self.add_line(p1.as_tuple, p2.as_tuple))

        return lines

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

    def add_centerpoint_arc(
        self,
        centerpoint: tuple[float, float],
        radius: float,
        start_angle: float,
        end_angle: float,
    ) -> SketchArc:
        """Adds a centerpoint arc to the sketch

        Args:
            centerpoint: The centerpoint of the arc
            radius: The radius of the arc
            start_angle: The angle to start drawing the arc at
            end_angle: The angle to stop drawing the arc at
        """

        center = Point2D.from_pair(centerpoint)

        if self._client.units is UnitSystem.INCH:
            radius *= 0.0254
            center *= 0.0254

        entity = SketchArc(
            sketch=self,
            radius=radius,
            center=center,
            theta_interval=(math.radians(start_angle), math.radians(end_angle)),
            units=self._client.units,
        )

        self._entities.append(entity)
        self._update_feature()
        return entity
    

    def add_fillet(
            self,
            line_1: SketchLine,
            line_2: SketchLine,
            radius: float,
    ) -> SketchArc:
        """Creates a fillet between two lines by shortening them and adding an
        arc in between. Returns the added arc.
        
        Args:
            line_1: Line to fillet
            line_2: Other line to fillet
            radius: Radius of the fillet

        Returns
            A SketchArc of the added arc. Updates line_1 and line_2

        Raises OnPyFeatureError if
        """

        if self._client.units is UnitSystem.INCH:
            radius *= 0.0254

        if line_1.start == line_2.start:
            center = line_1.start 
            vertex_1 = line_1.end 
            vertex_2 = line_2.end
        elif line_1.end == line_2.start:
            center = line_1.end
            vertex_1 = line_1.start
            vertex_2 = line_2.end
        else:
            raise OnPyFeatureError(f"Line entities need to share a point for a fillet")
        

        # draw a triangle to find the angle between the two lines using law of cosines
        a = math.sqrt((vertex_1.x-center.x)**2 + (vertex_1.y-center.y)**2)
        b = math.sqrt((vertex_2.x-center.x)**2 + (vertex_2.y-center.y)**2)
        c = math.sqrt((vertex_1.x-vertex_2.x)**2 + (vertex_1.y-vertex_2.y)**2)

        opening_angle = math.acos((a**2 + b**2 - c**2)/(2*a*b))

        print("opening angle:", opening_angle, math.degrees(opening_angle))

        # find the vector that is between the two lines
        line_1_vec = np.array(line_1.dir.as_tuple)
        line_2_vec = np.array(line_2.dir.as_tuple) 


        line_1_angle = math.atan2(line_1_vec[1], line_1_vec[0]) % (math.pi * 2)
        line_2_angle = math.atan2(line_2_vec[1], line_2_vec[0]) % (math.pi * 2)

        center_angle = np.average((line_1_angle, line_2_angle)) + math.pi/2 # relative to x-axis

        print("line_1_angle", math.degrees(line_1_angle))
        print("line_2_angle", math.degrees(line_2_angle))
        print("center_angle", math.degrees(center_angle))

        # find the distance of the fillet centerpoint from the intersection point
        arc_center_offset = radius/math.sin(opening_angle/2)
        line_dir = Point2D(math.cos(center_angle), math.sin(center_angle)) # really is a vector, not a point
        
        # Find which direction to apply the offset
        if math.degrees(np.dot(np.array(line_dir.as_tuple), line_1_vec)) < 0:
            arc_center = line_dir * arc_center_offset + center # make an initial guess
        else:
            arc_center = line_dir * -arc_center_offset + center # make an initial guess

        

        self.add_circle((arc_center/0.0254).as_tuple, radius/0.0254)
        self.add_line(start=(0,0), end=(line_dir/0.0254).as_tuple)
        








    @override
    def _to_model(self) -> model.Sketch:
        return model.Sketch(
            name=self.name,
            featureId=self._id,
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

    # def query_point(self, point: tuple[float, float, float]) -> "SketchRegionQuery":
    #     """Gets the sketch region at a specific point"""

    #     return SketchRegionQuery(self, point)

    # TODO: merge this with .entites eventually
    @property
    def queries(self) -> QueryList:
        """The available queries"""

        return QueryList._build_from_sketch(self)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f'Sketch("{self.name}")'


# class SketchRegion(Extrudable):

#     def __init__(self, sketch: Sketch, transient_id: str) -> None:
#         self.sketch = sketch
#         self.transient_id = transient_id

#     @property
#     @override
#     def _extrusion_query(self) -> str:
#         return "query =  { \"queryType\" : QueryType.TRANSIENT, \"transientId\" : \"TRANSIENT_ID\" } as Query;".replace("TRANSIENT_ID", self.transient_id)
#         # return (
#         #     f'query = qContainsPoint(qSketchRegion(makeId("{self.sketch.id}"), false), '
#         #     f" vector([{self.point[0]},{self.point[1]},{self.point[2]}])"
#         #     + ("* inch" if self.sketch._client.units is UnitSystem.INCH else "")
#         #     + ");"
#         # )

#     @property
#     @override
#     def _extrusion_parameter_bt_type(self) -> str:
#         return "BTMIndividualQuery-138"

#     @property
#     @override
#     def _extrusion_query_key(self) -> str:
#         return "queryString"
