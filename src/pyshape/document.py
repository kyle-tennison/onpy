"""Document implementation"""

import pyshape.api.model as model

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyshape.client import Client

class Document:

    def __init__(self, client: "Client", model: model.Document) -> None:
        self._model = model 
        self._client = client
        