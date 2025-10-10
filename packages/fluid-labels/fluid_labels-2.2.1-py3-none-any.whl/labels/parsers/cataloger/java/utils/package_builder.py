from typing import NamedTuple

from packageurl import PackageURL
from pydantic_core import ValidationError

from labels.model.ecosystem_data.java import JavaArchive
from labels.model.file import Location
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.java.utils.package import group_id_from_java_metadata
from labels.parsers.cataloger.utils import log_malformed_package_warning


class JavaPackageSpec(NamedTuple):
    simple_name: str | None
    version: str | None
    location: Location
    composed_name: str | None = None
    metadata: JavaArchive | None = None


def new_java_package(package_spec: JavaPackageSpec) -> Package | None:
    simple_name = package_spec.simple_name
    version = package_spec.version

    if not simple_name or not version:
        return None

    p_url = _get_package_url_for_java(simple_name, version, package_spec.metadata)

    name = package_spec.composed_name or simple_name

    try:
        return Package(
            name=name,
            version=version,
            locations=[package_spec.location],
            language=Language.JAVA,
            type=PackageType.JavaPkg,
            p_url=p_url,
            ecosystem_data=package_spec.metadata,
            licenses=[],
        )
    except ValidationError as ex:
        log_malformed_package_warning(package_spec.location, ex)
        return None


def _get_package_url_for_java(name: str, version: str, metadata: JavaArchive | None = None) -> str:
    group_id = name

    group_id_from_metadata = group_id_from_java_metadata(name, metadata)
    if group_id_from_metadata:
        group_id = group_id_from_metadata

    return PackageURL(type="maven", namespace=group_id, name=name, version=version).to_string()
