"""Datamodel used across the project"""

from enum import Enum


class HttpMethod(Enum):
    Post = "post"
    Get = "get"
    Put = "put"
    Delete = "delete"
