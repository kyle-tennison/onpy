"""Abstract base class for feature entities"""

from abc import ABC, abstractmethod
import uuid
import onpy.api.model as model


class Entity(ABC):

    @abstractmethod
    def to_model(self) -> model.FeatureEntity:
        """Convert the entity into the corresponding model"""
        ...

    def generate_entity_id(self) -> str:
        """Generates a random entity id"""
        return str(uuid.uuid4()).replace("-", "")

    def __str__(self) -> str:
        return repr(self)

    @abstractmethod
    def __repr__(self) -> str: ...
