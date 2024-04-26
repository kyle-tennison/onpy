"""Interface to managing OnShape documents"""

import onpy.api.model as model
from onpy.elements.partstudio import PartStudio
from onpy.elements.assembly import Assembly
from onpy.util.misc import find_by_name_or_id
from onpy.api.versioning import WorkspaceWVM
from onpy.util.exceptions import PyshapeParameterError

from typing import TYPE_CHECKING, Any
from functools import cache

if TYPE_CHECKING:
    from onpy.client import Client


class Document(model.NameIdFetchable):
    """Represents an OnShape document. Houses PartStudios, Assemblies, etc."""

    def __init__(self, client: "Client", model: model.Document) -> None:
        self._model = model
        self._client = client

    @property
    def id(self) -> str:
        """The document's id"""
        return self._model.id

    @property
    def name(self) -> str:
        """The document's name"""
        return self._model.name

    @property
    def default_workspace(self) -> model.Workspace:
        """The document's default workspace"""
        return self._model.defaultWorkspace

    @property
    def elements(self) -> list[PartStudio | Assembly]:
        """Gets the elements that exist on this document"""

        workspace_version = WorkspaceWVM(self.default_workspace.id)
        elements_model_list = self._client._api.endpoints.document_elements(
            self.id, workspace_version
        )

        element_objects: list[PartStudio | Assembly] = []
        for element in elements_model_list:

            if element.elementType == "PARTSTUDIO":
                element_objects.append(PartStudio(self, element))

            if element.elementType == "ASSEMBLY":
                element_objects.append(Assembly(self, element))

        return element_objects

    def delete(self) -> None:
        """Deletes the current document"""

        self._client._api.endpoints.document_delete(self.id)

    def list_partstudios(self) -> list[PartStudio]:
        """Gets a list of PartStudios that belong to this document"""

        return [e for e in self.elements if isinstance(e, PartStudio)]

    def get_partstudio(
        self, id: str | None = None, name: str | None = None
    ) -> PartStudio:
        """Fetches a partstudio by name or id"""

        if name is None and id is None:
            return self.list_partstudios()[0]

        match = find_by_name_or_id(id, name, self.list_partstudios())

        if match is None:
            raise PyshapeParameterError(
                "Unable to find a partstudio with "
                + (f"name {name}" if name else f"id {id}")
            )

        return match

    def __eq__(self, other: Any) -> bool:

        if type(other) is type(self) and self.id == getattr(other, "id", None):
            return True
        else:
            return False
