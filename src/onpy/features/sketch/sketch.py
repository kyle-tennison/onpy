"""

Interface to the Sketch Feature

This script defines the Sketch feature. Because sketches are naturally the
most complex feature, it has been moved to its own submodule.

OnPy - May 2024 - Kyle Tennison

"""

import math
from textwrap import dedent
import numpy as np
from loguru import logger
from typing import TYPE_CHECKING, override

import onpy.api.model as model
from onpy.entities import EntityFilter
from onpy.features.base import Feature
from onpy.api.versioning import WorkspaceWVM
from onpy.entities import Entity, FaceEntity, VertexEntity, EdgeEntity
from onpy.util.exceptions import OnPyFeatureError
from onpy.util.misc import unwrap, Point2D, UnitSystem
from onpy.features.sketch.sketch_items import SketchItem
from onpy.entities.protocols import FaceEntityConvertible
from onpy.features.sketch.sketch_items import SketchCircle, SketchLine, SketchArc

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio
    from onpy.features.planes import Plane


class Sketch(Feature, FaceEntityConvertible):
    """The OnShape Sketch Feature, used to build 2D geometries"""

    def __init__(
        self,
        partstudio: "PartStudio",
        plane: "Plane|FaceEntityConvertible",
        name: str = "New Sketch",
    ) -> None:
        self.plane = plane
        self._partstudio = partstudio
        self._name = name
        self._id: str | None = None
        self._items: list[SketchItem] = []

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
    def sketch_items(self) -> list[SketchItem]:
        """A list of items that were added to the sketch"""
        return self._items

    def add_circle(
        self,
        center: tuple[float, float],
        radius: float,
        units: UnitSystem | None = None,
    ) -> SketchCircle:
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

        item = SketchCircle(
            sketch=self, radius=radius, center=center_point, units=self._client.units
        )

        logger.info(f"Added circle to sketch: {item}")
        self._items.append(item)
        self._update_feature()

        return item

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

        item = SketchLine(self, start_point, end_point, self._client.units)

        logger.info(f"Added line to sketch: {item}")

        self._items.append(item)
        self._update_feature()
        return item

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

        item = SketchArc(
            sketch=self,
            radius=radius,
            center=center,
            theta_interval=(math.radians(start_angle), math.radians(end_angle)),
            units=self._client.units,
        )

        self._items.append(item)
        logger.info("Successfully added arc to sketch")
        self._update_feature()
        return item

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
        a = math.sqrt((vertex_1.x - center.x) ** 2 + (vertex_1.y - center.y) ** 2)
        b = math.sqrt((vertex_2.x - center.x) ** 2 + (vertex_2.y - center.y) ** 2)
        c = math.sqrt((vertex_1.x - vertex_2.x) ** 2 + (vertex_1.y - vertex_2.y) ** 2)

        opening_angle = math.acos((a**2 + b**2 - c**2) / (2 * a * b))

        # find the vector that is between the two lines
        line_1_vec = np.array(line_1.dir.as_tuple)
        line_2_vec = np.array(line_2.dir.as_tuple)

        line_1_angle = math.atan2(line_1_vec[1], line_1_vec[0]) % (math.pi * 2)
        line_2_angle = math.atan2(line_2_vec[1], line_2_vec[0]) % (math.pi * 2)

        center_angle = (
            np.average((line_1_angle, line_2_angle)) + math.pi / 2
        )  # relative to x-axis

        # find the distance of the fillet centerpoint from the intersection point
        arc_center_offset = radius / math.sin(opening_angle / 2)
        line_dir = Point2D(
            math.cos(center_angle), math.sin(center_angle)
        )  # really is a vector, not a point

        # find which direction to apply the offset
        if math.degrees(np.dot(np.array(line_dir.as_tuple), line_1_vec)) < 0:
            arc_center = line_dir * arc_center_offset + center  # make an initial guess
        else:
            arc_center = line_dir * -arc_center_offset + center  # make an initial guess

        # find the closest point to the line
        t = (arc_center.x - line_1.start.x) * math.cos(line_1_angle) + (
            arc_center.y - line_1.start.y
        ) * math.sin(line_1_angle)
        line_1_tangent_point = Point2D(
            math.cos(line_1_angle) * t + line_1.start.x,
            math.sin(line_1_angle) * t + line_1.start.y,
        )
        t = (arc_center.x - line_2.start.x) * math.cos(line_2_angle) + (
            arc_center.y - line_2.start.y
        ) * math.sin(line_2_angle)
        line_2_tangent_point = Point2D(
            math.cos(line_2_angle) * t + line_2.start.x,
            math.sin(line_2_angle) * t + line_2.start.y,
        )

        # shorten line segments
        if center == line_1.start:
            line_1.start = line_1_tangent_point
            line_2.start = line_2_tangent_point
        else:
            line_1.end = line_1_tangent_point
            line_2.start = line_2_tangent_point

        # add arc
        arc = SketchArc.three_point_with_midpoint(
            sketch=self,
            radius=radius,
            center=arc_center,
            endpoint_1=line_1_tangent_point,
            endpoint_2=line_2_tangent_point,
            units=self._client.units,
        )
        self._items.append(arc)

        self._update_feature()

        return arc

    @override
    def _to_model(self) -> model.Sketch:

        if isinstance(self.plane, FaceEntityConvertible):
            transient_ids = [e.transient_id for e in self.plane._face_entities()]
        else:
            transient_ids = [self.plane.transient_id]

        return model.Sketch(
            name=self.name,
            featureId=self._id,
            suppressed=False,
            parameters=[
                model.FeatureParameterQueryList(
                    queries=[
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": transient_ids,
                        }
                    ],
                    parameterId="sketchPlane",
                ).model_dump(exclude_none=True),
                {
                    "btType": "BTMParameterBoolean-144",
                    "value": True,
                    "parameterId": "disableImprinting",
                },
            ],
            entities=[i.to_model().model_dump(exclude_none=True) for i in self._items],
        )

    @override
    def _load_response(self, response: model.FeatureAddResponse) -> None:
        """Loads the feature id from the response"""
        self._id = unwrap(response.feature.featureId)

    @property
    @override
    def entities(self) -> EntityFilter:
        """All of the entities on this sketch

        Returns:
            An EntityFilter object used to query entities
        """

        script = dedent(
            f"""
            function(context is Context, queries) {{
                var feature_id = makeId("{self.id}");
                var faces = evaluateQuery(context, qCreatedBy(feature_id));
                return transientQueriesToStrings(faces);
            }}
            """
        )

        response = self._client._api.endpoints.eval_featurescript(
            document_id=self._partstudio.document.id,
            version=WorkspaceWVM(self._partstudio.document.default_workspace.id),
            element_id=self._partstudio.id,
            script=script,
            return_type=model.FeaturescriptResponse,
        )

        transient_ids_raw = unwrap(
            response.result, message="Featurescript failed get entities owned by part"
        )["value"]

        entities = [Entity(i["value"]) for i in transient_ids_raw]

        return EntityFilter(partstudio=self.partstudio, available=entities)

    @override
    def _face_entities(self) -> list[FaceEntity]:
        return self.faces._available

    @property
    def vertices(self) -> EntityFilter[VertexEntity]:
        """An object used for interfacing with vertex entities on this sketch"""
        return EntityFilter(
            partstudio=self._partstudio,
            available=self.entities.is_type(VertexEntity)._available,
        )

    @property
    def edges(self) -> EntityFilter[EdgeEntity]:
        """An object used for interfacing with edge entities on this sketch"""
        return EntityFilter(
            partstudio=self._partstudio,
            available=self.entities.is_type(EdgeEntity)._available,
        )

    @property
    def faces(self) -> EntityFilter[FaceEntity]:
        """An object used for interfacing with face entities on this sketch"""
        return EntityFilter(
            partstudio=self._partstudio,
            available=self.entities.is_type(FaceEntity)._available,
        )

    def mirror(
        self,
        *items: SketchItem,
        line_point: tuple[float, float],
        line_dir: tuple[float, float],
        copy: bool = True,
    ) -> list[SketchItem]:
        """Mirrors sketch items about a line

        Args:
            *items: Any number of sketch items to mirror
            line_point: Any point that lies on the mirror line
            line_dir: The direction of the mirror line
            copy: Whether or not to save a copy of the original entity. Defaults
                to True.

        Returns:
            A lit of the new items added
        """

        if copy:
            items = tuple([i.clone() for i in items])

        return [i.mirror(line_point, line_dir) for i in items]

    def rotate(
        self,
        *items: SketchItem,
        origin: tuple[float, float],
        theta: float,
        copy: bool = False,
    ) -> list[SketchItem]:
        """Rotates sketch items about a point

        Args:
            *items: Any number of sketch items to rotate
            origin: The point to pivot about
            theta: The degrees to rotate by
            copy: Whether or not to save a copy of the original entity. Defaults
                to False.

        Returns:
            A lit of the new items added
        """

        if copy:
            items = tuple([i.clone() for i in items])

        return [i.rotate(origin, theta) for i in items]

    def translate(
        self, *items: SketchItem, x: float = 0, y: float = 0, copy: bool = False
    ) -> list[SketchItem]:
        """Translates sketch items in a cartesian system

        Args:
            *items: Any number of sketch items to translate
            x: The amount to translate in the x-axis
            y: The amount to translate in the y-axis
            copy: Whether or not to save a copy of the original entity. Defaults
                to False.

        Returns:
            A lit of the new items added
        """

        if copy:
            items = tuple([i.clone() for i in items])

        return [i.translate(x, y) for i in items]

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f'Sketch("{self.name}")'
