"""Documents an assessment of impact and exploitability of vulnerabilities.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/enhancements/analysis_assessment.py
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

from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import rich

from hoppr import Affect, HopprLoadDataError, cdx, utils
from hoppr.utils import get_package_url
from typing_extensions import deprecated


if TYPE_CHECKING:
    from hoppr import Vulnerability
    from packageurl import PackageURL


class Analysis:
    """Documents an assessment of impact and exploitability."""

    enabled: bool = False
    assessments: ClassVar[list[Assessment]] = []
    _assessment_types: ClassVar[list[str]] = []
    _assessment_findings: ClassVar[list[str]] = []
    _assessment_descriptions: ClassVar[list[str]] = []

    class Assessment:
        assessment_date: date | None
        vulnerability: str | None
        state: str | None
        justification: str | None
        package: Package
        response: list[cdx.ResponseEnum] | None = None
        detail: str | None

        def __init__(self, assessment: dict):
            # Ref: https://cyclonedx.org/docs/1.5/json/#vulnerabilities_items_analysis
            valid_state: list[str] = [
                "resolved",
                "resolved_with_pedigree",
                "exploitable",
                "in_triage",
                "false_positive",
                "not_affected",
            ]
            valid_justification: list[str] = [
                "",
                "code_not_present",
                "code_not_reachable",
                "requires_configuration",
                "requires_dependency",
                "requires_environment",
                "protected_by_compiler",
                "protected_at_runtime",
                "protected_at_perimeter",
                "protected_by_mitigating_control",
            ]

            # Required Properties from analysis.assessment.yml
            self.assessment_date = assessment.get("assessmentDate")
            if not self.assessment_date:
                raise KeyError("assessments.assessmentDate must the date the assessment conducted.")

            self.vulnerability = assessment.get("vulnerability")
            if not self.vulnerability:
                raise KeyError("assessments.vulnerability must contain a vulnerability id")

            self.state = assessment.get("state")
            if self.state not in valid_state:
                raise KeyError(f"assessments.state must be one of {valid_state}")

            self.justification = assessment.get("justification") or ""
            if self.justification not in valid_justification:
                raise KeyError(f"assessments.justification must be one of {valid_justification[1:]}")

            if self.state in ["not_affected", "false_positive"] and not self.justification:
                # justification: required if state=not_affected or false_positive
                raise KeyError("assessments.justification is required when state=not_affected or false_positive")

            self.package = self.Package(assessment.get("package") or {})

            # Optional Properties
            if "response" in assessment:
                valid_response: list[str] = [
                    "can_not_fix",
                    "will_not_fix",
                    "update",
                    "rollback",
                    "workaround_available",
                ]
                if assessment.get("response") in valid_response:
                    self.response = [cdx.ResponseEnum(assessment.get("response"))]
                else:
                    raise KeyError(f"assessments.response must be one of {valid_response}")

            self.detail = assessment.get("detail") or ""
            if not self.detail and self.state not in ["exploitable", "in_triage"]:
                raise KeyError("assessments.detail must be set when state is not 'exploitable' or 'in_triage'")

        class Package:
            type: str | None
            name: str | None
            version: str | None

            def __init__(self, package: dict):
                valid_packages: list[str] = [
                    "cargo",
                    "composer",
                    "conan",
                    "deb",
                    "docker",
                    "gem",
                    "golang",
                    "gradle",
                    "maven",
                    "npm",
                    "nuget",
                    "oci",
                    "pypi",
                    "rpm",
                ]

                self.type = package.get("type")
                if self.type not in valid_packages:
                    raise KeyError(f"assessments.package.type must be one of {valid_packages}")

                self.name = package.get("name")
                if not self.name:
                    raise KeyError("assessments.package.name must contain a valid package name")

                self.version = package.get("version")
                if not self.version:
                    raise KeyError("assessments.package.version must contain a valid version")

    def _set_assessment_path(self, path: str | Path) -> bool:  # pragma: no cover
        """Sets the path to the analysis.assessment.yml file.

        Argument path can be relative or fully qualified path
        For example "./" will look for analysis.assessment.yml in the current directory
        """
        assessment_file_path: Path = Path(path) / "analysis.assessment.yml"

        # Clears lists if users are scanning multiple SBOMs
        self.assessments.clear()
        self._assessment_types.clear()
        self._assessment_findings.clear()
        self._assessment_descriptions.clear()

        if not assessment_file_path.exists():
            rich.print(f"Oops, analysis.assessment.yml doesn't exist in: {assessment_file_path.absolute()}")
            return False

        try:
            self.enabled = True
            assessment_dict = utils.load_file(assessment_file_path)
            if not isinstance(assessment_dict, dict):
                raise HopprLoadDataError("Pulled artifact data was not loaded as dictionary")
            for assessment in assessment_dict["assessments"]:
                assessment_obj = self.Assessment(assessment)
                if assessment_obj.package.type and assessment_obj.package.type not in self._assessment_types:
                    self._assessment_types.append(assessment_obj.package.type)
                self.assessments.append(assessment_obj)
            rich.print(f"Loaded: {assessment_file_path}")
        except KeyError as exc:
            raise KeyError(f"Invalid value specified in analysis.assessment.yml: {exc}") from None
        except Exception as exc:  # pylint: disable=broad-except
            rich.print(f"Failed to Load: {assessment_file_path}")
            rich.print(f"{self.__class__.__name__} generated an Assessment exception: {exc}")
            return False
        return True

    def apply_assessments(self, scanner_results: list[Vulnerability]):
        """Checks scanner results against analysis.assessment.yml.

        Returns a dictionary of vulnerabilities with related analysis assessment added if applicable.
        """
        for vuln in scanner_results:
            try:
                for assessment in self.assessments:
                    self._determine_assessment(assessment, vuln)

            except Exception as exc:  # pylint: disable=broad-except
                rich.print(
                    f"{vuln.id} and {assessment.package.type}/{assessment.package.name}:{assessment.package.version} generated an Assessment exception: {exc}"
                )

    def _requires_justification(self, state: str | None) -> bool:
        return state in [cdx.ImpactAnalysisState.NOT_AFFECTED.value, cdx.ImpactAnalysisState.FALSE_POSITIVE.value]

    def _determine_assessment(self, assessment_obj: Assessment, vuln: Vulnerability):
        """Determines if purl matches an assessment assertion. Documents analysis.

        Updates description. Description is reflected in enhanced json and html reports
        """
        if (
            not self._package_is_affected_by_vuln(assessment_obj.package, vuln.affects)
            or not vuln.ratings
            or assessment_obj.vulnerability != vuln.id
        ):
            return

        average_severity: str = self._get_average_severity(vuln.ratings)
        for rating in vuln.ratings:
            self._check_rating(assessment_obj, average_severity, vuln, rating)

        vuln.analysis = cdx.Analysis(
            state=cdx.ImpactAnalysisState(assessment_obj.state),
            justification=(
                cdx.ImpactAnalysisJustification(assessment_obj.justification)
                if assessment_obj.justification or self._requires_justification(assessment_obj.state)
                else None
            ),
            response=assessment_obj.response,
            detail=assessment_obj.detail,
            firstIssued=datetime.combine(assessment_obj.assessment_date or date.min, datetime.min.time()),
            lastUpdated=datetime.now(),
        )

        response_str = "" if assessment_obj.response is None else str(assessment_obj.response[0])
        description = f"<b class='font-medium'>Initial Severity:</b> {average_severity}<br><b class='font-medium'>Description</b>: VULN_DESCRIPTION<br><b class='font-medium'>Assessment of Impact:</b> {assessment_obj.assessment_date}<br><b class='font-medium'>State:</b> {assessment_obj.state}<br><b class='font-medium'>Justification:</b> {assessment_obj.justification}<br><b class='font-medium'>Response:</b> {response_str}<br><b class='font-medium'>Detail:</b> {assessment_obj.detail}<br><b class='font-medium'>Scan Date:</b> {datetime.now().strftime('%Y-%m-%d')}"
        desc_key = f"{vuln.id}:{description}"
        if desc_key not in self._assessment_descriptions:
            self._assessment_descriptions.append(desc_key)
            vuln.description = description.replace("VULN_DESCRIPTION", str(vuln.description))

    def _package_is_affected_by_vuln(self, assessment_package: Assessment.Package, affects: list[Affect]) -> bool:
        """Determines if the package from the assessment is in the affects list of a vulnerability.

        Returns a bool of whether the package is in the affects list.
        """
        return (
            len(
                [
                    purl
                    for purl in [get_package_url(affect.ref) for affect in affects]
                    if assessment_package.type == purl.type
                    and assessment_package.name == purl.name
                    and (assessment_package.version or "") == (purl.version or "")
                ]
            )
            > 0
        )

    @deprecated("Analysis.check_assessments is deprecated, use Analysis.apply_assessments")
    def check_assessments(
        self, scanner_results: dict[str, list[Vulnerability]], scanner_name: str
    ) -> dict[str, list[Vulnerability]]:
        """Checks scanner results against analysis.assessment.yml.

        Returns a dictionary of vulnerabilities with related analysis assessment added if applicable.
        """
        results: dict = {}
        scanner = scanner_name.lower().replace("scanner", "")
        for purl, vuln_list in scanner_results.items():
            try:
                purl_data = get_package_url(purl)
                if len(vuln_list) != 0 or purl_data.type in self._assessment_types:
                    for assessment in self.assessments:
                        self._check_assessment(purl_data, assessment, vuln_list)
                results[purl] = vuln_list

            except Exception as exc:  # pylint: disable=broad-except
                results[purl] = vuln_list
                rich.print(f"{scanner} generated an Assessment exception: {exc}")

        return results

    @deprecated("Analysis._check_assessment is deprecated, use Analysis._determine_assessment")
    def _check_assessment(self, purl_data: PackageURL, assessment_obj: Assessment, vuln_list: list[Vulnerability]):
        """Determines if purl matches an assessment assertion. Documents analysis.

        Updates description. Description is reflected in enhanced json and html reports
        """
        if assessment_obj.package.type != purl_data.type or assessment_obj.package.name != purl_data.name:
            return

        for vuln in vuln_list:
            average_severity: str = self._get_average_severity(vuln.ratings)
            if (
                vuln.ratings
                and assessment_obj.vulnerability == vuln.id
                and purl_data.version == assessment_obj.package.version
            ):
                for rating in vuln.ratings:
                    self._check_rating(assessment_obj, average_severity, vuln, rating)
                vuln.analysis = cdx.Analysis(
                    state=cdx.ImpactAnalysisState(assessment_obj.state),
                    justification=cdx.ImpactAnalysisJustification(assessment_obj.justification),
                    response=assessment_obj.response,
                    detail=assessment_obj.detail,
                    firstIssued=datetime.combine(assessment_obj.assessment_date or date.min, datetime.min.time()),
                    lastUpdated=datetime.now(),
                )
                response_str = "" if assessment_obj.response is None else str(assessment_obj.response[0])
                description = f"<b class='font-medium'>Initial Severity:</b> {average_severity}<br><b class='font-medium'>Description</b>: VULN_DESCRIPTION<br><b class='font-medium'>Assessment of Impact:</b> {assessment_obj.assessment_date}<br><b class='font-medium'>State:</b> {assessment_obj.state}<br><b class='font-medium'>Justification:</b> {assessment_obj.justification}<br><b class='font-medium'>Response:</b> {response_str}<br><b class='font-medium'>Detail:</b> {assessment_obj.detail}<br><b class='font-medium'>Scan Date:</b> {datetime.now().strftime('%Y-%m-%d')}"
                desc_key = f"{vuln.id}:{description}"
                if desc_key not in self._assessment_descriptions:
                    self._assessment_descriptions.append(desc_key)
                    vuln.description = description.replace("VULN_DESCRIPTION", str(vuln.description))

    def _check_rating(self, assessment_obj: Assessment, average_severity: str, vuln: Vulnerability, rating: cdx.Rating):
        """Determines if a rating adjustment is needed based on the analysis assessment.

        Documents rating adjustment if applicable.
        """
        adjusted_severity: cdx.Severity | None = None
        initial_severity = rating.severity

        if assessment_obj.state not in [] and average_severity not in ["info", "none", "unknown"]:
            rating.severity = cdx.Severity.low
            adjusted_severity = rating.severity

        assessment_message = f"[bold yellow]{vuln.id}[/bold yellow] severity:'INITIAL_SEVERITY' changed to 'NEW_SEVERITY' based Assessment of Impact state : {assessment_obj.state}. Ref: {assessment_obj.package.type}:{assessment_obj.package.name}:{assessment_obj.package.version} in analysis.assessment.yml"

        if assessment_message not in self._assessment_findings:
            self._assessment_findings.append(assessment_message)
            if average_severity == rating.severity:
                rich.print(
                    assessment_message.replace("INITIAL_SEVERITY", average_severity).replace(
                        "changed to 'NEW_SEVERITY'", "was not changed"
                    )
                )
            else:
                rich.print(
                    assessment_message.replace("INITIAL_SEVERITY", average_severity).replace(
                        "NEW_SEVERITY", str(rating.severity)
                    )
                )

        if adjusted_severity is not None:
            assessment_obj.detail = f"Severity of finding reduced from {initial_severity} to {adjusted_severity} due to analysis asserted by user in analysis.assessment.yml. Detail: {assessment_obj.detail}"
            if not rating.justification and assessment_obj.justification:
                rating.justification = assessment_obj.justification

    def _get_average_severity(self, ratings: list[cdx.Rating] | None) -> str:
        """Gets the average severity from the vuln.ratings.

        Returns str
        """
        severities = ["info", "low", "medium", "high", "critical"]

        if not isinstance(ratings, list):
            raise TypeError("Ratings was not passed as a list of Rating") from None
        indexes = [
            severities.index(str(rating.severity))
            for rating in ratings
            if rating.severity and str(rating.severity) in severities
        ]
        return severities[int(sum(indexes) / len(indexes))]
