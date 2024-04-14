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

        r = self.api.get(
            endpoint="/documents", 
            expected_response=model.DocumentsResponse
            )
        return r.items
    
    def document_create(self, name: str, description: str|None) -> model.Document:
        """Creates a new document"""

        if description is None:
            description = "Created with pyshape"

        return self.api.post(
            endpoint="/documents",
            payload=model.DocumentCreateRequest(
                name=name,
                description=description
            ),
            expected_response=model.Document
        )

