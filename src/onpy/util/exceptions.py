"""Exception definitions and excepthook injection"""

import json
from typing import override
from requests import Response
from abc import ABC, abstractmethod
import sys
from loguru import logger


class PyshapeException(Exception, ABC):

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    @abstractmethod
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        ...


class PyshapeAuthError(PyshapeException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nPyshapeAuthError({self.message})"


class PyshapeApiError(PyshapeException):

    def __init__(self, message: str, response: Response | None = None) -> None:
        self.response = response
        super().__init__(message)

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""

        response_pretty = ""
        url = "None"

        if self.response is not None:
            url = self.response.url
            try:
                response_pretty = json.dumps(self.response.json(), indent=4)
            except json.JSONDecodeError:
                response_pretty = self.response.text
        else:
            response_pretty = "Undefined"

        return (
            f"\nPyshapeApiError: (\n"
            f"  message: {self.message}\n"
            f"  url: {url}\n"
            f"  response: {response_pretty}\n"
            f")"
        )


class PyshapeInternalError(PyshapeException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nPyshapeInternalError({self.message})"


class PyshapeParameterError(PyshapeException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nPyshapeParameterError({self.message})"


class PyshapeFeatureError(PyshapeException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nPyshapeFeatureError({self.message})"


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, PyshapeException):
        logger.trace(str(exc_traceback))
        logger.error(exc_value.display())
        sys.exit(1)

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception
