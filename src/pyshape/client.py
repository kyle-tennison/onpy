"""Entry point to this library"""

from pyshape.util.credentials import CredentialManager
from pyshape.api.rest_api import RestApi

from loguru import logger


class Client:
    """Handles project management, authentication, and other related items"""

    def __init__(self) -> None:

        self._credentials = CredentialManager.fetch_or_prompt()
        self._api = RestApi(self)

    def list_documents(self):
        """DEBUG TOOL"""

        documents = self._api.endpoints.documents()

        for doc in documents:
            logger.info(doc.name)
