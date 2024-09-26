"""

Part interface

In OnShape, Parts are 3D bodies that belong to a partstudio. The OnPy part
interface is defined here

OnPy - May 2024 - Kyle Tennison

"""

from textwrap import dedent
from prettytable import PrettyTable
from typing import TYPE_CHECKING, Any, override

import onpy.api.model as model
from onpy.api.versioning import WorkspaceWVM
from onpy.util.misc import unwrap
from onpy.entities import VertexEntity, EdgeEntity, FaceEntity, BodyEntity
from onpy.entities.filter import EntityFilter
from onpy.entities.protocols import BodyEntityConvertible

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Part(BodyEntityConvertible):
    """Represents a Part in an OnShape partstudio"""

    def __init__(self, partstudio: "PartStudio", model: model.Part) -> None:
        self._partstudio = partstudio
        self._model = model
        self._api = self._partstudio._api
        self._client = self._partstudio._client

    @property
    def id(self) -> str:
        """The part id"""
        return self._model.partId

    @property
    def name(self) -> str:
        """The name of the part"""
        return self._model.name

    def _owned_by_type(self, type: str) -> list[str]:
        """Get the transient ids of the entities owned by this part of a
        certain type.

        Args:
            type: The type of entity to query. Accepts VERTEX, EDGE, FACE, BODY

        Returns:
            A list of transient ids of the resulting queries
        """

        script = dedent(
            f"""
            function(context is Context, queries) {{
                var part = {{ "queryType" : QueryType.TRANSIENT, "transientId" : "{self.id}" }} as Query;    
                var part_faces = qOwnedByBody(part, EntityType.{type.upper()});

                return transientQueriesToStrings( evaluateQuery(context, part_faces) ); 
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

        transient_ids = [i["value"] for i in transient_ids_raw]

        return transient_ids

    def _vertex_entities(self) -> list[VertexEntity]:
        """All of the vertices on this part"""
        return [VertexEntity(tid) for tid in self._owned_by_type("VERTEX")]

    def _edge_entities(self) -> list[EdgeEntity]:
        """All of the edges on this part"""
        return [EdgeEntity(tid) for tid in self._owned_by_type("EDGE")]

    def _face_entities(self) -> list[FaceEntity]:
        """All of the faces on this part"""
        return [FaceEntity(tid) for tid in self._owned_by_type("FACE")]

    def _body_entity(self) -> BodyEntity:
        """The body entity of this part"""
        return BodyEntity(self.id)

    @override
    def _body_entities(self) -> list["BodyEntity"]:
        """Converts the current object into a list of body entities"""
        return [self._body_entity()]

    @property
    def vertices(self) -> EntityFilter[VertexEntity]:
        """An object used for interfacing with vertex entities on this part"""
        return EntityFilter(
            partstudio=self._partstudio, available=self._vertex_entities()
        )

    @property
    def edges(self) -> EntityFilter[EdgeEntity]:
        """An object used for interfacing with edge entities on this part"""
        return EntityFilter(
            partstudio=self._partstudio, available=self._edge_entities()
        )

    @property
    def faces(self) -> EntityFilter[FaceEntity]:
        """An object used for interfacing with face entities on this part"""
        return EntityFilter(
            partstudio=self._partstudio, available=self._face_entities()
        )

    def __repr__(self) -> str:
        return f"Part({self.id})"

    def __str__(self) -> str:
        return repr(self)


class PartList:
    """Interface to listing/getting parts"""

    def __init__(self, parts: list[Part]) -> None:
        self.parts = parts

    def __getitem__(self, index: int) -> Any:
        return self.parts[index]

    def get(self, name: str) -> Part:
        """Gets a part by name. Raises KeyError if not found"""

        try:
            return next(filter(lambda x: x.name.lower() == name.lower(), self.parts))
        except StopIteration:
            raise KeyError(f"No part named '{name}'")

    def get_id(self, id: str) -> Part:
        """Gets a part by id. Raises KeyError if not found"""

        try:
            return next(filter(lambda x: x.id == id.upper(), self.parts))
        except StopIteration:
            raise KeyError(f"No part with id '{id}'")

    def __str__(self) -> str:

        table = PrettyTable(field_names=("Index", "Part Name", "Part ID"))
        for i, part in enumerate(self.parts):
            table.add_row([i, part.name, part.id])

        return str(table)

    def __repr__(self) -> str:
        return f"PartList({[p.id for p in self.parts]})"
