"""Abstract base class for features.

Features are the operations taken to create some geometry; they are
fundamental to the idea of parametric cad. The base class for OnShape Features
is defined here.

OnPy - May 2024 - Kyle Tennison

"""

from abc import ABC, abstractmethod
from textwrap import dedent
from typing import TYPE_CHECKING, cast

from loguru import logger

from onpy.api import schema
from onpy.api.versioning import WorkspaceWVM
from onpy.part import Part
from onpy.util.exceptions import OnPyFeatureError, OnPyParameterError
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.api.rest_api import RestApi
    from onpy.client import Client
    from onpy.document import Document
    from onpy.elements.partstudio import PartStudio
    from onpy.entities import EntityFilter
    from onpy.features.planes import Plane


class Feature(ABC):
    """An abstract base class for OnShape elements."""

    @property
    @abstractmethod
    def partstudio(self) -> "PartStudio":
        """A reference to the owning PartStudio."""

    @property
    def document(self) -> "Document":
        """A reference to the owning document."""
        return self.partstudio.document

    @property
    def _client(self) -> "Client":
        """A reference to the underlying client."""
        return self.document._client

    @property
    def _api(self) -> "RestApi":
        """A reference to the api."""
        return self._client._api

    @property
    @abstractmethod
    def id(self) -> str | None:
        """The id of the feature."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the feature."""
        ...

    @property
    @abstractmethod
    def entities(self) -> "EntityFilter":
        """An object used for interfacing with entities that belong to the object."""
        ...

    @abstractmethod
    def _to_model(self) -> schema.Feature:
        """Convert the feature into the corresponding api schema."""
        ...

    @abstractmethod
    def _load_response(self, response: schema.FeatureAddResponse) -> None:
        """Load the feature add response to the feature metadata."""
        ...

    def _upload_feature(self) -> None:
        """Add a feature to the partstudio.

        Raises:
            OnPyFeatureError if the feature fails to load

        """
        response = self._api.endpoints.add_feature(
            document_id=self.document.id,
            version=WorkspaceWVM(self.document.default_workspace.id),
            element_id=self.partstudio.id,
            feature=self._to_model(),
        )

        self.partstudio._features.append(self)

        if response.featureState.featureStatus != "OK":
            if response.featureState.featureStatus == "WARNING":
                logger.warning("Feature loaded with warning")
            else:
                msg = "Feature errored on upload"
                raise OnPyFeatureError(msg)
        else:
            logger.debug(f"Successfully uploaded feature '{self.name}'")

        self._load_response(response)

    def _update_feature(self) -> None:
        """Update the feature in the cloud."""
        response = self._api.endpoints.update_feature(
            document_id=self.document.id,
            workspace_id=self.document.default_workspace.id,
            element_id=self.partstudio.id,
            feature=self._to_model(),
        )

        if response.featureState.featureStatus != "OK":
            if response.featureState.featureStatus == "WARNING":
                logger.warning("Feature loaded with warning")
            else:
                msg = "Feature errored on update"
                raise OnPyFeatureError(msg)
        else:
            logger.debug(f"Successfully updated feature '{self.name}'")

    def _get_created_parts_inner(self) -> list[Part]:
        """Get the parts created by the current feature. Wrap this
        function in `get_created_parts` to expose it to the user, ONLY if
        it is applicable to the feature.

        Returns:
            A list of Part objects

        """
        script = dedent(
            f"""
            function(context is Context, queries) {{
                var query = qCreatedBy(makeId("{self.id}"), EntityType.BODY);

                return transientQueriesToStrings( evaluateQuery(context, query) );
            }}
            """,
        )

        response = self._client._api.endpoints.eval_featurescript(
            document_id=self.partstudio.document.id,
            version=WorkspaceWVM(self.partstudio.document.default_workspace.id),
            element_id=self.partstudio.id,
            script=script,
            return_type=schema.FeaturescriptResponse,
        )

        part_ids_raw = unwrap(
            response.result,
            message="Featurescript failed get parts created by feature",
        )["value"]

        part_ids = [i["value"] for i in part_ids_raw]

        available_parts = self._api.endpoints.list_parts(
            document_id=self.partstudio.document.id,
            version=WorkspaceWVM(self.partstudio.document.default_workspace.id),
            element_id=self.partstudio.id,
        )

        return [Part(self.partstudio, part) for part in available_parts if part.partId in part_ids]


class FeatureList:
    """Wrapper around a list of features."""

    def __init__(self, features: list[Feature]) -> None:
        """Construct a FeatureList wrapper from a list[Features] object."""
        self._features = features

    def __len__(self) -> int:
        """Get the number of features in the list."""
        return len(self._features)

    def __getitem__(self, name: str) -> Feature:
        """Get an item by its name."""
        matches = [f for f in self._features if f.name == name]

        if len(matches) == 0:
            msg = f"No feature named '{name}'"
            raise OnPyParameterError(msg)
        if len(matches) > 1:
            msg = f"Multiple '{name}' features. Use .get(id=...)"
            raise OnPyParameterError(msg)
        return matches[0]

    def __str__(self) -> str:
        """Pretty string representation of the feature list."""
        msg = "FeatureList(\n"
        for f in self._features:
            msg += f"  {f}\n"
        msg += ")"
        return msg

    @property
    def front_plane(self) -> "Plane":
        """A reference to the front default plane."""
        return cast("Plane", self["Front Plane"])

    @property
    def top_plane(self) -> "Plane":
        """A reference to the top default plane."""
        return cast("Plane", self["Top Plane"])

    @property
    def right_plane(self) -> "Plane":
        """A reference to the right default plane."""
        return cast("Plane", self["Right Plane"])
