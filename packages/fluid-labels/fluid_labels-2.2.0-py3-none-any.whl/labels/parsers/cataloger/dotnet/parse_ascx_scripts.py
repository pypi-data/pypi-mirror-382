import re
from contextlib import suppress

from bs4 import BeautifulSoup
from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.utils import get_npm_package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning

SCRIPT_DEP = re.compile(
    r"(?P<name>[^\s\/]*)(?P<separator>[-@\/])"
    r"(?P<version>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))",
)

NPM_CDNS = (
    "https://cdn.jsdelivr.net/npm/",
    "https://unpkg.com/",
    "https://cdn.skypack.dev/",
    "https://cdn.esm.sh/",
    "https://code.jquery.com/",
    "https://cdnjs.cloudflare.com/",
)


def parse_ascx_scripts(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    html = None
    with suppress(UnicodeError):
        try:
            html = BeautifulSoup(reader.read_closer, features="html.parser")
        except AssertionError:
            return [], []

    if not html:
        return [], []

    packages = []
    for script in html("script"):
        src_attribute = str(script.attrs.get("src"))
        if not (src_attribute and src_attribute.endswith(".js")):
            continue

        if not src_attribute.startswith(NPM_CDNS):
            continue

        matched = SCRIPT_DEP.search(src_attribute)

        if not matched:
            continue

        name = matched.group("name")
        version = matched.group("version")

        if not name or not version:
            continue

        new_location = get_enriched_location(reader.location, line=script.sourceline)
        p_url = get_npm_package_url(name, version)

        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    licenses=[],
                    locations=[new_location],
                    language=Language.JAVASCRIPT,
                    type=PackageType.NpmPkg,
                    p_url=p_url,
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue

    return packages, []
