"""Interface for OnShape queries"""

from abc import ABC, abstractmethod
from pprint import pprint
from textwrap import dedent
from typing import TYPE_CHECKING, override
from onpy.api.versioning import WorkspaceWVM
import onpy.api.model as model
from onpy.util.misc import unwrap, UnitSystem

if TYPE_CHECKING:
    from onpy.features import Sketch
    from onpy import Client
    from onpy.features.base import Feature


class QueryEntities:
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
    
    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"QueryEntity({self.transient_id})"

class QueryType(ABC):
    """Used to represent the type of a query"""

    @abstractmethod
    def inject_featurescript(self, q_to_filter: str) -> str:
        """The featurescript to inject to create a Query object of this type
        
        Args:
            q_to_filter: The internal query to filter
        """
        ...


class qContainsPoint(QueryType):

    def __init__(self, point: tuple[float, float, float], units: UnitSystem):

        self.point = point 
        self.units = units

    @property
    def point_vector(self) -> str:
        """The Featurescript compatible definition of the point to query"""
        return f"vector([{self.point[0]}, {self.point[1]}, {self.point[2]}]) * {self.units.fs_name}"

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qContainsPoint({q_to_filter}, {self.point_vector})"



class QueryList:
    """Object used to list and filter queries"""

    def __init__(self, feature: "Feature", available: list[QueryEntities]) -> None:
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
        query_entities = [QueryEntities(tid) for tid in transient_ids]

        return QueryList(
            feature=sketch,
            available=query_entities
        )
    

    def _apply_query(self, query: QueryType) -> list[QueryEntities]:
        """Builds the featurescript to evaluate a query and evaluates the featurescript
        
        Args:
            query: The query to apply

        Returns:
            A list of resulting QueryEntities
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
        query_entities = [QueryEntities(tid) for tid in transient_ids]

        return query_entities



    def contains_point(self, point: tuple[float, float, float]) -> "QueryList":
        """Filters out all queries that don't contain the provided point
        
        Args:
            point: The point to use for filtering
        """

        query = qContainsPoint(point=point, units=self._client.units)

        return QueryList(
            feature=self._feature,
            available=self._apply_query(query)
        )






    
    def __str__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"QueryList({self._available})"
            


        