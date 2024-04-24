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


def unwrap_type[T](object: object, expected_type: type[T]) -> T:
    """Returns the object if the type matches. Raises error otherwise."""

    if isinstance(object, expected_type):
        return object
    else:
        raise TypeError("Failed to unwrap type. Got %s, expected %s" % (type(object).__name__, expected_type.__name__))
    
def unwrap[T](object: T|None, default: T|None=None) -> T:
    """Takes the object out of an Option[T]. Returns default value if the
    object is None; will raise TypeError if default is unbound.""" 

    if object is not None:
        return object
    else:
        if default is not None:
            return default 
        else:
            raise TypeError("Failed to unwrap")