"""

Part interface

In OnShape, Parts are 3D bodies that belong to a partstudio. The OnPy part
interface is defined here

OnPy - May 2024 - Kyle Tennison

"""

from textwrap import dedent
from typing import TYPE_CHECKING

from loguru import logger

import onpy.api.model as model
from onpy.api.versioning import WorkspaceWVM
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.elements.partstudio import PartStudio


class Part:
    """Represents a Part in an OnShape partstudio"""

    def __init__(self, partstudio: "PartStudio", model: model.Part) -> None:
        self._partstudio = partstudio
        self._model = model 
        self._api = self._partstudio._api
        self._client = self._partstudio._client


    @property
    def id(self) -> str:
        """The part id"""
        return self._model.partId
    
    @property
    def name(self) -> str:
        """The name of the part"""
        return self._model.name

    def __repr__(self) -> str:
        return f"Part({self.id})"
    
    def __str__(self) -> str:
        return repr(self)
        
