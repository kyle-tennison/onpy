"""Different endpoints exposed to the RestApi object.

The api is built in two parts; a request centric, utility part, and a part
dedicated to wrapping the many OnShape endpoints. This script completes the
ladder; it uses the utilities from rest_api.py to wrap OnShape endpoints
in Python.

OnPy - May 2024 - Kyle Tennison

"""

from typing import TYPE_CHECKING

from onpy.api import schema
from onpy.api.versioning import VersionTarget

if TYPE_CHECKING:
    from onpy.api.rest_api import RestApi


class EndpointContainer:
    """Container for different OnShape endpoints and their schemas."""

    def __init__(self, rest_api: "RestApi") -> None:
        """Construct a container instance from a rest api instance."""
        self.api = rest_api

    def documents(self) -> list[schema.Document]:
        """Fetch a list of documents that belong to the current user."""
        r = self.api.get(endpoint="/documents", response_type=schema.DocumentsResponse)
        return r.items

    def document_create(self, name: str, description: str | None) -> schema.Document:
        """Create a new document."""
        if description is None:
            description = "Created with onpy"

        return self.api.post(
            endpoint="/documents",
            payload=schema.DocumentCreateRequest(name=name, description=description),
            response_type=schema.Document,
        )

    def document_delete(self, document_id: str) -> None:
        """Delete a document."""
        self.api.delete(endpoint=f"/documents/{document_id}", response_type=str)

    def document_elements(
        self,
        document_id: str,
        version: VersionTarget,
    ) -> list[schema.Element]:
        """Fetch all of the elements in the specified document."""
        return self.api.list_get(
            endpoint=f"/documents/d/{document_id}/{version.wvm}/{version.wvmid}/elements",
            response_type=schema.Element,
        )

    def eval_featurescript[T: str | schema.ApiModel](
        self,
        document_id: str,
        version: VersionTarget,
        element_id: str,
        script: str,
        return_type: type[T] = str,
    ) -> T:
        """Evaluate a snipit of featurescript."""
        return self.api.post(
            endpoint=f"/partstudios/d/{document_id}/{version.wvm}/{version.wvmid}/e/{element_id}/featurescript",
            response_type=return_type,
            payload=schema.FeaturescriptUpload(script=script),
        )

    def list_features(
        self,
        document_id: str,
        version: VersionTarget,
        element_id: str,
    ) -> list[schema.Feature]:
        """List all the features in a partstudio."""
        feature_list = self.api.get(
            endpoint=f"/partstudios/d/{document_id}/{version.wvm}/{version.wvmid}/e/{element_id}/features",
            response_type=schema.FeatureListResponse,
        )

        return feature_list.features

    def add_feature(
        self,
        document_id: str,
        version: VersionTarget,
        element_id: str,
        feature: schema.Feature,
    ) -> schema.FeatureAddResponse:
        """Add a feature to the partstudio."""
        return self.api.post(
            endpoint=f"/partstudios/d/{document_id}/{version.wvm}/{version.wvmid}/e/{element_id}/features",
            response_type=schema.FeatureAddResponse,
            payload=schema.FeatureAddRequest(
                feature=feature.model_dump(exclude_none=True),
            ),
        )

    def update_feature(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        feature: schema.Feature,
    ) -> schema.FeatureAddResponse:
        """Update an existing feature."""
        return self.api.post(
            endpoint=f"/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/features/featureid/{feature.featureId}",
            response_type=schema.FeatureAddResponse,
            payload=schema.FeatureAddRequest(
                feature=feature.model_dump(exclude_none=True),
            ),
        )

    def delete_feature(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        feature_id: str,
    ) -> None:
        """Delete a feature."""
        self.api.delete(
            endpoint=f"/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/features/featureid/{feature_id}",
            response_type=str,
        )

    def list_versions(self, document_id: str) -> list[schema.DocumentVersion]:
        """List the versions in a document in reverse-chronological order."""
        versions = self.api.list_get(
            endpoint=f"/documents/d/{document_id}/versions",
            response_type=schema.DocumentVersion,
        )

        return sorted(versions, key=lambda v: v.createdAt, reverse=True)

    def create_version(
        self,
        document_id: str,
        workspace_id: str,
        name: str,
    ) -> schema.DocumentVersion:
        """Create a new version from a workspace."""
        return self.api.post(
            f"/documents/d/{document_id}/versions",
            response_type=schema.DocumentVersion,
            payload=schema.DocumentVersionUpload(
                documentId=document_id,
                name=name,
                workspaceId=workspace_id,
            ),
        )

    def list_parts(
        self,
        document_id: str,
        version: VersionTarget,
        element_id: str,
    ) -> list[schema.Part]:
        """List all the parts in an element."""
        return self.api.list_get(
            endpoint=f"/parts/d/{document_id}/{version.wvm}/{version.wvmid}/e/{element_id}",
            response_type=schema.Part,
        )
