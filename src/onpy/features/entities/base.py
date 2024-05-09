"""Abstract base class for feature entities"""

from abc import ABC, abstractmethod
import copy
import math
import uuid

import numpy as np
import onpy.api.model as model
from typing import Self, TYPE_CHECKING
from onpy.util.misc import Point2D

if TYPE_CHECKING:
    from onpy.features.base import Feature


class Entity(ABC):

    @abstractmethod
    def to_model(self) -> model.FeatureEntity:
        """Convert the entity into the corresponding model"""
        ...

    @property
    @abstractmethod
    def _feature(self) -> "Feature":
        """A reference to the"""
        ...
