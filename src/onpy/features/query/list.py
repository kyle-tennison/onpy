"""Classes for interacting with queries"""

from textwrap import dedent
from typing import TYPE_CHECKING, override
from onpy.util.misc import unwrap
from onpy.api.versioning import WorkspaceWVM
import onpy.api.model as model
import onpy.features.query.types as qtypes
from onpy.features.base import Extrudable


if TYPE_CHECKING:
    from onpy.features import Sketch, Extrude
    from onpy.features.base import Feature
    


class QueryEntity(Extrudable):
    """Base class for query entities"""

    def __init__(self, transient_id: str):
        self.transient_id = transient_id

    @property
    def as_query(self) -> str:
        """Featurescript expression to convert into query of self"""
        return "{ \"queryType\" : QueryType.TRANSIENT, \"transientId\" : \"TRANSIENT_ID\" } as Query".replace("TRANSIENT_ID", self.transient_id)

    @property
    def as_entity(self) -> str:
        """Featurescript expression to get a reference to this entity"""
        return f"evaluateQuery(context, {self.as_query})[0] "
    
    @property
    @override
    def _extrusion_query(self) -> list[str]:
        return [ self.transient_id ]

    @property
    @override
    def _extrusion_parameter_bt_type(self) -> str:
        return "BTMIndividualQuery-138"

    @property
    @override
    def _extrusion_query_key(self) -> str:
        return "deterministicIds"

    
    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"QueryEntity({self.transient_id})"

class QueryList:
    """Object used to list and filter queries"""

    def __init__(self, feature: "Feature", available: list[QueryEntity]) -> None:
        self._available = available
        self._feature = feature
        self._client = feature._client
        self._api = feature._api

    @staticmethod
    def _build_from_sketch(sketch: "Sketch") -> "QueryList":
        """Loads available feature from a sketch"""

        featurescript = dedent(f"""
        function(context is Context, queries) {{

            var sketch_query = qSketchRegion(makeId(\"{sketch.id}\"), false);
            var sketch_entities = evaluateQuery(context, sketch_query);
            return transientQueriesToStrings(sketch_entities);
                               
        }}
        """)

        result = unwrap(sketch._api.endpoints.eval_featurescript(
            document_id=sketch.document.id,
            version=WorkspaceWVM(sketch.document.default_workspace.id),
            element_id=sketch.partstudio.id,
            script=featurescript,
            return_type=model.FeaturescriptResponse
        ).result,
        message="Featurescript has error")

        transient_ids = [i["value"] for i in result["value"]]
        query_entities = [QueryEntity(tid) for tid in transient_ids]

        return QueryList(
            feature=sketch,
            available=query_entities
        )
    

    def _apply_query(self, query: "qtypes.QueryType") -> list[QueryEntity]:
        """Builds the featurescript to evaluate a query and evaluates the featurescript
        
        Args:
            query: The query to apply

        Returns:
            A list of resulting QueryEntity instances
        """

        script = dedent(f"""
                      
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

        """)

        result =  unwrap(self._api.endpoints.eval_featurescript(
            self._feature.document.id,
            version=WorkspaceWVM(self._feature.document.default_workspace.id),
            element_id=unwrap(self._feature.partstudio.id),
            script=script,
            return_type=model.FeaturescriptResponse
        ).result,
        message="Query has error"
        )

        transient_ids = [i["value"] for i in result["value"]]
        query_entities = [QueryEntity(tid) for tid in transient_ids]

        return query_entities



    def contains_point(self, point: tuple[float, float, float]) -> "QueryList":
        """Filters out all queries that don't contain the provided point
        
        Args:
            point: The point to use for filtering
        """

        query = qtypes.qContainsPoint(point=point, units=self._client.units)

        return QueryList(
            feature=self._feature,
            available=self._apply_query(query)
        )

    def closest_to(self, point: tuple[float, float, float]) -> "QueryList":
        """Gets the entity closest to the point
        
        Args:
            point: The point to use for filtering
        """

        query = qtypes.qClosestTo(point=point, units=self._client.units)

        return QueryList(
            feature=self._feature,
            available=self._apply_query(query)
        )
    
    def largest(self) -> "QueryList":
        """Gets the largest entity"""

        query = qtypes.qLargest()

        return QueryList(
            feature=self._feature,
            available=self._apply_query(query)
        )
    
    def smallest(self) -> "QueryList":
        """Gets the smallest entity"""

        query = qtypes.qSmallest()

        return QueryList(
            feature=self._feature,
            available=self._apply_query(query)
        )
    
    def intersects(self, origin: tuple[float, float, float], direction: tuple[float, float, float]) -> "QueryList":
        """Gets the queries that intersect an infinite line
        
        Args:
            origin: The origin on the line. This can be any point that lays on 
                the line.
            direction: The direction vector of the line
        """

        query = qtypes.qIntersectsLine(
            line_origin=origin,
            line_direction=direction,
            units=self._client.units
        )

        return QueryList(
            feature=self._feature,
            available=self._apply_query(query)
        )
    
    def is_type(self, entity_type: str) -> "QueryList":
        """Gets the queries of a specific type
        
        Args:
            entity_type: The entity type to filter. Supports VERTEX, EDGE,
                FACE, and BODY (case insensitive)
        """

        query = qtypes.qEntityType(
            entity_type=qtypes.EntityType.parse_type(entity_type)
        )

        return QueryList(
            feature=self._feature,
            available=self._apply_query(query)
        )





    
    def __str__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"QueryList({self._available})"
            


        