"""Models for OnShape API payloads & responses.

The API uses pydantic to serialize and deserialize API calls. The models
to do this are stored here.

OnPy - May 2024 - Kyle Tennison

"""

from abc import abstractmethod
from datetime import datetime
from enum import Enum
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class HttpMethod(Enum):
    """Enumeration of available HTTP methods."""

    Post = "post"
    Get = "get"
    Put = "put"
    Delete = "delete"


class NameIdFetchable(Protocol):
    """A protocol for an object that can be fetched by name or id."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the item."""
        ...

    @property
    @abstractmethod
    def id(self) -> str:
        """The ID of the item."""
        ...


class ApiModel(BaseModel):
    """Base model for OnShape APIs."""

    model_config = ConfigDict(extra="ignore")


class UserReference(ApiModel):
    """Represents a reference to a user."""

    href: str
    id: str
    name: str


class Workspace(ApiModel):
    """Represents an instance of OnShape's workspace versioning."""

    name: str
    id: str


class Document(ApiModel):
    """Represents surface-level document information."""

    createdAt: datetime
    createdBy: UserReference
    href: str
    id: str
    name: str
    owner: UserReference
    defaultWorkspace: Workspace


class DocumentsResponse(ApiModel):
    """Response model of GET /documents."""

    items: list[Document]


class DocumentCreateRequest(ApiModel):
    """Request model of POST /documents."""

    name: str
    description: str | None
    isPublic: bool | None = True


class DocumentVersion(ApiModel):
    """Represents a document version."""

    documentId: str
    name: str
    id: str
    microversion: str
    createdAt: datetime
    description: str | None = ""


class DocumentVersionUpload(ApiModel):
    """Represents a partial document version, used for upload."""

    documentId: str
    name: str
    workspaceId: str


class Element(ApiModel):
    """Represents an OnShape element."""

    angleUnits: str | None
    areaUnits: str | None
    lengthUnits: str | None
    massUnits: str | None
    volumeUnits: str | None
    elementType: str
    id: str
    name: str


class FeatureParameter(ApiModel):
    """Represents a feature parameter."""

    btType: str
    queries: list[dict | ApiModel]
    parameterId: str


class FeatureParameterQueryList(FeatureParameter):
    """Represents a BTMParameterQueryList-148."""

    btType: str = "BTMParameterQueryList-148"


class FeatureEntity(ApiModel):
    """Represents a feature entity."""

    btType: str | None = None
    entityId: str


class SketchCurveEntity(FeatureEntity):
    """Represents a sketch's curve."""

    geometry: dict
    centerId: str
    btType: str | None = "BTMSketchCurve-4"


class SketchCurveSegmentEntity(FeatureEntity):
    """Represents a sketch curve segment."""

    btType: str | None = "BTMSketchCurveSegment-155"
    startPointId: str
    endPointId: str
    startParam: float
    endParam: float
    geometry: dict
    centerId: str | None = None


class Feature(ApiModel):
    """Represents an OnShape feature."""

    name: str
    namespace: str | None = None
    featureType: str
    suppressed: bool
    parameters: list[dict] | None = []  # dict is FeatureParameter

    # TODO @kyle-tennison: use the actual models again
    featureId: str | None = None

    # TODO @kyle-tennison: is there any way to use inheritance in
    # pydantic w/o filtering off attributes


class FeatureState(ApiModel):
    """Contains information about the health of a feature."""

    featureStatus: str
    inactive: bool


class FeatureAddRequest(ApiModel):
    """API Request to add a feature."""

    feature: dict


class FeatureAddResponse(ApiModel):
    """API Response after adding a feature."""

    feature: Feature
    featureState: FeatureState


class FeatureListResponse(ApiModel):
    """API Response of GET /partstudios/DWE/features."""

    features: list[Feature]
    defaultFeatures: list[Feature]


class FeaturescriptUpload(ApiModel):
    """Request model of POST /partstudios/DWE/featurescript."""

    script: str


class FeaturescriptResponse(ApiModel):
    """The response from a featurescript upload."""

    result: dict | None


class Sketch(Feature):
    """Represents a Sketch Feature."""

    btType: str = "BTMSketch-151"
    featureType: str = "newSketch"
    constraints: list[dict] | None = []
    entities: list[dict] | None  # dict is FeatureEntity


class Extrude(Feature):
    """Represents an Extrude Feature."""

    btType: str = "BTMFeature-134"
    featureType: str = "extrude"


class Plane(Feature):
    """Represents a Plane Feature."""

    btType: str = "BTMFeature-134"
    featureType: str = "cPlane"


class Loft(Feature):
    """Represents a Loft Feature."""

    btType: str = "BTMFeature-134"
    featureType: str = "loft"


class Part(ApiModel):
    """Represents a Part."""

    name: str
    partId: str
    bodyType: str
    partQuery: str
