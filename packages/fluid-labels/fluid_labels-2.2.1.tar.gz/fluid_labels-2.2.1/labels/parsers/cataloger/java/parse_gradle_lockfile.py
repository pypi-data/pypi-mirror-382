from pydantic import BaseModel

from labels.model.ecosystem_data.java import JavaArchive, JavaPomProject
from labels.model.file import LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.utils.package_builder import (
    JavaPackageSpec,
    new_java_package,
)
from labels.parsers.cataloger.utils import get_enriched_location


class LockFileDependency(BaseModel):
    group: str
    name: str
    version: str
    line: int | None = None


def parse_gradle_lockfile(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []

    packages = _collect_packages(reader)

    return packages, relationships


def _collect_packages(reader: LocationReadCloser) -> list[Package]:
    packages: list[Package] = []
    dependencies = _collect_dependencies(reader.read_closer.readlines())

    for dependency in dependencies:
        name = dependency.name
        composed_name = f"{dependency.group}:{name}"

        version = dependency.version

        new_location = get_enriched_location(reader.location, line=dependency.line)

        archive = JavaArchive(
            pom_project=JavaPomProject(
                group_id=dependency.group,
                name=name,
                artifact_id=name,
                version=version,
            ),
        )

        package_spec = JavaPackageSpec(
            simple_name=name,
            version=version,
            location=new_location,
            metadata=archive,
            composed_name=composed_name,
        )

        package = new_java_package(package_spec)
        if package:
            packages.append(package)

    return packages


def _collect_dependencies(file_lines: list[str]) -> list[LockFileDependency]:
    dependencies: list[LockFileDependency] = []

    for line_number, line in enumerate(file_lines, 1):
        if _is_dependency_line(line):
            dependency_part = line.split("=")[0]
            group, name, version = dependency_part.split(":")
            dependencies.append(
                LockFileDependency(group=group, name=name, version=version, line=line_number),
            )

    return dependencies


def _is_dependency_line(line: str) -> bool:
    return "=" in line and ":" in line
