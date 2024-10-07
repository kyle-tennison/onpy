"""Interface for controlling OnShape API versions.

For each API call, OnShape requests a version; this can be a workspace,
a version, or a microversion. Each of these will have a corresponding ID.
This script adds scripts that make it easy to interface with any of these
versions.

OnPy - May 2024 - Kyle Tennison

"""

from abc import ABC, abstractmethod


class VersionTarget(ABC):
    """Abstract base class for OnShape version targets."""

    @property
    @abstractmethod
    def wvm(self) -> str:
        """Convert versioning method into {wvm} block."""
        ...

    @property
    @abstractmethod
    def wvmid(self) -> str:
        """Convert versioning method into {wvmid} block."""
        ...


class MicroversionWVM(VersionTarget):
    """Microversion Target for WVM."""

    def __init__(self, microversion_id: str) -> None:
        """Construct a Microversion type WVM version target from a workspace id."""
        self.id = microversion_id

    @property
    def wvm(self) -> str:
        """The {wvm} of the version."""
        return "m"

    @property
    def wvmid(self) -> str:
        """The {wvmid} of the version."""
        return self.id


class VersionWVM(VersionTarget):
    """Version Target for WVM."""

    def __init__(self, version_id: str) -> None:
        """Construct a Version type WVM version target from a workspace id."""
        self.id = version_id

    @property
    def wvm(self) -> str:
        """The {wvm} of the version."""
        return "v"

    @property
    def wvmid(self) -> str:
        """The {wvmid} of the version."""
        return self.id


class WorkspaceWVM(VersionTarget):
    """Workspace Target for WVM."""

    def __init__(self, workspace_id: str) -> None:
        """Construct a Workspace type WVM version target from a workspace id."""
        self.id = workspace_id

    @property
    def wvm(self) -> str:
        """The {wvm} of the version."""
        return "w"

    @property
    def wvmid(self) -> str:
        """The {wvmid} of the version."""
        return self.id
