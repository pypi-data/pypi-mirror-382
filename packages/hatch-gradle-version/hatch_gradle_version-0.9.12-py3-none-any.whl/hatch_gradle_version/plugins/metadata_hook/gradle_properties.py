from functools import cached_property
from pathlib import Path
from typing import Any

from hatch_gradle_version.common.gradle import (
    GradleDependency,
    GradleVersion,
    load_properties,
)
from hatch_gradle_version.common.model import GradlePath

from .base import BaseMetadataHook


class GradlePropertiesMetadataHook(BaseMetadataHook):
    PLUGIN_NAME = "gradle-properties"

    path: GradlePath = Path("gradle.properties")

    def get_format_value(self, key: str) -> Any | None:
        if prop := self.properties.get(key):
            return prop.data

    def parse_gradle_dependency(self, dependency: GradleDependency):
        gradle_version = GradleVersion.from_properties(
            p=self.properties,
            key=dependency.key,
            fmt=None,
        )
        return dependency.version_specifier(gradle_version)

    @cached_property
    def properties(self):
        return load_properties(self.path)
