"""

Custom Exceptions 

OnPy features some custom exceptions, which are defined here. Their implementation
is aimed at being maximally readable and descriptive.

OnPy - May 2024 - Kyle Tennison

"""

import sys
import json
from loguru import logger
from typing import override
from requests import Response
from abc import ABC, abstractmethod


class OnPyException(Exception, ABC):

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    @abstractmethod
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        ...


class OnPyAuthError(OnPyException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nOnPyAuthError({self.message})"


class OnPyApiError(OnPyException):

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
            f"\nOnPyApiError: (\n"
            f"  message: {self.message}\n"
            f"  url: {url}\n"
            f"  response: {response_pretty}\n"
            f")"
        )


class OnPyInternalError(OnPyException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nOnPyInternalError({self.message})"


class OnPyParameterError(OnPyException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nOnPyParameterError({self.message})"


class OnPyFeatureError(OnPyException):

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string"""
        return f"\nOnPyFeatureError({self.message})"


def is_interactive() -> bool:
    """Check if the script is being run in an interactive Python shell."""
    return hasattr(sys, "ps1")


def maybe_exit(exit_code: int) -> None:
    """Exit the program if running from a Python file. Will not exit if running
    in an interactive shell.

    Args:
        exit_code: Bash exit code

    """
    if not is_interactive():
        sys.exit(exit_code)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Custom excepthook."""
    if issubclass(exc_type, OnPyException):
        logger.trace(str(exc_traceback))
        logger.error(exc_value.display())
        maybe_exit(1)
        return

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception
