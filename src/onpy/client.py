"""Client Object - Entry Point.

The Client object is the entry point to OnPy. It handles authentication and
document management.

OnPy - May 2024 - Kyle Tennison

"""

import requests

from onpy.api.rest_api import RestApi
from onpy.document import Document
from onpy.util.credentials import CredentialManager
from onpy.util.exceptions import OnPyApiError, OnPyAuthError, OnPyParameterError
from onpy.util.misc import UnitSystem, find_by_name_or_id


class Client:
    """Handles project management, authentication, and other related items."""

    def __init__(
        self,
        units: str = "inch",
        onshape_access_token: str | None = None,
        onshape_secret_token: str | None = None,
    ) -> None:
        """Args:
        units: The unit system to use. Supports 'inch' and 'metric'.

        """
        self.units = UnitSystem.from_string(units)

        if onshape_access_token and onshape_secret_token:
            self._credentials = (onshape_access_token, onshape_secret_token)
        else:
            self._credentials = CredentialManager.fetch_or_prompt()
        self._api = RestApi(self)

        # check that a request can be made
        try:
            self.list_documents()
        except OnPyApiError as e:
            if e.response is not None and e.response.status_code == requests.codes.unauthorized:
                msg = (
                    "The provided API token is not valid or is no longer valid. "
                    "Run onpy.configure() to update your API tokens."
                )
                raise OnPyAuthError(
                    msg,
                ) from e
            raise

    def list_documents(self) -> list[Document]:
        """Get a list of available documents.

        Returns:
            A list of Document objects

        """
        return [Document(self, model) for model in self._api.endpoints.documents()]

    def get_document(
        self,
        document_id: str | None = None,
        name: str | None = None,
    ) -> Document:
        """Get a document by name or id.

        Args:
            document_id: The id of the document to fetch
            name: The name of the document to fetch

        Returns:
            A list of Document objects

        """
        candidate = find_by_name_or_id(document_id, name, self.list_documents())

        if candidate is None:
            raise OnPyParameterError(
                "Unable to find a document with " + (f"name {name}" if name else f"id {id}"),
            )

        return candidate

    def create_document(self, name: str, description: str | None = None) -> Document:
        """Create a new document.

        Args:
            name: The name of the new document
            description: The description of document

        Returns:
            A Document object of the new document

        """
        return Document(self, self._api.endpoints.document_create(name, description))
