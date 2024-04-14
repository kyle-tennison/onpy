"""Contains different endpoints exposed to the RestApi object"""

import pyshape.api.model as model

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyshape.api.rest_api import RestApi

class EndpointContainer: 

    def __init__(self, rest_api: "RestApi") -> None:
        self.api = rest_api

    
    def documents(self) -> list[model.Document]:
        """Fetches a list of documents that belong to the current user"""

        r = self.api.get("/documents", model.DocumentsResponse)
        return r.items