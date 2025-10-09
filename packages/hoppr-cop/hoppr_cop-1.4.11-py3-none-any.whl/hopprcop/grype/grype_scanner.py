"""Scan an SBOM using the Grype CLI.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/grype/grype_scanner.py
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

from subprocess import PIPE, Popen
from typing import TYPE_CHECKING, Any, ClassVar

import rich

from cvss import CVSS2, CVSS3
from hoppr import Affect, HopprError, Sbom, Vulnerability, cdx
from hoppr.utils import get_package_url
from typing_extensions import deprecated

from hopprcop.grype.models import GrypeResult, Match, Vulnerability as GrypeVulnerability
from hopprcop.utils import (
    _add_vulnerability,
    build_bom_from_purls,
    create_bom_from_purl_list,
    get_advisories_from_urls,
    get_references_from_ids,
    get_vulnerability_source,
    purl_check,
    unsupported_purl_feedback,
)
from hopprcop.vulnerability_scanner import VulnerabilitySuper


if TYPE_CHECKING:
    from packageurl import PackageURL


class GrypeScanner(VulnerabilitySuper, author="Anchore", name="Grype", offline_mode_supported=True):
    """This scanner utilizes the anchore grype command line to gather vulnerabilities."""

    required_tools_on_path: ClassVar[list[str]] = ["grype"]
    grype_os_distro = os.getenv("OS_DISTRIBUTION", None)

    process_environment = None
    supported_types: ClassVar[list[str]] = [
        "cargo",
        "composer",
        "docker",
        "gem",
        "golang",
        "maven",
        "npm",
        "nuget",
        "oci",
        "pypi",
        "rpm",
    ]

    def __init__(self, offline_mode: bool = False, grype_os_distro: str | None = None):
        self.grype_os_distro = grype_os_distro or os.getenv("OS_DISTRIBUTION", None)

        self.offline_mode = offline_mode
        self.process_environment = os.environ.copy()
        if self.offline_mode:
            self.process_environment["GRYPE_DB_AUTO_UPDATE"] = "false"
            self.process_environment["GRYPE_DB_VALIDATE_AGE"] = "false"

        super().__init__()

    def get_vulnerability_db(self) -> bool:
        """Downloads vulnerability database."""
        args = ["grype", "db", "update"]

        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            stdout, stderr = process.communicate()

            if not stdout and stderr:
                rich.print(f"GrypeScanner: generated an exception: {stderr.decode()}")
                return False

            rich.print(f"GrypeScanner: {stdout.decode()}")
            return True

    def get_vulnerabilities_for_purl(self, purls: list[str]) -> list[Vulnerability]:  # pragma: no cover
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a list of CycloneDX vulnerabilities.
        """
        bom = create_bom_from_purl_list(purls)
        return self.get_vulnerabilities_for_sbom(bom)

    def get_vulnerabilities_for_sbom(self, bom: Sbom) -> list[Vulnerability]:
        """Get the vulnerabilities for a CycloneDx compatible Software Bill of Materials (SBOM).

        Returns a list of CycloneDX vulnerabilities.
        """
        # Check for unsupported purl types and report if found
        purls = [component.purl for component in bom.components or [] if component.purl]
        unsupported_purl_feedback(self._scanner_name, self.supported_types, [get_package_url(purl) for purl in purls])

        results: dict[str, Vulnerability] = {}

        args = ["grype", "--output", "json"]
        if self.grype_os_distro is not None:
            args += ["--distro", self.grype_os_distro]

        with Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, env=self.process_environment) as process:
            # Remove tools from metadata due to cyclonedx-go only having partial support for spec version 1.5 (as of 0.72.0)
            # TODO: roll back once full support is in cyclonedx-go
            parsed_bom = bom.copy(deep=True)
            if parsed_bom.metadata:
                parsed_bom.metadata.tools = None

            stdout, stderr = process.communicate(input=(bytes(parsed_bom.json(), "utf-8")))
            if process.returncode != 0:
                raise HopprError(f"{self.__class__.__name__} generated an exception: {stderr.decode()}")

            result = GrypeResult(**json.loads(stdout))

            for match in [match for match in result.matches if match.artifact.purl in purls]:
                match_purl = get_package_url(match.artifact.purl)
                if match_purl.type != "npm" or match_purl.namespace != "@types":
                    try:
                        _add_vulnerability(match.vulnerability.id, results, self._convert_to_cyclone_dx(match, purls))
                    except AttributeError:
                        rich.print(
                            f"[yellow]WARNING: {self._scanner_name} -- received an AttributeError while attempting to add vulnerability - {match.vulnerability.id}"
                        )

        return list(results.values())

    @deprecated("GrypeScanner.get_vulnerabilities_by_purl is deprecated, use GrypeScanner.get_vulnerabilities_for_purl")
    def get_vulnerabilities_by_purl(
        self, purls: list[PackageURL]
    ) -> dict[str, list[Vulnerability]]:  # pragma: no cover
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """
        bom = build_bom_from_purls(purls)
        return self.get_vulnerabilities_by_sbom(bom)

    @deprecated("GrypeScanner.get_vulnerabilities_by_sbom is deprecated, use GrypeScanner.get_vulnerabilities_for_sbom")
    def get_vulnerabilities_by_sbom(self, bom: Sbom) -> dict[str, list[Vulnerability]]:
        """Parse a CycloneDX compatible SBOM and return a list of vulnerabilities.

        Returns a dictionary of package URL to vulnerabilities.
        """
        args = ["grype", "--output", "json"]
        if self.grype_os_distro is not None:
            args += ["--distro", self.grype_os_distro]

        with Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, env=self.process_environment) as process:
            # Remove tools from metadata due to cyclonedx-go only having partial support for spec version 1.5 (as of 0.72.0)
            # TODO: roll back once full support is in cyclonedx-go
            parsed_bom = bom.copy(deep=True)
            if parsed_bom.metadata:
                parsed_bom.metadata.tools = None

            stdout, stderr = process.communicate(input=(bytes(parsed_bom.json(), "utf-8")))
            result = GrypeResult(**json.loads(stdout))

            results: dict[str, list[Vulnerability]] = {}

        # Use a generator to get all of the component purls if they exist and intialize the results for the purl
        purls = [component.purl for component in bom.components or [] if component.purl]
        for pkg_url in purls:
            results[pkg_url] = []

        # Check for unsupported purl types and report if found
        unsupported_purl_feedback(self._scanner_name, self.supported_types, [get_package_url(purl) for purl in purls])

        for match in list(result.matches):
            purl = get_package_url(match.artifact.purl)

            if purl.type != "npm" or purl.namespace != "@types":
                # Raise the error if `match.artifact.purl` is not already a key in the dict
                # This can occur when the `match.artifact.purl` is not in the `component.purl` above
                try:
                    # Append the Grype result information to the results dict at the purl key
                    results[match.artifact.purl].append(self._convert_to_cyclone_dx_deprecated(match))
                except KeyError:
                    rich.print(f"[yellow]WARNING: {self._scanner_name} -- Match not found: {match.artifact.purl}")

        return results

    def _convert_to_cyclone_dx(self, match: Match, original_purls: list[str]) -> Vulnerability:
        """Converts a match to a vulnerability."""
        related: GrypeVulnerability = next(
            (related_vuln for related_vuln in match.related_vulnerabilities if related_vuln.id.startswith("CVE")),
            (match.related_vulnerabilities[0] if match.related_vulnerabilities else match.vulnerability),
        )

        cyclone_vuln = Vulnerability(
            description=related.description,
            recommendation=(
                f"State: {match.vulnerability.fix.state} | Fix Versions: {','.join(match.vulnerability.fix.versions)}"
            ),
            source=get_vulnerability_source(related.id),
        )

        cyclone_vuln.id = related.id
        cyclone_vuln.ratings = []

        ids = [match.vulnerability.id, *[x.id for x in match.related_vulnerabilities]]

        # Maintain cyclone_vul.source or initialize to empty VulnerabilitySource
        cyclone_vuln.source = cyclone_vuln.source or cdx.VulnerabilitySource()
        cyclone_vuln.source.url = related.data_source
        cyclone_vuln.advisories = get_advisories_from_urls(related.urls)
        cyclone_vuln.references = get_references_from_ids(ids, cyclone_vuln.id)

        affected_purls = [purl for purl in original_purls if purl_check(match.artifact.purl, purl)]
        for purl in affected_purls:
            affect_dict: dict[str, Any] = {"ref": purl}
            if match.artifact.version is not None:
                affect_dict["versions"] = [{"version": match.artifact.version, "status": "affected"}]

            cyclone_vuln.affects.append(Affect.parse_obj(affect_dict))

        cvss_scores = match.vulnerability.cvss or related.cvss

        for cvss in cvss_scores:
            if cvss.version.startswith("3"):
                cvss3 = CVSS3(cvss.vector)
                method = "CVSSv31" if cvss.version == "3.1" else "CVSSv3"

                cyclone_vuln.ratings.append(
                    cdx.Rating(
                        score=float(cvss3.base_score or 0.0),
                        severity=cdx.Severity[cvss3.severities()[0].lower()],
                        method=cdx.ScoreMethod(method),
                        vector=cvss.vector,
                    )
                )
            elif cvss.version.startswith("2"):
                cvss2 = CVSS2(cvss.vector)

                cyclone_vuln.ratings.append(
                    cdx.Rating(
                        score=float(cvss2.base_score or 0.0),
                        severity=cdx.Severity[cvss2.severities()[0].lower()],
                        method=cdx.ScoreMethod.CVSSv2,
                        vector=cvss.vector,
                    )
                )

        if not cyclone_vuln.ratings and match.vulnerability.severity:
            cyclone_vuln.ratings.append(
                cdx.Rating(
                    severity=getattr(cdx.Severity, match.vulnerability.severity.lower(), cdx.Severity.INFO),
                    method=cdx.ScoreMethod.OTHER,
                )
            )

        cyclone_vuln.tools = self.scanner_tools()

        return cyclone_vuln

    @deprecated("GrypeScanner._convert_to_cyclone_dx_deprecated is deprecated, use GrypeScanner._convert_to_cyclone_dx")
    def _convert_to_cyclone_dx_deprecated(self, match: Match) -> Vulnerability:
        """Converts a match to a vulnerability."""
        related: GrypeVulnerability = next(
            (related_vuln for related_vuln in match.related_vulnerabilities if related_vuln.id.startswith("CVE")),
            (match.related_vulnerabilities[0] if match.related_vulnerabilities else match.vulnerability),
        )

        cyclone_vuln = Vulnerability(
            description=related.description,
            recommendation=(
                f"State: {match.vulnerability.fix.state} | Fix Versions: {','.join(match.vulnerability.fix.versions)}"
            ),
            source=get_vulnerability_source(related.id),
        )

        cyclone_vuln.id = related.id
        cyclone_vuln.ratings = []

        ids = [match.vulnerability.id, *[x.id for x in match.related_vulnerabilities]]

        # Maintain cyclone_vul.source or initialize to empty VulnerabilitySource
        cyclone_vuln.source = cyclone_vuln.source or cdx.VulnerabilitySource()
        cyclone_vuln.source.url = related.data_source
        cyclone_vuln.advisories = get_advisories_from_urls(related.urls)
        cyclone_vuln.references = get_references_from_ids(ids, cyclone_vuln.id)
        cvss_scores = match.vulnerability.cvss or related.cvss

        for cvss in cvss_scores:
            if cvss.version.startswith("3"):
                cvss3 = CVSS3(cvss.vector)
                method = "CVSSv31" if cvss.version == "3.1" else "CVSSv3"

                cyclone_vuln.ratings.append(
                    cdx.Rating(
                        score=cvss3.base_score,
                        severity=cdx.Severity[cvss3.severities()[0].lower()],
                        method=cdx.ScoreMethod(method),
                        vector=cvss.vector,
                    )
                )
            elif cvss.version.startswith("2"):
                cvss2 = CVSS2(cvss.vector)

                cyclone_vuln.ratings.append(
                    cdx.Rating(
                        score=cvss2.base_score,
                        severity=cdx.Severity[cvss2.severities()[0].lower()],
                        method=cdx.ScoreMethod.CVSSv2,
                        vector=cvss.vector,
                    )
                )

        if not cyclone_vuln.ratings and match.vulnerability.severity:
            cyclone_vuln.ratings.append(
                cdx.Rating(
                    severity=cdx.Severity[match.vulnerability.severity.lower()],
                    method=cdx.ScoreMethod.OTHER,
                )
            )

        cyclone_vuln.tools = self.scanner_tools()

        return cyclone_vuln
