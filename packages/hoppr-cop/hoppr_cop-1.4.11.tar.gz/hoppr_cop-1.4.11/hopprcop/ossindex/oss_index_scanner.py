"""A vulnerability scanner that locates vulnerabilities in the Sonatype OSS Index.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/ossindex/oss_index_scanner.py
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

import contextlib
import os

from copy import deepcopy
from typing import TYPE_CHECKING, ClassVar, cast

import rich

from cvss import CVSS2, CVSS3, CVSS4
from cvss.exceptions import CVSS2MalformedError, CVSS3MalformedError, CVSS4MalformedError
from hoppr import Affect, Vulnerability, cdx
from hoppr.utils import get_package_url
from packageurl import PackageURL
from requests.auth import HTTPBasicAuth
from typing_extensions import deprecated

from hopprcop.ossindex.api.ossindex import OssIndex
from hopprcop.utils import (
    _add_vulnerability,
    get_advisories_from_urls,
    get_vulnerability_source,
    purl_check,
    unsupported_purl_feedback,
)
from hopprcop.vulnerability_scanner import VulnerabilitySuper


if TYPE_CHECKING:
    from hopprcop.ossindex.api.model import OssIndexComponent, Vulnerability as OssVulnerability


class OSSIndexScanner(VulnerabilitySuper, author="Sonatype", name="OSS-Index", offline_mode_supported=False):
    """A vulnerability scanner that locates vulnerabilities in Sonotypes' OSS Index."""

    required_environment_variables: ClassVar[list[str]] = ["OSS_INDEX_TOKEN", "OSS_INDEX_USER"]

    api = OssIndex()
    api.oss_index_authentication = HTTPBasicAuth(
        username=os.getenv("OSS_INDEX_USER", ""),
        password=os.getenv("OSS_INDEX_TOKEN", ""),
    )

    supported_types: ClassVar[list[str]] = [
        "cargo",
        "conan",
        "gem",
        "golang",
        "maven",
        "npm",
        "nuget",
        "pypi",
        "rpm",
    ]

    def __init__(self, offline_mode: bool = False):
        self.offline_mode = offline_mode
        super().__init__()

    def get_vulnerabilities_for_purl(self, purls: list[str]) -> list[Vulnerability]:
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a list of CycloneDX vulnerabilities.
        """
        # Check for unsupported purl types and report if found
        filtered_purls = list(
            filter(lambda x: x.type in self.supported_types, [get_package_url(purl) for purl in purls])
        )
        unsupported_purl_feedback(self._scanner_name, self.supported_types, filtered_purls)
        packages_with_version = [package for package in filtered_purls if package.version is not None]
        if packages_without_version := [package for package in filtered_purls if package.version is None]:
            rich.print(
                "[yellow]WARNING: OSS-Index -- does not support purls with missing versions, components may be missed."
            )
            for package in packages_without_version:
                rich.print(f"[yellow]  {package}")

        if not packages_with_version:
            return []

        cleaned_purl_map: dict[str, str] = {}

        def remove_qualifiers(pkg_url: PackageURL) -> PackageURL:
            before_cleaning = pkg_url.to_string()
            cleaned_purl = deepcopy(pkg_url)
            cast("dict", cleaned_purl.qualifiers).clear()

            if cleaned_purl.type == "rpm":
                cleaned_purl = PackageURL(name=pkg_url.name, type=pkg_url.type, version=pkg_url.version)

            cleaned_purl_map[cleaned_purl.to_string()] = before_cleaning

            return cleaned_purl

        cleaned_purls = list(map(remove_qualifiers, packages_with_version))

        matches: list[OssIndexComponent] = self.api.get_component_report(packages=cleaned_purls)
        results: dict[str, Vulnerability] = {}

        for match in matches:
            for vulnerability in match.vulnerabilities:
                _add_vulnerability(
                    vulnerability.id,
                    results,
                    self._convert_to_cyclone_dx(vulnerability, cleaned_purl_map[match.coordinates], purls),
                )

        return list(results.values())

    @deprecated(
        "OSSIndexScanner.get_vulnerabilities_by_purl is deprecated, use OSSIndexScanner.get_vulnerabilities_for_purl"
    )
    def get_vulnerabilities_by_purl(self, purls: list[PackageURL]) -> dict[str, list[Vulnerability]]:
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """
        # Check for unsupported purl types and report if found
        unsupported_purl_feedback(self._scanner_name, self.supported_types, purls)
        purls = list(filter(lambda x: x.type in self.supported_types, purls))
        cleaned_purl_map: dict[str, str] = {}

        def remove_qualifiers(pkg_url: PackageURL) -> PackageURL:
            before_cleaning = pkg_url.to_string()
            cast("dict", pkg_url.qualifiers).clear()

            if pkg_url.type == "rpm":
                pkg_url = PackageURL(name=pkg_url.name, type=pkg_url.type, version=pkg_url.version)

            cleaned_purl_map[pkg_url.to_string()] = before_cleaning

            return pkg_url

        purls = list(map(remove_qualifiers, purls))

        results: list[OssIndexComponent] = self.api.get_component_report(packages=purls)
        enhanced_results: dict[str, list[Vulnerability]] = {}

        for result in results:
            purl = result.coordinates
            enhanced_results[cleaned_purl_map[purl]] = []

            for vulnerability in result.vulnerabilities:
                enhanced_results[cleaned_purl_map[purl]].append(self._convert_to_cyclone_dx_deprecated(vulnerability))

        return enhanced_results

    def _convert_to_cyclone_dx(
        self, vulnerability: OssVulnerability, vuln_purl: str, original_purls: list[str]
    ) -> Vulnerability:
        """Convert an OSS Index vulnerability to cyclone dx."""
        vuln_id = vulnerability.cve if vulnerability.cve is not None else vulnerability.display_name

        try:
            cwes = [int((vulnerability.cwe or "").removeprefix("CWE-"))]
        except ValueError:
            cwes = []

        cyclone_vuln = Vulnerability(
            id=vuln_id,
            description=vulnerability.description,
            cwes=cwes,
            source=get_vulnerability_source(vuln_id),
        )

        cyclone_vuln.ratings = []

        # Add Affects for the current purl to the vulnerability
        cyclone_vuln.affects = [
            Affect.parse_obj(
                {
                    "ref": purl,
                    "versions": [{"version": get_package_url(purl).version, "status": "affected"}],
                }
            )
            for purl in original_purls
            if purl_check(vuln_purl, purl)
        ]

        if vulnerability.cvss_vector is not None:
            cvss = None
            cvss_types_iterator = iter([CVSS4, CVSS3, CVSS2])
            try:
                while cvss is None:
                    cvss_type = next(cvss_types_iterator)
                    with contextlib.suppress(CVSS4MalformedError, CVSS3MalformedError, CVSS2MalformedError):
                        cvss = cvss_type(vulnerability.cvss_vector)
                score_method = {
                    CVSS4: cdx.ScoreMethod.CVSSv4,
                    CVSS3: cdx.ScoreMethod.CVSSv3,
                    CVSS2: cdx.ScoreMethod.CVSSv2,
                }[type(cvss)]
                cyclone_vuln.ratings.append(
                    cdx.Rating(
                        score=float(cvss.base_score or 0.0),
                        severity=cdx.Severity[cvss.severities()[0].lower()],
                        method=score_method,
                        vector=cvss.vector,
                    )
                )
            except StopIteration:
                rich.print(
                    f"[yellow]Vulnerability {cyclone_vuln.id} contains "
                    f"unrecognized CVSS vector {vulnerability.cvss_vector}"
                )

        cyclone_vuln.advisories = get_advisories_from_urls(list(vulnerability.external_references))
        cyclone_vuln.tools = self.scanner_tools()

        return cyclone_vuln

    @deprecated(
        "OSSIndexScanner._convert_to_cyclone_dx_deprecated is deprecated, use OSSIndexScanner._convert_to_cyclone_dx"
    )
    def _convert_to_cyclone_dx_deprecated(self, vulnerability: OssVulnerability) -> Vulnerability:
        """Convert an OSS Index vulnerability to cyclone dx."""
        vuln_id = vulnerability.cve if vulnerability.cve is not None else vulnerability.display_name

        try:
            cwes = [int((vulnerability.cwe or "").removeprefix("CWE-"))]
        except ValueError:
            cwes = []

        cyclone_vuln = Vulnerability(
            id=vuln_id,
            description=vulnerability.description,
            cwes=cwes,
            source=get_vulnerability_source(vuln_id),
        )

        cyclone_vuln.ratings = []

        if vulnerability.cvss_vector is not None:
            try:
                cvss = CVSS3(vulnerability.cvss_vector)
                cyclone_vuln.ratings.append(
                    cdx.Rating(
                        score=cvss.base_score,
                        severity=cdx.Severity[cvss.severities()[0].lower()],
                        method=cdx.ScoreMethod.CVSSv3,
                        vector=cvss.vector,
                    )
                )
            except CVSS3MalformedError:
                cvss = CVSS2(vulnerability.cvss_vector)
                cyclone_vuln.ratings.append(
                    cdx.Rating(
                        score=cvss.base_score,
                        severity=cdx.Severity[cvss.severities()[0].lower()],
                        method=cdx.ScoreMethod.CVSSv2,
                        vector=cvss.vector,
                    )
                )

        cyclone_vuln.advisories = get_advisories_from_urls(list(vulnerability.external_references))
        cyclone_vuln.tools = self.scanner_tools()

        return cyclone_vuln
