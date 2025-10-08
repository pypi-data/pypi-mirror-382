from pathlib import Path

from hatch_gradle_version.common.gradle import GradleVersion, load_properties
from hatch_gradle_version.common.model import GradlePath

from .base import BaseVersionSource


class GradlePropertiesVersionSource(BaseVersionSource):
    PLUGIN_NAME = "gradle-properties"

    gradle_path: GradlePath = Path("gradle.properties")
    key: str = "modVersion"

    def get_gradle_version(self) -> GradleVersion:
        p = load_properties(self.gradle_path)
        return GradleVersion.from_properties(p, self.key, self.fmt_raw_gradle_version)
