"""Filtering mechanism for selecting entities.

In OnShape, entities are usually interacted with through a series of queries.
For instance, one might query the entity that is closest to a point, or the
largest in a set of other entities. The functionality to query, and to join
queries, is defined in EntityFilter.

OnPy - May 2024 - Kyle Tennison

"""

from textwrap import dedent
from typing import TYPE_CHECKING, cast, override

import onpy.entities.queries as qtypes
from onpy.api import schema
from onpy.api.versioning import WorkspaceWVM
from onpy.entities import Entity, FaceEntity
from onpy.entities.protocols import FaceEntityConvertible
from onpy.util.exceptions import OnPyInternalError
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class EntityFilter[T: Entity](FaceEntityConvertible):
    """Object used to list and filter queries."""

    def __init__(self, partstudio: "PartStudio", available: list[T]) -> None:
        """Construct an EntityFilter object.

        Args:
            partstudio: The owning partstudio.
            available: A list of available entities.

        """
        self._available = available
        self._partstudio = partstudio
        self._client = partstudio._client
        self._api = partstudio._api

    @property
    def _entity_type(self) -> type[T]:
        """The class of the generic type T."""
        orig_class = getattr(self, "__orig__class__", None)

        etype = cast(T, orig_class.__args__[0]) if orig_class else Entity

        if not callable(etype):
            etype = Entity  # default to generic entity

        if not issubclass(etype, Entity) or etype is not Entity:
            msg = f"Found illegal etype: {etype}"
            raise OnPyInternalError(msg)

        return cast(type[T], etype)

    @override
    def _face_entities(self) -> list[FaceEntity]:
        return self.is_type(FaceEntity)._available

    def _apply_query(self, query: "qtypes.QueryType") -> list[T]:
        """Build the featurescript to evaluate a query and evaluates the featurescript.

        Args:
            query: The query to apply

        Returns:
            A list of resulting Entity instances

        """
        script = dedent(
            f"""

        function(context is Context, queries){{

            // Combine all transient ids into one query
            const transient_ids = {[e.transient_id for e in self._available]};
            var element_queries is array = makeArray(size(transient_ids));

            var idx = 0;
            for (var tid in transient_ids)
            {{
                var query = {{ "queryType" : QueryType.TRANSIENT, "transientId" : tid }} as Query;
                element_queries[idx] = query;
                idx += 1;
            }}

            var cumulative_query = qUnion(element_queries);

            // Apply specific query
            var specific_query = {query.inject_featurescript("cumulative_query")};
            var matching_entities = evaluateQuery(context, specific_query);
            return transientQueriesToStrings(matching_entities);

        }}

        """,
        )

        result = unwrap(
            self._api.endpoints.eval_featurescript(
                self._partstudio.document.id,
                version=WorkspaceWVM(self._partstudio.document.default_workspace.id),
                element_id=unwrap(self._partstudio.id),
                script=script,
                return_type=schema.FeaturescriptResponse,
            ).result,
            message=f"Query raised error when evaluating fs. Script:\n\n{script}",
        )

        transient_ids = [i["value"] for i in result["value"]]
        return [self._entity_type(transient_id=tid) for tid in transient_ids]

    def contains_point(self, point: tuple[float, float, float]) -> "EntityFilter":
        """Filter out all queries that don't contain the provided point.

        Args:
            point: The point to use for filtering

        """
        query = qtypes.qContainsPoint(point=point, units=self._client.units)

        return EntityFilter[T](
            partstudio=self._partstudio,
            available=self._apply_query(query),
        )

    def closest_to(self, point: tuple[float, float, float]) -> "EntityFilter":
        """Get the entity closest to the point.

        Args:
            point: The point to use for filtering

        """
        query = qtypes.qClosestTo(point=point, units=self._client.units)

        return EntityFilter[T](
            partstudio=self._partstudio,
            available=self._apply_query(query),
        )

    def largest(self) -> "EntityFilter":
        """Get the largest entity."""
        query = qtypes.qLargest()

        return EntityFilter[T](
            partstudio=self._partstudio,
            available=self._apply_query(query),
        )

    def smallest(self) -> "EntityFilter":
        """Get the smallest entity."""
        query = qtypes.qSmallest()

        return EntityFilter[T](
            partstudio=self._partstudio,
            available=self._apply_query(query),
        )

    def intersects(
        self,
        origin: tuple[float, float, float],
        direction: tuple[float, float, float],
    ) -> "EntityFilter":
        """Get the queries that intersect an infinite line.

        Args:
            origin: The origin on the line. This can be any point that lays on
                the line.
            direction: The direction vector of the line

        """
        query = qtypes.qIntersectsLine(
            line_origin=origin,
            line_direction=direction,
            units=self._client.units,
        )

        return EntityFilter[T](
            partstudio=self._partstudio,
            available=self._apply_query(query),
        )

    def is_type[E: Entity](self, entity_type: type[E]) -> "EntityFilter[E]":
        """Get the queries of a specific type.

        Args:
            entity_type: The entity type to filter. Supports VERTEX, EDGE,
                FACE, and BODY (case insensitive)

        """
        query = qtypes.qEntityType(entity_type=entity_type)

        available: list[E] = [entity_type(e.transient_id) for e in self._apply_query(query)]

        return EntityFilter[E](partstudio=self._partstudio, available=available)

    def __str__(self) -> str:
        """Pretty string representation of the filter."""
        return f"EntityFilter({self._available})"
