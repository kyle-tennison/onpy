"""OnPy, an unofficial OnShape API for Python."""

import sys

from loguru import logger

from onpy.client import Client
from onpy.document import Document
from onpy.util.credentials import CredentialManager

# --- configure loguru ---
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<level>{level: <8}</level> | <level>{message}</level>",
)

# --- some quality of life functions ---


def get_document(document_id: str | None = None, name: str | None = None) -> Document:
    """Get a document by name or id. Instantiates a new client.

    Args:
        document_id: The id of the document to fetch
        name: The name of the document to fetch

    Returns:
        A list of Document objects

    """
    return Client().get_document(document_id, name)


def create_document(name: str, description: str | None = None) -> Document:
    """Create a new document. Instantiates a new client.

    Args:
        name: The name of the new document
        description: The description of document

    Returns:
        A Document object of the new document

    """
    return Client().create_document(name, description)


def configure() -> None:
    """CLI interface to update OnShape credentials."""
    tokens = CredentialManager.prompt_tokens()
    CredentialManager.configure_file(*tokens)
