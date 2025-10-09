"""Utility functions for working with vulnerabilities and SBOMs.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/utils.py
SPDX-FileType: SOURCE
SPDX-License-Identifier: MIT
--------------------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
--------------------------------------------------------------------------------
"""

from __future__ import annotations

import json
import os
import stat
import tempfile

from pathlib import Path
from typing import TYPE_CHECKING, Any

import requests
import rich
import typer

from hoppr import Component, ComponentType, Sbom, Vulnerability, cdx
from hoppr.utils import dedup_list, get_package_url
from rapidfuzz import fuzz
from requests import Response
from typing_extensions import deprecated


if TYPE_CHECKING:
    from packageurl import PackageURL


FUZZY_MATCH_THRESHOLD = 85


def purl_check(first_purl_str: str, second_purl_str: str) -> bool:
    """Determine if two purls are equivalent. Returns true if all properties of the PURL match."""
    if not (first_purl_str and second_purl_str):
        return False

    self_purl = get_package_url(first_purl_str)
    other_purl = get_package_url(second_purl_str)

    first_qualifiers = {}
    second_qualifiers = {}
    match self_purl.qualifiers, other_purl.qualifiers:
        case str(first), str(second):
            first_qualifiers = {"encoded": first}
            second_qualifiers = {"encoded": second}
        case str(first), dict(second):
            first_qualifiers = {"encoded": first}
            second_qualifiers = second
        case dict(first), str(second):
            first_qualifiers = first
            second_qualifiers = {"encoded": second}
        case dict(first), dict(second):
            first_qualifiers = first
            second_qualifiers = second

    qual_keys = dedup_list(first_qualifiers | second_qualifiers)

    return all(
        [
            self_purl.name == other_purl.name,
            self_purl.type == other_purl.type,
            self_purl.namespace == other_purl.namespace,
            str(self_purl.version).removeprefix("v") == str(other_purl.version).removeprefix("v"),
            self_purl.subpath == other_purl.subpath,
            *[qualifier_match(key, first_qualifiers, second_qualifiers) for key in qual_keys],
        ]
    )


def qualifier_match(key: str, first_qualifiers: dict[str, str], second_qualifiers: dict[str, str]) -> bool:
    """Determines if two groups of PURL qualifiers contain the same entries using a fuzzy match."""
    # Compare only if both purls have a value for specified qualifier
    if key not in first_qualifiers or key not in second_qualifiers:
        return True

    return fuzz.ratio(first_qualifiers.get(key, ""), second_qualifiers.get(key, "")) > FUZZY_MATCH_THRESHOLD


def _add_vulnerability(key: str, vuln_list: dict[str, Vulnerability], new_vuln: Vulnerability):
    vuln_list.setdefault(key, Vulnerability())
    vuln_list[key].merge(new_vuln)


def unsupported_purl_feedback(scanner_name: str, supported_types: list[str], purl_list: list[PackageURL]) -> None:
    """Determine if there are purls that the scanner does not support, report findings."""
    purl_types = list(dict.fromkeys(purl.type for purl in purl_list))

    for purl_type in filter(lambda type_: type_ not in supported_types, purl_types):
        rich.print(
            f"[yellow]WARNING: {scanner_name} -- does not support purls of type {purl_type}, components may be missed.",
        )


def convert_xml_to_json(file_path: Path) -> Path:
    """Function to convert a xml file to json format."""
    typer.echo("xml format detected, attempt to convert with cyclonedx tools")

    # Default to the path specified in the hoppr-cop docker file or define the local filename to save data
    docker_image_path = Path("/usr/local/bin/cyclone-dx")
    cyclone_dx_path = docker_image_path if docker_image_path.exists() else Path(tempfile.gettempdir()) / "cyclonedx"
    if not cyclone_dx_path.exists():
        typer.echo("cyclonedx tools not found Attempting to download")
        if url := os.getenv("CYCLONE_INSTALL_URL"):
            # Make http request for remote file datae
            data = requests.get(url, timeout=60)

            # Save file data to local copy
            cyclone_dx_path.write_bytes(data.content)
        else:
            msg = typer.style(
                "In order to support xml SBOMs, you must set 'CYCLONE_INSTALL_URL' to "
                "the correct release of cyclone-dx cli. https://github.com/CycloneDX/cyclonedx-cli/releases",
                fg=typer.colors.RED,
            )
            typer.echo(msg)
            raise typer.Exit(code=1)

    cyclone_dx_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    os.system(
        f"{cyclone_dx_path.absolute()} convert --input-file {file_path} \
            --output-file {tempfile.gettempdir()}/{file_path.name}.json --output-format json",
    )
    return Path(f"{tempfile.gettempdir()}/{file_path.name}.json")


def parse_sbom(sbom_file: Path) -> Sbom:
    """Parses a Software Bill of Materials File."""
    if sbom_file.is_file() and sbom_file.exists():
        typer.echo(f"processing {sbom_file}")

        if sbom_file.suffix == ".xml":
            sbom_file = convert_xml_to_json(sbom_file)

        sbom_json_object = json.loads(sbom_file.read_text(encoding="utf-8"))
        sbom = create_sbom_object(sbom_json_object, str(sbom_file))
    else:
        typer.secho(f"{sbom_file!s} is not a file", fg=typer.colors.RED)
        raise typer.Exit

    return sbom


def parse_sbom_json_string(sbom_file_json: str, sbom_info: str) -> Sbom:
    """Parses a Software Bill of Materials JSON String."""
    sbom_json_object = json.loads(sbom_file_json)
    return create_sbom_object(sbom_json_object, sbom_info)


def create_sbom_object(sbom_json_object: dict[str, Any], sbom_info: str) -> Sbom:
    """Creates a Software Bill of Materials Object."""
    spec_version = sbom_json_object.get("specVersion", "")
    sbom_json_object.pop("$schema", None)

    if spec_version not in {"1.2", "1.3", "1.4", "1.5", "1.6"}:
        typer.secho(f"{sbom_info} is an unknown spec version ({spec_version})")
        raise typer.Exit

    return Sbom.parse_obj(sbom_json_object)


def get_vulnerability_source(vulnerability_id: str) -> cdx.VulnerabilitySource | None:
    """Generate the source for a vulnerability based on a given ID."""
    match vulnerability_id:
        case cve if cve.startswith("CVE-"):
            return cdx.VulnerabilitySource(
                name="NVD",
                url=f"https://nvd.nist.gov/vuln/detail/{vulnerability_id}",
            )
        case gh if gh.startswith(("GHSA", "GMS")):
            return cdx.VulnerabilitySource(
                name="Github Advisories",
                url=f"https://github.com/advisories/{vulnerability_id}",
            )
        case oss if oss.startswith("sonatype"):
            return cdx.VulnerabilitySource(
                name="OSS Index",
                url=f"https://ossindex.sonatype.org/vulnerability/{vulnerability_id}",
            )
        case _:
            return None


def get_advisories_from_urls(urls: list[str]) -> list[cdx.Advisory]:
    """Generates a list of advisories for the given set of urls."""
    urls = list(set(urls))
    return [cdx.Advisory(url=x) for x in urls]


def get_references_from_ids(ids: list[str], primary_id: str) -> list[cdx.Reference]:
    """Builds a list of Reference objects to the given vulnerability IDs."""
    references = []

    for ident in list(set(ids)):
        if ident != primary_id and (source := get_vulnerability_source(ident)):
            references.append(cdx.Reference(id=ident, source=source))

    return references


def build_bom_dict_from_purls(purls: list[PackageURL]) -> dict[str, Any]:
    """Create SBOM dictionary from PackageURL list."""
    sbom = Sbom(
        components=[
            Component(
                type=ComponentType.LIBRARY,
                name=purl.name if purl.type == "npm" else f"{purl.namespace}/{purl.name}",
                version=purl.version,
                purl=purl.to_string(),
                group=purl.namespace,
                bom_ref=purl.to_string(),
                description="test",
                author="test",
                externalReferences=[],
            )
            for purl in purls
        ]
    )

    return sbom.dict()


def create_bom_from_purl_list(purls: list[str]) -> Sbom:
    """Creates a skeleton SBOM from a list of purls."""
    return Sbom.parse_obj(build_bom_dict_from_purls([get_package_url(purl) for purl in purls]))


@deprecated("utils.build_bom_from_purls is deprecated, use utils.create_bom_from_purl_list")
def build_bom_from_purls(purls: list[PackageURL]) -> Sbom:
    """Creates a skeleton SBOM from a list of purls."""
    return Sbom.parse_obj(build_bom_dict_from_purls(purls))


def api_query(url: str, proxies: dict[str, str] | None = None) -> Response:
    """Load response from API query into JSON."""
    return requests.get(
        url=url,
        allow_redirects=True,
        proxies=proxies,
        stream=True,
        verify=True,
        timeout=60,
    )
