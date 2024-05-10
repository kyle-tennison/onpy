"""Classes for interacting with queries"""

from textwrap import dedent
from typing import TYPE_CHECKING, override
from onpy.util.misc import unwrap
from onpy.api.versioning import WorkspaceWVM
import onpy.api.model as model
import onpy.entities.queries as qtypes
from onpy.entities import Entity


if TYPE_CHECKING:
    from onpy.features import Sketch
    from onpy.features.base import Feature


class EntityFilter:
    """Object used to list and filter queries"""

    def __init__(self, feature: "Feature", available: list[Entity]) -> None:
        self._available = available
        self._feature = feature
        self._client = feature._client
        self._api = feature._api

    @staticmethod
    def _build_from_sketch(sketch: "Sketch") -> "EntityFilter":
        """Loads available feature from a sketch"""

        featurescript = dedent(
            f"""
        function(context is Context, queries) {{

            var sketch_query = qSketchRegion(makeId(\"{sketch.id}\"), false);
            var sketch_entities = evaluateQuery(context, sketch_query);
            return transientQueriesToStrings(sketch_entities);
                               
        }}
        """
        )

        result = unwrap(
            sketch._api.endpoints.eval_featurescript(
                document_id=sketch.document.id,
                version=WorkspaceWVM(sketch.document.default_workspace.id),
                element_id=sketch.partstudio.id,
                script=featurescript,
                return_type=model.FeaturescriptResponse,
            ).result,
            message="Featurescript has error",
        )

        transient_ids = [i["value"] for i in result["value"]]
        query_entities = [Entity(tid) for tid in transient_ids]

        return EntityFilter(feature=sketch, available=query_entities)

    def _apply_query(self, query: "qtypes.QueryType") -> list[Entity]:
        """Builds the featurescript to evaluate a query and evaluates the featurescript

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

        """
        )

        result = unwrap(
            self._api.endpoints.eval_featurescript(
                self._feature.document.id,
                version=WorkspaceWVM(self._feature.document.default_workspace.id),
                element_id=unwrap(self._feature.partstudio.id),
                script=script,
                return_type=model.FeaturescriptResponse,
            ).result,
            message="Query has error",
        )

        transient_ids = [i["value"] for i in result["value"]]
        query_entities = [Entity(tid) for tid in transient_ids]

        return query_entities

    def contains_point(self, point: tuple[float, float, float]) -> "EntityFilter":
        """Filters out all queries that don't contain the provided point

        Args:
            point: The point to use for filtering
        """

        query = qtypes.qContainsPoint(point=point, units=self._client.units)

        return EntityFilter(feature=self._feature, available=self._apply_query(query))

    def closest_to(self, point: tuple[float, float, float]) -> "EntityFilter":
        """Gets the entity closest to the point

        Args:
            point: The point to use for filtering
        """

        query = qtypes.qClosestTo(point=point, units=self._client.units)

        return EntityFilter(feature=self._feature, available=self._apply_query(query))

    def largest(self) -> "EntityFilter":
        """Gets the largest entity"""

        query = qtypes.qLargest()

        return EntityFilter(feature=self._feature, available=self._apply_query(query))

    def smallest(self) -> "EntityFilter":
        """Gets the smallest entity"""

        query = qtypes.qSmallest()

        return EntityFilter(feature=self._feature, available=self._apply_query(query))

    def intersects(
        self, origin: tuple[float, float, float], direction: tuple[float, float, float]
    ) -> "EntityFilter":
        """Gets the queries that intersect an infinite line

        Args:
            origin: The origin on the line. This can be any point that lays on
                the line.
            direction: The direction vector of the line
        """

        query = qtypes.qIntersectsLine(
            line_origin=origin, line_direction=direction, units=self._client.units
        )

        return EntityFilter(feature=self._feature, available=self._apply_query(query))

    def is_type(self, entity_type: str) -> "EntityFilter":
        """Gets the queries of a specific type

        Args:
            entity_type: The entity type to filter. Supports VERTEX, EDGE,
                FACE, and BODY (case insensitive)
        """

        query = qtypes.qEntityType(
            entity_type=qtypes.EntityType.parse_type(entity_type)
        )

        return EntityFilter(feature=self._feature, available=self._apply_query(query))

    def __str__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"EntityFilter({self._available})"
