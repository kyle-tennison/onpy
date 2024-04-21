"""Assembly element interface"""

from pyshape.elements.base import Element
import pyshape.api.model as model

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyshape.client import Client
    from pyshape.document import Document


class Assembly(Element):

    def __init__(
        self, client: "Client", model: model.Element, document: "Document"
    ) -> None:
        super().__init__(client, model, document)
        self._model = model

    @property
    def id(self) -> str:
        """The element id of the Assembly"""
        return self._model.id

    @property
    def name(self) -> str:
        """The name of the Assembly"""
        return self._model.name
    
    def __repr__(self) -> str:
        return super().__repr__()
