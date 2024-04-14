"""Exception Definitions"""

from requests import Response

class PyshapeException(Exception): ...

class OnshapeAuthError(PyshapeException): ...

class PyshapeApiError(PyshapeException): 

    def __init__(self, message: str, response: Response|None) -> None:
        self.response = response
        super().__init__(message)

class PyshapeInternalError(PyshapeException): ...