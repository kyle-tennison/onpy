"""Partstudio element interface.

In OnShape, partstudios are the place where parts are modeled. This is
partstudios are fundamental to how OnPy operates; besides documents,
they are effectively the entry point to creating a schema. All features
are created by a partstudio, and they all live in the partstudio.

OnPy - May 2024 - Kyle Tennison

"""

from typing import TYPE_CHECKING, override

from onpy.api import schema
from onpy.api.versioning import WorkspaceWVM
from onpy.elements.base import Element
from onpy.entities.protocols import BodyEntityConvertible, FaceEntityConvertible
from onpy.features import Extrude, Loft, OffsetPlane, Plane, Sketch
from onpy.features.base import Feature, FeatureList
from onpy.features.planes import DefaultPlane, DefaultPlaneOrientation
from onpy.part import Part, PartList
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.document import Document


class PartStudio(Element):
    """Represents a part studio."""

    def __init__(
        self,
        document: "Document",
        model: schema.Element,
    ) -> None:
        """Construct a new PartStudio object from a partstudio schema.

        Args:
            document: The document that owns the partstudio.
            model: The schema of the partstudio.

        """
        self._model = model
        self._document = document
        self._features: list[Feature] = []

        self._features.extend(self._get_default_planes())

    @property
    @override
    def document(self) -> "Document":
        return self._document

    @property
    @override
    def id(self) -> str:
        """The element id of the PartStudio."""
        return self._model.id

    @property
    @override
    def name(self) -> str:
        """The name of the PartStudio."""
        return self._model.name

    @property
    def features(self) -> FeatureList:
        """A list of the partstudio's features."""
        return FeatureList(self._features)

    def _get_default_planes(self) -> list[DefaultPlane]:
        """Get the default planes from the PartStudio."""
        return [DefaultPlane(self, orientation) for orientation in DefaultPlaneOrientation]

    def add_sketch(
        self,
        plane: Plane | FaceEntityConvertible,
        name: str = "New Sketch",
    ) -> Sketch:
        """Add a new sketch to the partstudio.

        Args:
            plane: The plane to base the sketch off of
            name: An optional name for the sketch

        Returns:
            A Sketch object

        """
        return Sketch(partstudio=self, plane=plane, name=name)

    def add_extrude(
        self,
        faces: FaceEntityConvertible,
        distance: float,
        name: str = "New Extrude",
        merge_with: BodyEntityConvertible | None = None,
        subtract_from: BodyEntityConvertible | None = None,
    ) -> Extrude:
        """Add a new blind extrude feature to the partstudio.

        Args:
            faces: The faces to extrude
            distance: The distance to extrude
            name: An optional name for the extrusion
            merge_with: An optional body to merge with
            subtract_from: An optional body to subtract the extruded volume from.
                This will make the extrusion into a subtraction.

        Returns:
            An Extrude object

        """
        return Extrude(
            partstudio=self,
            faces=faces,
            distance=distance,
            name=name,
            merge_with=merge_with,
            subtract_from=subtract_from,
        )

    def add_loft(
        self,
        start: FaceEntityConvertible,
        end: FaceEntityConvertible,
        name: str = "Loft",
    ) -> Loft:
        """Add a new loft feature to the partstudio.

        Args:
            start: The start face(s) of the loft
            end: The end face(s) of the loft
            name: An optional name for the loft feature

        Returns:
            A Loft object

        """
        return Loft(partstudio=self, start_face=start, end_face=end, name=name)

    def add_offset_plane(
        self,
        target: Plane | FaceEntityConvertible,
        distance: float,
        name: str = "Offset Plane",
    ) -> OffsetPlane:
        """Add a new offset plane to the partstudio.

        Args:
            target: The plane to offset from
            distance: The distance to offset
            name: An optional name for the plane

        Returns:
            An OffsetPlane object

        """
        return OffsetPlane(partstudio=self, owner=target, distance=distance, name=name)

    def list_parts(self) -> list[Part]:
        """Get a list of parts attached to the partstudio."""
        parts = self._api.endpoints.list_parts(
            document_id=self.document.id,
            version=WorkspaceWVM(self.document.default_workspace.id),
            element_id=self.id,
        )

        return [Part(self, pmodel) for pmodel in parts]

    @property
    def parts(self) -> PartList:
        """A PartList object used to list available parts."""
        return PartList(self.list_parts())

    def wipe(self) -> None:
        """Remove all features from the current partstudio. Stores in another version."""
        self.document.create_version()

        features = self._api.endpoints.list_features(
            document_id=self._document.id,
            version=WorkspaceWVM(self._document.default_workspace.id),
            element_id=self.id,
        )

        features.reverse()

        for feature in features:
            self._api.endpoints.delete_feature(
                document_id=self._document.id,
                workspace_id=self._document.default_workspace.id,
                element_id=self.id,
                feature_id=unwrap(feature.featureId),
            )

    def __repr__(self) -> str:
        """Printable representation of the partstudio."""
        return super().__repr__()
