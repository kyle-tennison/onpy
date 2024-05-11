import sys
from loguru import logger
from onpy.document import Document
from onpy.client import Client

# --- configure loguru ---
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<level>{level: <8}</level> | <level>{message}</level>",
)

# --- some quality of life functions ---


def get_document(id: str | None = None, name: str | None = None) -> Document:
    """Gets a document by name or id. Instantiates a new client.

    Args:
        id: The id of the document to fetch
        name: The name of the document to fetch

    Returns:
        A list of Document objects
    """
    return Client().get_document(id, name)


def create_document(name: str, description: str | None = None) -> Document:
    """Creates a new document. Instantiates a new client.

    Args:
        name: The name of the new document
        description: The description of document

    Returns:
        A Document object of the new document
    """
    return Client().create_document(name, description)
