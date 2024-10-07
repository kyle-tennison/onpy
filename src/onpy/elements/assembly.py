"""Assembly element interface.

Assemblies combine multiple parts together to create a complete product. As of
now (May 2024), OnPy does not directly interface with assemblies, hence
the lack of code.

OnPy - May 2024 - Kyle Tennison

"""

from typing import TYPE_CHECKING, override

from onpy.api import schema
from onpy.elements.base import Element

if TYPE_CHECKING:
    from onpy.document import Document


class Assembly(Element):
    """Represents an OnShape assembly."""

    def __init__(self, document: "Document", model: schema.Element) -> None:
        """Construct an assembly object from it's schema model.

        Args:
            document: The document that owns the assembly
            model: The schema model of the assembly

        """
        self._model = model
        self._document = document

    @property
    @override
    def document(self) -> "Document":
        return self._document

    @property
    @override
    def id(self) -> str:
        """The element id of the Assembly."""
        return self._model.id

    @property
    @override
    def name(self) -> str:
        """The name of the Assembly."""
        return self._model.name

    def __repr__(self) -> str:
        """Printable representation of the assembly."""
        return super().__repr__()
