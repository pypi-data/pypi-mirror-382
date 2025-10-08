import os
from pathlib import Path
from typing import Annotated, Any, ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)

DEFAULT_CONFIG = ConfigDict(extra="forbid")


def to_kebab(string: str) -> str:
    return string.replace("_", "-")


class DefaultModel(BaseModel):
    model_config = DEFAULT_CONFIG

    # workaround for https://github.com/pypa/hatch/issues/959
    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
    ):
        try:
            return super().model_validate(
                obj,
                strict=strict,
                from_attributes=from_attributes,
                context=context,
            )
        except ValidationError as e:
            # wrap ValidationError so Hatchling doesn't try to construct it
            raise RuntimeError(e)

    # workaround for https://github.com/pypa/hatch/issues/959
    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: dict[str, Any] | None = None,
    ):
        try:
            return super().model_validate_json(
                json_data,
                strict=strict,
                context=context,
            )
        except ValidationError as e:
            raise RuntimeError(e)


class KebabModel(DefaultModel, alias_generator=to_kebab):
    pass


ProjectPath = Annotated[Path, "ProjectPath"]

GradlePath = Annotated[Path, "GradlePath"]


class HookModel(KebabModel, validate_default=True):
    PLUGIN_NAME: ClassVar[str]

    root__: str | Path = Field(alias="root", kw_only=False)
    config__: dict[str, Any] = Field(alias="config", kw_only=False)

    def __init__(self, root: str | Path, config: dict[str, Any]):
        self.__pydantic_validator__.validate_python(
            {"root": root, "config": config},
            self_instance=self,
        )

    @classmethod
    def from_config(cls, root: str | Path, config: dict[str, Any]):
        return cls(root, config)

    @property
    def root(self):
        return self.root__

    @property
    def config(self):
        return self.config__

    @model_validator(mode="before")
    def _merge_with_config(cls, value: Any):
        match value:
            case {"config": dict() as config}:
                return config | value
            case _:
                return value

    @field_validator("*", mode="after")
    @classmethod
    def _resolve_paths(cls, value: Any, info: ValidationInfo):
        root = info.data.get("root__")
        if not root:
            return value
        root = Path(root)

        if info.field_name is None:
            raise RuntimeError(
                f"Expected field_name to be a string, but got None. This is probably a bug.\n{info=}"
            )

        field_info = cls.model_fields[info.field_name]

        for annotation in field_info.metadata:
            match annotation:
                case "ProjectPath":
                    return root / value
                case "GradlePath":
                    return root / os.getenv("HATCH_GRADLE_DIR", "") / value
                case _:
                    pass

        return value
