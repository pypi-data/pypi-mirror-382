from hatchling.plugin import hookimpl

from .plugins.metadata_hook.gradle_properties import GradlePropertiesMetadataHook
from .plugins.metadata_hook.version_catalog import VersionCatalogMetadataHook
from .plugins.version_scheme import GradleVersionScheme
from .plugins.version_source.gradle_properties import GradlePropertiesVersionSource
from .plugins.version_source.json import JSONVersionSource


@hookimpl
def hatch_register_version_source():
    return [GradlePropertiesVersionSource, JSONVersionSource]


@hookimpl
def hatch_register_version_scheme():
    return GradleVersionScheme


@hookimpl
def hatch_register_metadata_hook():
    return [GradlePropertiesMetadataHook, VersionCatalogMetadataHook]
