"""Assembly element interface"""

from onpy.elements.base import Element
import onpy.api.model as model

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from onpy.client import Client
    from onpy.document import Document


class Assembly(Element):

    def __init__(self, document: "Document", model: model.Element) -> None:
        self._model = model
        self._document = document

    @property
    @override
    def document(self) -> "Document":
        return self._document

    @property
    @override
    def id(self) -> str:
        """The element id of the Assembly"""
        return self._model.id

    @property
    @override
    def name(self) -> str:
        """The name of the Assembly"""
        return self._model.name

    def __repr__(self) -> str:
        return super().__repr__()
