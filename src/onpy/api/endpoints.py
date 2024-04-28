"""Contains different endpoints exposed to the RestApi object"""

import onpy.api.model as model
from onpy.api.versioning import VersionTarget

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from onpy.api.rest_api import RestApi


class EndpointContainer:

    def __init__(self, rest_api: "RestApi") -> None:
        self.api = rest_api

    def documents(self) -> list[model.Document]:
        """Fetches a list of documents that belong to the current user"""

        r = self.api.get(endpoint="/documents", response_type=model.DocumentsResponse)
        return r.items

    def document_create(self, name: str, description: str | None) -> model.Document:
        """Creates a new document"""

        if description is None:
            description = "Created with onpy"

        return self.api.post(
            endpoint="/documents",
            payload=model.DocumentCreateRequest(name=name, description=description),
            response_type=model.Document,
        )

    def document_delete(self, document_id: str) -> None:
        """Deletes a document"""

        self.api.delete(endpoint=f"/documents/{document_id}", response_type=str)

    def document_elements(
        self, document_id: str, version: VersionTarget
    ) -> list[model.Element]:
        """Fetches all of the elements in the specified document"""

        return self.api.list_get(
            endpoint=f"/documents/d/{document_id}/{version.wvm}/{version.wvmid}/elements",
            response_type=model.Element,
        )

    def eval_featurescript[
        T: str | model.ApiModel
    ](
        self,
        document_id: str,
        version: VersionTarget,
        element_id: str,
        script: str,
        return_type: type[T] = str,
    ) -> T:
        """Evaluates a snipit of featurescript"""

        return self.api.post(
            endpoint=f"/partstudios/d/{document_id}/{version.wvm}/{version.wvmid}/e/{element_id}/featurescript",
            response_type=return_type,
            payload=model.FeaturescriptUpload(script=script),
        )

    def list_features(
        self, document_id: str, version: VersionTarget, element_id: str
    ) -> list[model.Feature]:
        """Lists all the features in a partstudio"""

        feature_list = self.api.get(
            endpoint=f"/partstudios/d/{document_id}/{version.wvm}/{version.wvmid}/e/{element_id}/features",
            response_type=model.FeatureListResponse,
        )

        return feature_list.features

    def add_feature(
        self,
        document_id: str,
        version: VersionTarget,
        element_id: str,
        feature: model.Feature,
    ) -> model.FeatureAddResponse:
        """Adds a feature to the partstudio"""

        return self.api.post(
            endpoint=f"/partstudios/d/{document_id}/{version.wvm}/{version.wvmid}/e/{element_id}/features",
            response_type=model.FeatureAddResponse,
            payload=model.FeatureAddRequest(
                feature=feature.model_dump(exclude_none=True)
            ),
        )
    

    def update_feature(
            self,
            document_id: str ,
            workspace_id: str,
            element_id: str,
            feature: model.Feature,
    ) -> model.FeatureAddResponse:
        """Updates an existing feature"""

        return self.api.post(
            endpoint=f"/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/features/featureid/{feature.featureId}",
            response_type=model.FeatureAddResponse,
            payload=model.FeatureAddRequest(
                feature=feature.model_dump(exclude_none=True)
            )
        )
    
    def delete_feature(
        self, document_id: str, workspace_id, element_id: str, feature_id: str
    ) -> None:
        """Deletes a feature"""

        self.api.delete(
            endpoint=f"/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/features/featureid/{feature_id}",
            response_type=str,
        )

    def list_versions(self, document_id: str) -> list[model.DocumentVersion]:
        """Lists the versions in a document in reverse-chronological order"""

        versions = self.api.list_get(
            endpoint=f"/documents/d/{document_id}/versions",
            response_type=model.DocumentVersion,
        )

        return sorted(versions, key=lambda v: v.createdAt, reverse=True)

    def create_version(
        self, document_id: str, workspace_id: str, name: str
    ) -> model.DocumentVersion:
        """Creates a new version from a workspace"""

        return self.api.post(
            f"/documents/d/{document_id}/versions",
            response_type=model.DocumentVersion,
            payload=model.DocumentVersionUpload(
                documentId=document_id, name=name, workspaceId=workspace_id
            ),
        )

