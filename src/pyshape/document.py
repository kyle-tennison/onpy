"""Interface to managing OnShape documents"""

import pyshape.api.model as model

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyshape.client import Client


class Document:
    """Represents an OnShape document. Houses PartStudios, Assemblies, etc."""

    def __init__(self, client: "Client", model: model.Document) -> None:
        self._model = model
        self._client = client

    @property
    def id(self) -> str:
        """The document id"""
        return self._model.id

    def delete(self) -> None:
        """Deletes the current document"""

        self._client._api.endpoints.document_delete(self.id)

    def __eq__(self, other: Any) -> bool:

        if type(other) is type(self) and self.id == getattr(other, "id", None):
            return True
        else:
            return False
