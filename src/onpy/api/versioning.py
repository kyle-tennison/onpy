"""

Interface for controlling OnShape API versions.

For each API call, OnShape requests a version; this can be a workspace,
a version, or a microversion. Each of these will have a corresponding ID.
This script adds scripts that make it easy to interface with any of these 
versions.

OnPy - May 2024 - Kyle Tennison

"""

from abc import ABC, abstractmethod


class VersionTarget(ABC):

    @property
    @abstractmethod
    def wvm(self) -> str:
        """Convert versioning method into {wvm} block"""
        ...

    @property
    @abstractmethod
    def wvmid(self) -> str:
        """Convert versioning method into {wvmid} block"""
        ...


class MicroversionWVM(VersionTarget):
    """Microversion Target for WVM"""

    def __init__(self, microversion_id: str):
        self.id = microversion_id

    @property
    def wvm(self) -> str:
        return "m"

    @property
    def wvmid(self) -> str:
        return self.id


class VersionWVM(VersionTarget):
    """Version Target for WVM"""

    def __init__(self, version_id: str) -> None:
        self.id = version_id

    @property
    def wvm(self) -> str:
        return "v"

    @property
    def wvmid(self) -> str:
        return self.id


class WorkspaceWVM(VersionTarget):
    """Workspace Target for WVM"""

    def __init__(self, workspace_id: str) -> None:
        self.id = workspace_id

    @property
    def wvm(self) -> str:
        return "w"

    @property
    def wvmid(self) -> str:
        return self.id
