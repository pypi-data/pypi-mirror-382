import json
from typing import Annotated, Any, overload

from pydantic import Field, field_validator
from pydantic.types import JsonValue

from hatch_gradle_version.common.gradle import GradleVersion
from hatch_gradle_version.common.model import GradlePath

from .base import BaseVersionSource


class JSONVersionSource(BaseVersionSource):
    PLUGIN_NAME = "json"

    json_path: GradlePath
    key: Annotated[list[str], Field(min_length=1)]

    def get_gradle_version(self) -> GradleVersion:
        with self.json_path.open() as f:
            data: JsonValue = json.load(f)

        raw_version = data
        for key in self.key:
            if not isinstance(raw_version, dict):
                raise ValueError(f"Invalid key: {self.key} (not a dict: {raw_version})")
            raw_version = raw_version[key]

        raw_version = self.json_to_string(raw_version)
        if raw_version is None:
            raise ValueError(f"Invalid key: {self.key} (invalid value: {raw_version})")

        extra_versions = dict[str, str]()
        self.get_extra_versions(data, extra_versions, [])

        return GradleVersion.from_raw(
            raw_version,
            extra_versions,
            self.fmt_raw_gradle_version,
        )

    def get_extra_versions(
        self,
        value: JsonValue,
        result: dict[str, str],
        parents: list[str],
    ):
        match value:
            case dict():
                for key, child in value.items():
                    parents.append(key)
                    self.get_extra_versions(child, result, parents)
                    parents.pop()
            case list():
                for i, child in enumerate(value):
                    parents.append(str(i) if parents else f"_{i}")
                    self.get_extra_versions(child, result, parents)
                    parents.pop()
            case _:
                result[".".join(parents)] = self.json_to_string(value)

    @overload
    def json_to_string(self, value: str | bool | int | float | None) -> str: ...

    @overload
    def json_to_string(self, value: list[JsonValue] | dict[str, JsonValue]) -> None: ...

    @overload
    def json_to_string(self, value: JsonValue) -> str | None: ...

    def json_to_string(self, value: JsonValue):
        match value:
            case dict() | list():
                return None
            case True:
                return "true"
            case False:
                return "false"
            case None:
                return "null"
            case _:
                return str(value)

    @field_validator("key", mode="before")
    @classmethod
    def _split_key(cls, value: Any):
        match value:
            case str():
                return value.split(".")
            case _:
                return value
