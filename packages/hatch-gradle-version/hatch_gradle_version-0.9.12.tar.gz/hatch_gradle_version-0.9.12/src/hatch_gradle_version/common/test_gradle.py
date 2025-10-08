# pyright: reportMissingTypeStubs=none

import jproperties
import pytest

from hatch_gradle_version.common.gradle import GradleVersion


def test_from_properties_valid():
    p = jproperties.Properties()
    p["key"] = "0.11.1-7"

    gradle_version = GradleVersion.from_properties(p, "key", None)

    assert gradle_version == GradleVersion(
        raw_version="0.11.1-7",
        version="0.11.1",
        rc=7,
        build=None,
        extra_versions={"key": "0.11.1-7"},
    )


def test_from_properties_missing_key():
    p = jproperties.Properties()
    p["key"] = "0.11.1-7"

    with pytest.raises(KeyError, match="MISSING_KEY"):
        GradleVersion.from_properties(p, "MISSING_KEY", None)
