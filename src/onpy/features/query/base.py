"""Interface for OnShape queries"""

from pprint import pprint
from textwrap import dedent
from typing import TYPE_CHECKING
from onpy.api.versioning import WorkspaceWVM
import onpy.api.model as model
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.features import Sketch
    from onpy import Client


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


class QueryList:
    """Object used to list and filter queries"""

    def __init__(self, client: "Client", available: list[QueryEntities]) -> None:
        self._available = available
        self._client = client
        self._api = client._api

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
            client=sketch._client,
            available=query_entities
        )
    
    def __str__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"QueryList({self._available})"
            


        