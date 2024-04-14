"""Entry point to this library"""

from pyshape.util.credentials import CredentialManager
from pyshape.api.rest_api import RestApi
from pyshape.document import Document
from pyshape.util.exceptions import PyshapeParameterError

from loguru import logger


class Client:
    """Handles project management, authentication, and other related items"""

    def __init__(self) -> None:

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

        if id is None and name is None:
            raise PyshapeParameterError(
                "A name or id must be provided to fetch a document"
            )

        document_models = self._api.endpoints.documents()
        model_candidate = None

        if name:
            name_matches = [model.name == name for model in document_models].count(True)
            if name_matches > 1:
                raise PyshapeParameterError(
                    f"Multiple documents with name {name}. Use document id instead"
                )

        for model in document_models:
            if id and model.id == id:
                model_candidate = model
                break

            if name and model.name == name:
                model_candidate = model
                break

        if model_candidate is None:
            raise PyshapeParameterError(
                "Unable to find a document with "
                + (f"name {name}" if name else f"id {id}")
            )

        return Document(self, model_candidate)

    def create_document(self, name: str, description: str | None = None) -> Document:
        """Creates a new document

        Args:
            name: The name of the new document
            description: The description of document

        Returns:
            A Document object of the new document
        """

        return Document(self, self._api.endpoints.document_create(name, description))
