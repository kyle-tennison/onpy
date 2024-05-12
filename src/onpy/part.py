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
    
    @property
    def _transient_id(self) -> str:
        """The transient id of the part"""

        updated_query = self._model.partQuery.replace("id", "newId()")

        logger.critical(f"Using updated query: {updated_query}")

        script = dedent(f"""
            function(context is Context, queries) {{
                var query = {updated_query}                    
                return transientQueriesToStrings( evaluateQuery(context, query) ); 
            }}
            """)
        
        response = self._client._api.endpoints.eval_featurescript(
            document_id=self._partstudio.document.id,
            version=WorkspaceWVM(self._partstudio.document.default_workspace.id),
            element_id=self._partstudio.id,
            script=script,
            return_type=model.FeaturescriptResponse,
        )

        transient_id = unwrap(
            response.result, message="Featurescript failed to load part as transient ID"
        )["value"]
        return transient_id

    def __repr__(self) -> str:
        return f"Part({self.id})"
    
    def __str__(self) -> str:
        return repr(self)
        
