"""Abstract base class for feature entities"""

from abc import ABC, abstractmethod
import pyshape.api.model as model


class Entity(ABC):

    @abstractmethod
    def to_model(self) -> model.FeatureEntity:
        """Convert the entity into the corresponding model"""
        ...
