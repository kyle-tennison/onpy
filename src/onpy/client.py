"""Entry point to this library"""

from onpy.util.credentials import CredentialManager
from onpy.api.rest_api import RestApi
from onpy.document import Document
from onpy.util.exceptions import PyshapeParameterError
from onpy.util.misc import find_by_name_or_id, UnitSystem

from loguru import logger


class Client:
    """Handles project management, authentication, and other related items"""

    def __init__(self, units: str = "inch") -> None:
        """
        Args:
            units: The unit system to use. Supports 'inch' and 'metric'
        """
        self.units = UnitSystem.from_string(units)
        self._credentials = CredentialManager.fetch_or_prompt()
        self._api = RestApi(self)

    def list_documents(self) -> list[Document]:
        """Gets a list of available documents

        Returns:
            A list of Document objects
        """

        return [Document(self, model) for model in self._api.endpoints.documents()]

    def get_document(self, id: str | None = None, name: str | None = None) -> Document:
        """Gets a document by name or id

        Args:
            id: The id of the document to fetch
            name: The name of the document to fetch

        Returns:
            A list of Document objects
        """

        candidate = find_by_name_or_id(id, name, self.list_documents())

        if candidate is None:
            raise PyshapeParameterError(
                "Unable to find a document with "
                + (f"name {name}" if name else f"id {id}")
            )

        return candidate

    def create_document(self, name: str, description: str | None = None) -> Document:
        """Creates a new document

        Args:
            name: The name of the new document
            description: The description of document

        Returns:
            A Document object of the new document
        """

        return Document(self, self._api.endpoints.document_create(name, description))
