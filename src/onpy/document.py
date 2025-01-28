"""OnShape Document interface.

OnShape Documents contain multiple elements and versions. This script defines
methods to interact and control these items.

OnPy - May 2024 - Kyle Tennison

"""

import re
from typing import TYPE_CHECKING

from loguru import logger

from onpy.api import schema
from onpy.api.versioning import WorkspaceWVM
from onpy.elements.assembly import Assembly
from onpy.elements.partstudio import PartStudio
from onpy.util.exceptions import OnPyParameterError
from onpy.util.misc import find_by_name_or_id

if TYPE_CHECKING:
    from onpy.client import Client


class Document(schema.NameIdFetchable):
    """Represents an OnShape document. Houses PartStudios, Assemblies, etc."""

    def __init__(self, client: "Client", model: schema.Document) -> None:
        """Construct a new OnShape document from it's schema model.

        Args:
            client: A reference to the client.
            model: The schema model of the document.

        """
        self._model = model
        self._client = client

    @property
    def id(self) -> str:
        """The document's id."""
        return self._model.id

    @property
    def name(self) -> str:
        """The document's name."""
        return self._model.name

    @property
    def default_workspace(self) -> schema.Workspace:
        """The document's default workspace."""
        return self._model.defaultWorkspace

    @property
    def elements(self) -> list[PartStudio | Assembly]:
        """Get the elements that exist on this document."""
        workspace_version = WorkspaceWVM(self.default_workspace.id)
        elements_model_list = self._client._api.endpoints.document_elements(
            self.id,
            workspace_version,
        )

        element_objects: list[PartStudio | Assembly] = []
        for element in elements_model_list:
            if element.elementType == "PARTSTUDIO":
                element_objects.append(PartStudio(self, element))

            if element.elementType == "ASSEMBLY":
                element_objects.append(Assembly(self, element))

        return element_objects

    def delete(self) -> None:
        """Delete the current document."""
        self._client._api.endpoints.document_delete(self.id)

    def list_partstudios(self) -> list[PartStudio]:
        """Get a list of PartStudios that belong to this document."""
        return [e for e in self.elements if isinstance(e, PartStudio)]

    def get_partstudio(
        self,
        element_id: str | None = None,
        name: str | None = None,
        *,
        wipe: bool = True,
    ) -> PartStudio:
        """Fetch a partstudio by name or id. By default, the partstudio
        will be wiped of all features.

        Args:
            element_id: The id of the partstudio OR
            name: The name of the partstudio
            wipe: Wipes the partstudio of all features. DEFAULTS TO TRUE!

        """
        if name is None and element_id is None:
            return self.list_partstudios()[0]

        match = find_by_name_or_id(element_id, name, self.list_partstudios())

        if match is None:
            raise OnPyParameterError(
                "Unable to find a partstudio with "
                + (f"name {name}" if name else f"id {element_id}"),
            )

        if wipe:
            match.wipe()

        return match

    def create_version(self, name: str | None = None) -> None:
        """Create a version from the current workspace.

        Args:
            name: An optional name of the version. Defaults to v1, v2, etc.

        """
        if name is None:
            versions = self._client._api.endpoints.list_versions(self.id)
            for version in versions:
                pattern = r"^V(\d+)$"
                match = re.match(pattern, version.name)
                if match:
                    name = f"V{int(match.group(1)) + 1}"
                    break

            if name is None:
                name = "V1"

        self._client._api.endpoints.create_version(
            document_id=self.id,
            workspace_id=self.default_workspace.id,
            name=name,
        )

        logger.info(f"Created new version {name}")

    def __eq__(self, other: object) -> bool:
        """Check if two documents are the same."""
        return type(other) is type(self) and self.id == getattr(other, "id", None)
