import copy
import textwrap
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from .gradle_properties import GradlePropertiesMetadataHook


@pytest.mark.parametrize(
    # fmt: off
    "package, op,key,py_version,gradle_version,rc_upper_bound,full_version",
    [
        ("P", "~=", "KEY", "4",       "1.2.3",   False, "P~=1.2.3.4"),
        ("P", "~=", "KEY", "4.5",     "1.2.3",   False, "P~=1.2.3.4.5"),
        ("P", ">=", "KEY", "4.5",     "1.2.3",   False, "P>=1.2.3.4.5"),
        ("P", "~=", "KEY", "4.5",     "1.2.3-6", False, "P~=1.2.3.4.5rc6"),
        ("P", "~=", "KEY", "4.5",     "1.2.3-6", True,  "P~=1.2.3.4.5rc6,<1.2.3.4.5rc7"),
        ("P", "~=", "KEY", "4.5dev6", "1.2.3",   False, "P~=1.2.3.4.5.dev6"),
        ("P", "~=", "KEY", "4.5dev7", "1.2.3-6", False, "P~=1.2.3.4.5rc6.dev7"),
        ("P", "~=", "KEY", "4.5dev8", "1.2.3-6", True,  "P~=1.2.3.4.5rc6.dev8,<1.2.3.4.5rc7.dev8"),
    ],
    # fmt: on
)
def test_gradle_properties_deps(
    tmp_path: Path,
    package: str,
    op: str,
    key: str,
    py_version: str,
    gradle_version: str,
    rc_upper_bound: bool,
    full_version: str,
    monkeypatch: MonkeyPatch,
):
    # arrange
    monkeypatch.setenv("HATCH_GRADLE_DIR", "gradle_dir")

    gradle_properties = tmp_path / "gradle_dir" / "gradle.properties"
    gradle_properties.parent.mkdir()
    gradle_properties.write_text(f"{key}={gradle_version}")

    hook = GradlePropertiesMetadataHook(
        tmp_path.as_posix(),
        {
            "dependencies": [
                {
                    "package": package,
                    "op": op,
                    "key": key,
                    "py-version": py_version,
                    "rc-upper-bound": rc_upper_bound,
                }
            ],
        },
    )

    orig_metadata = {
        "dynamic": [
            "dependencies",
            "optional-dependencies",
        ],
    }

    # act
    metadata = copy.deepcopy(orig_metadata)
    hook.update(metadata)

    # assert
    assert metadata == orig_metadata | {
        "dependencies": [full_version],
        "optional-dependencies": {},
    }


@pytest.mark.parametrize(
    ["dependency", "result"],
    [
        ("", ""),
        ("foo", "foo"),
        ("{foo", "{foo"),
        ("{foo}", "{foo}"),
        ("{placeholder}", "result"),
        ("{{placeholder}}", "{result}"),
        ("{placeholder}{placeholder}", "resultresult"),
        ("{placeholder} {other}", "result value"),
        ("{other} {placeholder}", "value result"),
        ("foo bar baz", "foo bar baz"),
        ("{foo} bar baz", "{foo} bar baz"),
        ("foo {bar} baz", "foo {bar} baz"),
        ("foo bar {baz}", "foo bar {baz}"),
        ("{placeholder} bar baz", "result bar baz"),
        ("foo {placeholder} baz", "foo result baz"),
        ("foo bar {placeholder}", "foo bar result"),
        (
            "package @ {root:uri}/path/to/package-0.1.0-py3-none-any.whl",
            "package @ {root:uri}/path/to/package-0.1.0-py3-none-any.whl",
        ),
    ],
)
def test_placeholders(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    dependency: str,
    result: str,
):
    # arrange
    monkeypatch.setenv("HATCH_GRADLE_DIR", "gradle_dir")

    gradle_properties = tmp_path / "gradle_dir" / "gradle.properties"
    gradle_properties.parent.mkdir()
    gradle_properties.write_text(
        textwrap.dedent(
            """\
            placeholder=result
            other=value
            """
        )
    )

    hook = GradlePropertiesMetadataHook(
        tmp_path.as_posix(),
        {
            "dependencies": [dependency],
            "optional-dependencies": {"dev": [dependency]},
        },
    )

    metadata = {
        "dynamic": [
            "dependencies",
            "optional-dependencies",
        ],
    }

    # act
    hook.update(metadata)

    # assert
    assert metadata == {
        "dynamic": [
            "dependencies",
            "optional-dependencies",
        ],
        "dependencies": [result],
        "optional-dependencies": {"dev": [result]},
    }
