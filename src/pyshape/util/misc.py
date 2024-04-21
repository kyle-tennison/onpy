"""Miscellaneous tools"""

from pyshape.api.model import NameIdFetchable
from pyshape.util.exceptions import PyshapeParameterError


def find_by_name_or_id[
    T: NameIdFetchable
](id: str | None, name: str | None, items: list[T]) -> T | None:
    """Given a list of values and a name & id, find the first match. Only the
    name or id needs to be provided.

    Args:
        id: The id to search for
        name: The name to search for
        items: A list of items to search through

    Returns:
        The matching item, if found. Returns None if no match is found.

    Raises:
        PyshapeParameterError if neither the id nor name were provided.
    """

    if name is None and id is None:
        raise PyshapeParameterError("A name or id is required to fetch")
    
    if len(items) == 0:
        return None

    candidate: T | None = None

    if name:
        filtered = [i for i in items if i.name == name]
        if len(filtered) > 1:
            raise PyshapeParameterError(
                f"Duplicate names '{name}'. Use id instead to fetch."
            )
        if len(filtered) == 0:
            return None

        candidate = filtered[0]

    if id:
        for i in items:
            if i.id == id:
                candidate = i
                break

    return candidate


# if id is None and name is None:
#     raise PyshapeParameterError(
#         "A name or id must be provided to fetch a document"
#     )

# document_models = self._api.endpoints.documents()
# model_candidate = None

# if name:
#     name_matches = [model.name == name for model in document_models].count(True)
#     if name_matches > 1:
#         raise PyshapeParameterError(
#             f"Multiple documents with name {name}. Use document id instead"
#         )

# for model in document_models:
#     if id and model.id == id:
#         model_candidate = model
#         break

#     if name and model.name == name:
#         model_candidate = model
#         break

# if model_candidate is None:
#     raise PyshapeParameterError(
#         "Unable to find a document with "
#         + (f"name {name}" if name else f"id {id}")
#     )

# return Document(self, model_candidate)
