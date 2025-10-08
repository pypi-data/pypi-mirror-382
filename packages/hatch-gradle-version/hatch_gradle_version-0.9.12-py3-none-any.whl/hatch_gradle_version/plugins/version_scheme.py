from typing import Any

from hatchling.version.scheme.standard import StandardScheme

from ..common.gradle import GradleVersion
from .version_source.base import VersionData


class GradleVersionScheme(StandardScheme):
    PLUGIN_NAME = "gradle"

    def update(
        self,
        desired_version: str,
        original_version: str,
        version_data: dict[str, Any] | VersionData,
    ) -> str:
        assert isinstance(version_data["py_version"], str)
        assert isinstance(version_data["full_gradle_version"], GradleVersion)

        # just update the Python component of the version
        new_py_version = super().update(
            desired_version=desired_version,
            original_version=version_data["py_version"],
            version_data=version_data | {"version": version_data["py_version"]},
        )

        # update version_data so version_source can write the updated py version
        version_data["py_version"] = new_py_version
        return version_data["full_gradle_version"].full_version(new_py_version)
