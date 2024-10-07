"""Custom Exceptions.

OnPy features some custom exceptions, which are defined here. Their implementation
is aimed at being maximally readable and descriptive.

OnPy - May 2024 - Kyle Tennison

"""

from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast, override

from loguru import logger

if TYPE_CHECKING:
    from types import TracebackType

    from requests import Response


class OnPyError(Exception, ABC):
    """An abstract method for OnPy exceptions."""

    def __init__(self, message: str) -> None:
        """Construct a base OnPyError.

        Args:
            message: The message of the exception

        """
        self.message = message
        super().__init__(message)

    @abstractmethod
    def display(self) -> str:
        """Display the exception as a user-friendly string."""
        ...


class OnPyAuthError(OnPyError):
    """Represents an error caused by bad authentication tokens."""

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string."""
        return f"\nOnPyAuthError({self.message})"


class OnPyApiError(OnPyError):
    """Represents an error caused by an API calls. Should only be used internally."""

    def __init__(self, message: str, response: Response | None = None) -> None:
        """Construct an OnPyApiError.

        Args:
            message: The message of the error
            response: An optional HTTP response to include

        """
        self.response = response
        super().__init__(message)

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string."""
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


class OnPyInternalError(OnPyError):
    """Represents an error caused by an internal OnPy bug."""

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string."""
        return f"\nOnPyInternalError({self.message})"


class OnPyParameterError(OnPyError):
    """Represents an error caused by an invalid user input."""

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string."""
        return f"\nOnPyParameterError({self.message})"


class OnPyFeatureError(OnPyError):
    """Represents an error caused by an OnShape feature during (re)generation."""

    @override
    def display(self) -> str:
        """Display the exception as a user-friendly string."""
        return f"\nOnPyFeatureError({self.message})"


def is_interactive() -> bool:
    """Check if the script is being run in an interactive Python shell."""
    return hasattr(sys, "ps1")


def maybe_exit(exit_code: int) -> None:
    """Exit the program if running from a Python file.

    Will not exit if running in an interactive shell.

    Args:
        exit_code: Bash exit code

    """
    if not is_interactive():
        sys.exit(exit_code)


def handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    """Handle an exception.

    Used to override the default system excepthook to catch OnPy errors.

    Args:
        exc_type: The type of the exception
        exc_value: The instance of the exception
        exc_traceback: A traceback object

    """
    if issubclass(exc_type, OnPyError):
        logger.trace(str(exc_traceback))
        exc_value = cast(OnPyError, exc_value)
        logger.error(exc_value.display())
        maybe_exit(1)
        return

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception
