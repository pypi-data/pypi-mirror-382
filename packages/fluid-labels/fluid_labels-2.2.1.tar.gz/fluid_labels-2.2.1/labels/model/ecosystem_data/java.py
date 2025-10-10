from typing import NamedTuple

from labels.model.ecosystem_data.base import EcosystemDataModel


class PomContext(NamedTuple):
    parent_info: dict[str, str] | None
    parent_version_properties: dict[str, str] | None
    manage_deps: dict[str, str] | None


class JavaPomParent(NamedTuple):
    group_id: str
    artifact_id: str
    version: str


class JavaPomProject(NamedTuple):
    group_id: str | None = None
    artifact_id: str | None = None
    version: str | None = None
    name: str | None = None
    parent: JavaPomParent | None = None


class JavaManifest(NamedTuple):
    main: dict[str, str]
    sections: list[dict[str, str]] | None = None


class JavaPomProperties(NamedTuple):
    name: str | None = None
    group_id: str | None = None
    artifact_id: str | None = None
    version: str | None = None


class JavaArchive(EcosystemDataModel):
    manifest: JavaManifest | None = None
    pom_properties: JavaPomProperties | None = None
    pom_project: JavaPomProject | None = None
