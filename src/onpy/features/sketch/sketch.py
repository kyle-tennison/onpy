"""Interface to the Sketch Feature.

This script defines the Sketch feature. Because sketches are naturally the
most complex feature, it has been moved to its own submodule.

OnPy - May 2024 - Kyle Tennison

"""

import copy
import math
from collections.abc import Sequence
from textwrap import dedent
from typing import TYPE_CHECKING, override

import numpy as np
from loguru import logger

from onpy.api import schema
from onpy.api.versioning import WorkspaceWVM
from onpy.entities import EdgeEntity, Entity, EntityFilter, FaceEntity, VertexEntity
from onpy.entities.protocols import FaceEntityConvertible
from onpy.features.base import Feature
from onpy.features.sketch.sketch_items import (
    SketchArc,
    SketchCircle,
    SketchItem,
    SketchLine,
)
from onpy.util.exceptions import OnPyFeatureError
from onpy.util.misc import Point2D, UnitSystem, unwrap

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio
    from onpy.features.planes import Plane


class Sketch(Feature, FaceEntityConvertible):
    """The OnShape Sketch Feature, used to build 2D geometries."""

    def __init__(
        self,
        partstudio: "PartStudio",
        plane: "Plane|FaceEntityConvertible",
        name: str = "New Sketch",
    ) -> None:
        """Construct a new sketch.

        Args:
            partstudio: The partstudio that owns the sketch.
            plane: The plane to base the sketch on.
            name: The name of the sketch entity.

        """
        self.plane = plane
        self._partstudio = partstudio
        self._name = name
        self._id: str | None = None
        self._items: set[SketchItem] = set()

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
        """The name of the sketch."""
        return self._name

    @property
    def sketch_items(self) -> Sequence[SketchItem]:
        """A list of items that were added to the sketch."""
        return list(self._items)

    def add_circle(
        self,
        center: tuple[float, float],
        radius: float,
        units: UnitSystem | None = None,
    ) -> SketchCircle:
        """Add a circle to the sketch.

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
            sketch=self,
            radius=radius,
            center=center_point,
            units=self._client.units,
        )

        logger.info(f"Added circle to sketch: {item}")
        self._items.add(item)
        self._update_feature()

        return item

    def add_line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> SketchLine:
        """Add a line to the sketch.

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

        self._items.add(item)
        self._update_feature()
        return item

    def trace_points(
        self,
        *points: tuple[float, float],
        end_connect: bool = True,
    ) -> list[SketchLine]:
        """Traces a series of points.

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
                (Point2D.from_pair(points[0]), Point2D.from_pair(points[-1])),
            )

        lines = []

        for p1, p2 in segments:
            lines.append(self.add_line(p1.as_tuple, p2.as_tuple))

        return lines

    def add_corner_rectangle(
        self,
        corner_1: tuple[float, float],
        corner_2: tuple[float, float],
    ) -> None:
        """Add a corner rectangle to the sketch.

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
        """Add a centerpoint arc to the sketch.

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

        self._items.add(item)
        logger.info("Successfully added arc to sketch")
        self._update_feature()
        return item

    def add_fillet(
        self,
        line_1: SketchLine,
        line_2: SketchLine,
        radius: float,
    ) -> SketchArc:
        """Create a fillet between two lines by shortening them and adding an
        arc in between. Returns the added arc.

        Args:
            line_1: Line to fillet
            line_2: Other line to fillet
            radius: Radius of the fillet

        Returns:
            A SketchArc of the added arc. Updates line_1 and line_2

        """
        if line_1 == line_2:
            msg = "Cannot create a fillet between the same line"
            raise OnPyFeatureError(msg)

        if self._client.units is UnitSystem.INCH:
            radius *= 0.0254

        if Point2D.approx(line_1.start, line_2.start):
            line_1.start = line_2.start
            center = line_1.start
            vertex_1 = line_1.end
            vertex_2 = line_2.end
        elif Point2D.approx(line_1.end, line_2.start):
            line_1.end = line_2.start
            center = line_1.end
            vertex_1 = line_1.start
            vertex_2 = line_2.end
        elif Point2D.approx(line_1.start, line_2.end):
            line_1.start = line_2.end
            center = line_1.start
            vertex_1 = line_1.end
            vertex_2 = line_2.start
        elif Point2D.approx(line_1.end, line_2.end):
            line_1.end = line_2.end
            center = line_1.end
            vertex_1 = line_1.start
            vertex_2 = line_2.start
        else:
            msg = "Line entities need to share a point for a fillet"
            raise OnPyFeatureError(msg)

        # draw a triangle to find the angle between the two lines using law of cosines
        a = math.sqrt((vertex_1.x - center.x) ** 2 + (vertex_1.y - center.y) ** 2)
        b = math.sqrt((vertex_2.x - center.x) ** 2 + (vertex_2.y - center.y) ** 2)
        c = math.sqrt((vertex_1.x - vertex_2.x) ** 2 + (vertex_1.y - vertex_2.y) ** 2)

        opening_angle = math.acos((a**2 + b**2 - c**2) / (2 * a * b))

        # find the vector that is between the two lines
        line_1_vec = np.array(((vertex_1.x - center.x), (vertex_1.y - center.y)))
        line_2_vec = np.array(((vertex_2.x - center.x), (vertex_2.y - center.y)))

        line_1_angle = math.atan2(line_1_vec[1], line_1_vec[0]) % (math.pi * 2)
        line_2_angle = math.atan2(line_2_vec[1], line_2_vec[0]) % (math.pi * 2)

        center_angle = np.average((line_1_angle, line_2_angle))  # relative to x-axis

        # find the distance of the fillet centerpoint from the intersection point
        arc_center_offset = radius / math.sin(opening_angle / 2)
        line_dir = Point2D(
            math.cos(center_angle),
            math.sin(center_angle),
        )  # really is a vector, not a point

        # find which direction to apply the offset
        arc_center = line_dir * arc_center_offset + center  # make an initial guess

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

        # check to see if distance increased or decreased

        line_1_copy = copy.copy(line_1)
        line_2_copy = copy.copy(line_2)

        # Try shortening lines
        if Point2D.approx(line_1.start, line_2.start):
            line_1_copy.start = line_1_tangent_point
            line_2_copy.start = line_2_tangent_point
        elif Point2D.approx(line_1.end, line_2.start):
            line_1_copy.end = line_1_tangent_point
            line_2_copy.start = line_2_tangent_point
        elif Point2D.approx(line_1.start, line_2.end):
            line_1_copy.start = line_1_tangent_point
            line_2_copy.end = line_2_tangent_point
        elif Point2D.approx(line_1.end, line_2.end):
            line_1_copy.end = line_1_tangent_point
            line_2_copy.end = line_2_tangent_point

        # Check if lines got bigger
        if line_1_copy.length > line_1.length or line_2_copy.length > line_2.length:
            arc_center = line_dir * -arc_center_offset + center  # make an initial guess
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

        # Shorten lines
        if Point2D.approx(line_1.start, line_2.start):
            line_1.start = line_1_tangent_point
            line_2.start = line_2_tangent_point
        elif Point2D.approx(line_1.end, line_2.start):
            line_1.end = line_1_tangent_point
            line_2.start = line_2_tangent_point
        elif Point2D.approx(line_1.start, line_2.end):
            line_1.start = line_1_tangent_point
            line_2.end = line_2_tangent_point
        elif Point2D.approx(line_1.end, line_2.end):
            line_1.end = line_1_tangent_point
            line_2.end = line_2_tangent_point

        # add arc
        arc = SketchArc.three_point_with_midpoint(
            sketch=self,
            radius=radius,
            center=arc_center,
            endpoint_1=line_1_tangent_point,
            endpoint_2=line_2_tangent_point,
            units=self._client.units,
        )
        self._items.add(arc)

        self._update_feature()

        return arc

    @override
    def _to_model(self) -> schema.Sketch:
        if isinstance(self.plane, FaceEntityConvertible):
            transient_ids = [e.transient_id for e in self.plane._face_entities()]
        else:
            transient_ids = [self.plane.transient_id]

        return schema.Sketch(
            name=self.name,
            featureId=self._id,
            suppressed=False,
            parameters=[
                schema.FeatureParameterQueryList(
                    queries=[
                        {
                            "btType": "BTMIndividualQuery-138",
                            "deterministicIds": transient_ids,
                        },
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
    def _load_response(self, response: schema.FeatureAddResponse) -> None:
        """Load the feature id from the response."""
        self._id = unwrap(response.feature.featureId)

    @property
    @override
    def entities(self) -> EntityFilter:
        """All of the entities on this sketch.

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
            """,
        )

        response = self._client._api.endpoints.eval_featurescript(
            document_id=self._partstudio.document.id,
            version=WorkspaceWVM(self._partstudio.document.default_workspace.id),
            element_id=self._partstudio.id,
            script=script,
            return_type=schema.FeaturescriptResponse,
        )

        transient_ids_raw = unwrap(
            response.result,
            message="Featurescript failed get entities owned by part",
        )["value"]

        entities = [Entity(i["value"]) for i in transient_ids_raw]

        return EntityFilter(partstudio=self.partstudio, available=entities)

    @override
    def _face_entities(self) -> list[FaceEntity]:
        return self.faces._available

    @property
    def vertices(self) -> EntityFilter[VertexEntity]:
        """An object used for interfacing with vertex entities on this sketch."""
        return EntityFilter(
            partstudio=self._partstudio,
            available=self.entities.is_type(VertexEntity)._available,
        )

    @property
    def edges(self) -> EntityFilter[EdgeEntity]:
        """An object used for interfacing with edge entities on this sketch."""
        return EntityFilter(
            partstudio=self._partstudio,
            available=self.entities.is_type(EdgeEntity)._available,
        )

    @property
    def faces(self) -> EntityFilter[FaceEntity]:
        """An object used for interfacing with face entities on this sketch."""
        return EntityFilter(
            partstudio=self._partstudio,
            available=self.entities.is_type(FaceEntity)._available,
        )

    def mirror[T: SketchItem](
        self,
        items: Sequence[T],
        line_point: tuple[float, float],
        line_dir: tuple[float, float],
        *,
        copy: bool = True,
    ) -> list[T]:
        """Mirrors sketch items about a line.

        Args:
            items: Any number of sketch items to mirror
            line_point: Any point that lies on the mirror line
            line_dir: The direction of the mirror line
            copy: Whether or not to save a copy of the original entity. Defaults
                to True.

        Returns:
            A list of the new items added

        """
        if copy:
            items = tuple([i.clone() for i in items])

        return [i.mirror(line_point, line_dir) for i in items]

    def rotate[T: SketchItem](
        self,
        items: Sequence[T],
        origin: tuple[float, float],
        theta: float,
        *,
        copy: bool = False,
    ) -> list[T]:
        """Rotates sketch items about a point.

        Args:
            items: Any number of sketch items to rotate
            origin: The point to pivot about
            theta: The degrees to rotate by
            copy: Whether or not to save a copy of the original entity. Defaults
                to False.

        Returns:
            A list of the new items added

        """
        if copy:
            items = tuple([i.clone() for i in items])

        return [i.rotate(origin, theta) for i in items]

    def translate[T: SketchItem](
        self,
        items: Sequence[T],
        x: float = 0,
        y: float = 0,
        *,
        copy: bool = False,
    ) -> list[T]:
        """Translate sketch items in a cartesian system.

        Args:
            items: Any number of sketch items to translate
            x: The amount to translate in the x-axis
            y: The amount to translate in the y-axis
            copy: Whether or not to save a copy of the original entity. Defaults
                to False.

        Returns:
            A list of the new items added

        """
        if copy:
            items = tuple([i.clone() for i in items])

        return [i.translate(x, y) for i in items]

    def circular_pattern[T: SketchItem](
        self,
        items: Sequence[T],
        origin: tuple[float, float],
        num_steps: int,
        theta: float,
    ) -> list[T]:
        """Create a circular pattern of sketch items.

        Args:
            items: Any number of sketch items to include in the pattern
            origin: The point to center the circular pattern about.
            num_steps: The number of steps to take. Does not include original position
            theta: The degrees to rotate per step

        Returns:
            A list of the entities that compose the circular pattern, including the
            original items.

        """
        new_items = []

        for item in items:
            new_items.extend(item.circular_pattern(origin, num_steps, theta))

        self._items.update(new_items)
        return new_items

    def linear_pattern[T: SketchItem](
        self, items: Sequence[T], num_steps: int, x: float = 0, y: float = 0
    ) -> list[T]:
        """Create a linear pattern of sketch items.

        Args:
            items: Any number of sketch items to include in the pattern
            num_steps: THe number of steps to take. Does not include original position
            x: The x distance to travel each step. Defaults to zero
            y: The y distance to travel each step. Defaults to zero

        Returns:
            A list of the entities that compose the linear pattern, including the
            original item.

        """
        new_items = []

        for item in items:
            new_items.extend(item.linear_pattern(num_steps, x, y))

        self._items.update(new_items)
        return new_items

    def __str__(self) -> str:
        """Pretty string representation of the sketch."""
        return repr(self)

    def __repr__(self) -> str:
        """Printable representation of the sketch."""
        return f'Sketch("{self.name}")'
