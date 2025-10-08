import re
from abc import ABC, abstractmethod
from typing import Any, Iterator

from hatchling.metadata.plugin.interface import MetadataHookInterface
from pydantic import Field

from hatch_gradle_version.common.decorators import listify
from hatch_gradle_version.common.gradle import GradleDependency
from hatch_gradle_version.common.model import GradlePath, HookModel

Dependencies = list[str | GradleDependency]

PLACEHOLDER_REGEX = re.compile(r"\{([a-zA-Z0-9_.\-]+)\}")


class BaseMetadataHook(HookModel, MetadataHookInterface, ABC):
    dependencies: Dependencies = Field(default_factory=dict)
    optional_dependencies: dict[str, Dependencies] = Field(default_factory=dict)
    path: GradlePath

    @abstractmethod
    def get_format_value(self, key: str) -> Any | None: ...

    @abstractmethod
    def parse_gradle_dependency(self, dependency: GradleDependency) -> str: ...

    def update(self, metadata: dict[str, Any]) -> None:
        """Implements MetadataHookInterface."""
        self.set_dynamic(
            metadata,
            "dependencies",
            self.parse_dependencies(self.dependencies),
        )

        self.set_dynamic(
            metadata,
            "optional-dependencies",
            {
                key: self.parse_dependencies(value)
                for key, value in self.optional_dependencies.items()
            },
        )

    @listify
    def parse_dependencies(self, dependencies: Dependencies) -> Iterator[str]:
        for dependency in dependencies:
            match dependency:
                case str():
                    result = ""
                    index = 0
                    for match in PLACEHOLDER_REGEX.finditer(dependency):
                        # if we fail to find a placeholder, just leave it in the string
                        # this is especially important for eg. Hatch's `{root:uri}`
                        if value := self.get_format_value(match.group(1)):
                            # add everything before the placeholder, then the value
                            result += dependency[index : match.start()] + value
                            # move the index to the character after the placeholder
                            index = match.end()
                    # add anything after the final placeholder
                    result += dependency[index:]
                    yield result
                case GradleDependency():
                    yield self.parse_gradle_dependency(dependency)

    def set_dynamic(self, metadata: dict[str, Any], key: str, value: Any):
        if key in metadata:
            raise ValueError(
                f"`{key}` may not be listed in the `project` table when using hatch-gradle-version to populate dependencies. Please use `tool.hatch.metadata.hooks.{self.PLUGIN_NAME}.{key}` instead."
            )
        if key not in metadata.get("dynamic", []):
            raise ValueError(
                f"`{key}` must be listed in `project.dynamic` when using hatch-gradle-version to populate dependencies."
            )
        metadata[key] = value
