from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Callable

import jproperties  # pyright: ignore[reportMissingTypeStubs]
from packaging.version import Version

from .model import DefaultModel, KebabModel

GRADLE_VERSION_RE = re.compile(
    r"""
    v?
    (?P<version>
        \d+
        (?:\.\d+)*
    )
    (?:
        -(?P<rc>\d+)
    )?
    (?:
        \+(?P<build>.+)
    )?
    """,
    re.VERBOSE,
)


# this uses Model so I can be lazy with constructing it from a regex
class GradleVersion(DefaultModel, arbitrary_types_allowed=True):
    raw_version: str
    version: str
    rc: int | None
    build: str | None
    extra_versions: dict[str, str]

    @classmethod
    def from_properties(
        cls,
        p: jproperties.Properties,
        key: str,
        fmt: Callable[[str, dict[str, str]], str] | None,
    ):
        if key not in p:
            raise KeyError(f"Key not found in gradle.properties: {key}")
        return cls.from_raw(
            raw_version=str(p[key].data),
            extra_versions={key: value.data for key, value in p.items()},
            fmt=fmt,
        )

    @classmethod
    def from_raw(
        cls,
        raw_version: str,
        extra_versions: dict[str, str],
        fmt: Callable[[str, dict[str, str]], str] | None,
    ):
        if fmt:
            raw_version = fmt(raw_version, extra_versions)

        match = GRADLE_VERSION_RE.match(raw_version)
        if match is None:
            raise ValueError(f"Failed to parse version: {raw_version}")

        data = match.groupdict() | {
            "raw_version": raw_version,
            "extra_versions": extra_versions,
        }
        return cls.model_validate(data)

    def full_version(
        self,
        py_version: str | Version,
        *,
        next_rc: bool = False,
    ) -> str:
        # ensure py_version is a valid version by itself
        if isinstance(py_version, str):
            py_version = Version(py_version)

        if py_version.pre:
            raise ValueError("a/b/c/pre/rc is reserved for Gradle prereleases")

        # split py_version at the point where we need to insert the gradle prerelease
        py_base = py_version.base_version
        py_rest = str(py_version).removeprefix(py_base)

        # construct the full version
        # eg. 1.2.3 . 4.5 rc6 .dev7
        rc = self.rc_segment(next_rc)
        full_version = self.version + "." + py_base + rc + py_rest

        # round-trip through Version to normalize it
        return str(Version(full_version))

    def rc_segment(self, next_rc: bool):
        if self.rc is None:
            return ""
        return f"rc{self.next_rc if next_rc else self.rc}"

    @property
    def next_rc(self):
        if self.rc is None:
            raise ValueError("Tried to call next_rc on a non-rc version")
        return self.rc + 1

    def __str__(self) -> str:
        return self.raw_version


def load_properties(path: Path):
    p = jproperties.Properties()
    with open(path, "rb") as f:
        p.load(f, "utf-8")
    return p


class GradleDependency(KebabModel):
    package: str
    op: str
    key: str
    py_version: str
    rc_upper_bound: bool = False
    """If True and gradle_version has a pre-release suffix (eg. `0.1.0-1`), add a
    corresponding exclusive upper bound for the next RC version (eg. `<0.1.0.1.0rc2`).
    
    If True, the operators `>=` and `~=` effectively become `==`. If False, pip may
    install a later prerelease or a released version. There's not really a "best"
    option, which is why this flag exists.

    The default is `False`. This *should* work in more cases than not.
    """

    def version_specifier(self, gradle_version: GradleVersion):
        full_version = gradle_version.full_version(self.py_version)
        lower_bound = self.op + full_version

        if gradle_version.rc is None or not self.rc_upper_bound:
            return self.package + lower_bound

        if "<" not in self.op:
            warnings.warn(
                f"Dependency on package `{self.package}` will ONLY accept `{full_version}` (`{gradle_version}` is a prerelease and `rc-upper-bound` is enabled)."
            )

        upper_bound = "<" + gradle_version.full_version(self.py_version, next_rc=True)
        return f"{self.package}{lower_bound},{upper_bound}"
