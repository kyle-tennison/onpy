"""Models for OnShape API payloads & responses"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Protocol


class NameIdFetchable(Protocol):
    name: str | None
    id: str | None


class ApiModel(BaseModel):

    model_config = ConfigDict(extra="ignore")


class UserReference(ApiModel):
    """Represents a reference to a user"""

    href: str
    id: str
    name: str


class Workspace(ApiModel):
    """Represents an instance of OnShape's workspace versioning"""

    name: str
    id: str


class Document(ApiModel):
    """Represents surface-level document information"""

    createdAt: datetime
    createdBy: UserReference
    href: str
    id: str
    name: str
    owner: UserReference
    defaultWorkspace: Workspace


class DocumentsResponse(ApiModel):
    """Response model of GET /documents"""

    items: list[Document]


class DocumentCreateRequest(ApiModel):
    """Request model of POST /documents"""

    name: str
    description: str | None
    isPublic: Optional[bool] = True


class Element(ApiModel):
    """Represents an OnShape element"""

    angleUnits: str | None
    areaUnits: str | None
    lengthUnits: str | None
    massUnits: str | None
    volumeUnits: str | None
    elementType: str
    id: str
    name: str


class FeatureParameter(ApiModel):
    """Represents a feature parameter"""

    btType: str
    queries: list[dict | ApiModel]
    parameterId: str


class FeatureParameterQueryList(FeatureParameter):
    """Represents a BTMParameterQueryList-148"""

    btType: str = "BTMParameterQueryList-148"


class FeatureEntity(ApiModel):
    """Represents a feature entity"""

    btType: Optional[str] = None
    entityId: str


class SketchCurveEntity(FeatureEntity):
    """Represents a sketch's curve"""

    geometry: dict
    centerId: str
    btType: str = "BTMSketchCurve-4"


class SketchCurveSegmentEntity(FeatureEntity):
    """Represents a sketch curve segment"""

    btType: str = "BTMSketchCurveSegment-155"
    startPointId: str
    endPointId: str
    startParam: float
    endParam: float
    geometry: dict


class Feature(ApiModel):
    """Represents an OnShape feature"""

    name: str
    namespace: Optional[str] = None
    # nodeId: str
    featureType: str
    suppressed: bool
    parameters: Optional[list[dict]] = (
        []
    )  # dict is FeatureParameter TODO: use the actual models again
    featureId: Optional[str] = None

    # TODO: is there any way to use inheritance in pydantic w/o filtering off attributes


class FeatureState(ApiModel):
    """Contains information about the health of a feature"""

    featureStatus: str
    inactive: bool


class FeatureAddRequest(ApiModel):
    """API Request to add a feature"""

    feature: dict


class FeatureAddResponse(ApiModel):
    """API Response after adding a feature"""

    feature: Feature
    featureState: FeatureState


class FeaturescriptUpload(ApiModel):
    """Request model of POST /partstudio/DWE/featurescript"""

    script: str


class FeaturescriptResponse(ApiModel):
    result: dict


class Sketch(Feature):
    """Represents a Sketch Feature"""

    btType: str = "BTMSketch-151"
    featureType: str = "newSketch"
    constraints: Optional[list[dict]] = []
    entities: Optional[list[dict]]  # dict is FeatureEntity


class Extrude(Feature):
    """Represents an Extrude Feature"""

    btType: str = "BTMFeature-134"
    featureType: str = "extrude"
