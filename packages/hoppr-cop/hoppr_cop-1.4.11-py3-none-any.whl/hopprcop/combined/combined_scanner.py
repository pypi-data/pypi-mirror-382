"""A Vulnerability Scanner that combines results from all configured scanners.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/combined/combined_scanner.py
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

import concurrent.futures
import importlib
import warnings

from typing import TYPE_CHECKING, ClassVar, TypeVar, cast

import rich

from hoppr import Sbom, Vulnerability
from typing_extensions import deprecated

from hopprcop.enhancements.analysis_assessment import Analysis
from hopprcop.vulnerability_combiner import combine_vulnerabilities, merge_scanner_vulnerabilities
from hopprcop.vulnerability_scanner import VulnerabilitySuper


if TYPE_CHECKING:
    from collections.abc import Callable

    from packageurl import PackageURL

    from hopprcop.vulnerability_enhancer import BaseEnhancer


ScanResultT = TypeVar("ScanResultT", list[Vulnerability], bool)
ScanResultDeprecatedT = TypeVar("ScanResultDeprecatedT", dict[str, list[Vulnerability]], bool)


# Put here to ensure this is set no matter how it is run
def _showwarning(message: Warning | str, category: type[Warning], *_, **__):
    rich.print(f"[bold yellow]{category.__name__}: {message}")


# Override `warnings.showwarning` to print to console
warnings.showwarning = _showwarning
warnings.filterwarnings(action="once", category=DeprecationWarning)


class ScannerError(RuntimeError):
    """Error class that is thrown when an exception is encountered in a scanner."""


class CombinedScanner(VulnerabilitySuper, author="hoppr-cop", name="CombinedScanner"):
    """A Vulnerability Scanner that combines results from all configured scanners."""

    scanners: ClassVar[list[VulnerabilitySuper]] = []
    enhancers: ClassVar[list[BaseEnhancer]] = []
    assessment = Analysis()

    def set_scanners(self, scanners: list[VulnerabilitySuper] | list[str]):
        """Sets the scanners that should be used for vulnerability scanning.

        The argument can either be a list of scanner instances or a list of fully qualified strings to a scanner
        instance. For example ["vuln.gemnasium.gemnasium_scanner.GemnasiumScanner"].
        """
        for scanner in scanners:
            if isinstance(scanner, str):
                modname, _, clsname = scanner.rpartition(".")
                mod = importlib.import_module(modname)
                scanner = cast("VulnerabilitySuper", getattr(mod, clsname)())

            if scanner.should_activate():
                rich.print(f"{scanner.__class__.__name__} is activated")
                self.scanners.append(scanner)

    def set_enhancers(self, enhancers: list[BaseEnhancer]):
        """Sets the scanners that should be used for vulnerability scanning.

        Args:
            enhancers: Either a list of scanner instances or fully qualified scanner class name strings
        instance. For example ["vuln.gemnasium.gemnasium_scanner.GemnasiumScanner"].
        """
        self.enhancers.extend(enhancer for enhancer in enhancers if enhancer.should_activate())

    def _run_concurrently(self, function: Callable[[VulnerabilitySuper], ScanResultT]) -> dict[str, ScanResultT]:
        results: dict[str, ScanResultT] = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(function, scanner): scanner for scanner in self.scanners}

        for future in concurrent.futures.as_completed(futures):
            scanner = type(futures[future]).__name__
            try:
                result: ScanResultT = future.result()
                results[scanner] = result
            except Exception as exc:
                rich.print(f"{scanner} generated an exception: {exc}")
                raise ScannerError(exc) from exc

        return results

    @deprecated("CombinedScanner._run_concurrently_deprecated is deprecated, use CombinedScanner._run_concurrently")
    def _run_concurrently_deprecated(
        self, function: Callable[[VulnerabilitySuper], ScanResultDeprecatedT]
    ) -> list[ScanResultDeprecatedT]:
        results: list[ScanResultDeprecatedT] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(function, scanner): scanner for scanner in self.scanners}

        for future in concurrent.futures.as_completed(futures):
            try:
                result: ScanResultDeprecatedT = future.result()
                if self.assessment.enabled and not isinstance(result, bool):
                    results.append(self.assessment.check_assessments(result, type(future).__name__))
                else:
                    results.append(result)
            except Exception as exc:
                rich.print(f"{type(futures[future]).__name__} generated an exception: {exc}")
                raise exc

        return results

    def _apply_enhancements(self, vuln_list: list[Vulnerability]) -> list[Vulnerability]:
        if self.assessment.enabled:
            self.assessment.apply_assessments(vuln_list)

        for enhancer in self.enhancers:
            enhancer.enhance_vulnerabilities(vuln_list)

        return vuln_list

    def get_vulnerabilities_for_purl(self, purls: list[str]) -> list[Vulnerability]:  # pragma: no cover
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a list of CycloneDX vulnerabilities.
        """

        def submit_to_scanner_purl(scanner: VulnerabilitySuper) -> list[Vulnerability]:
            return scanner.get_vulnerabilities_for_purl(purls)

        vuln_map: dict[str, list[Vulnerability]] = self._run_concurrently(submit_to_scanner_purl)
        results: list[Vulnerability] = merge_scanner_vulnerabilities(vuln_map)
        return self._apply_enhancements(results)

    def get_vulnerabilities_for_sbom(self, bom: Sbom) -> list[Vulnerability]:  # pragma: no cover
        """Get the vulnerabilities for a CycloneDx compatible Software Bill of Materials (SBOM).

        Returns a list of CycloneDX vulnerabilities.
        """

        def submit_to_scanner(scanner: VulnerabilitySuper) -> list[Vulnerability]:
            return scanner.get_vulnerabilities_for_sbom(bom)

        vuln_map: dict[str, list[Vulnerability]] = self._run_concurrently(submit_to_scanner)
        results: list[Vulnerability] = merge_scanner_vulnerabilities(vuln_map)
        return self._apply_enhancements(results)

    @deprecated(
        "CombinedScanner.get_vulnerabilities_by_purl is deprecated, use CombinedScanner.get_vulnerabilities_for_purl"
    )
    def get_vulnerabilities_by_purl(
        self, purls: list[PackageURL]
    ) -> dict[str, list[Vulnerability]]:  # pragma: no cover
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """

        def submit_to_scanner_purl(scanner: VulnerabilitySuper) -> dict[str, list[Vulnerability]]:
            return scanner.get_vulnerabilities_by_purl(purls)

        results: list[dict[str, list[Vulnerability]]] = self._run_concurrently_deprecated(submit_to_scanner_purl)
        return combine_vulnerabilities(list(results))

    @deprecated(
        "CombinedScanner.get_vulnerabilities_by_sbom is deprecated, use CombinedScanner.get_vulnerabilities_for_sbom"
    )
    def get_vulnerabilities_by_sbom(self, bom: Sbom) -> dict[str, list[Vulnerability]]:  # pragma: no cover
        """Parse a CycloneDX compatible SBOM and return a list of vulnerabilities.

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """

        def submit_to_scanner(scanner: VulnerabilitySuper) -> dict[str, list[Vulnerability]]:
            return scanner.get_vulnerabilities_by_sbom(bom)

        results = self._run_concurrently_deprecated(submit_to_scanner)
        return combine_vulnerabilities(list(results))

    def get_vulnerability_dbs(self) -> bool:  # pragma: no cover
        """Load the vulnerability Databases for enabled scanners.

        Returns a boolean representation of success.
        """

        def submit_to_scanner(scanner: VulnerabilitySuper) -> bool:
            return scanner.get_vulnerability_db()

        results = self._run_concurrently(submit_to_scanner)
        return list(results.values()).count(False) == 0

    def set_assessment_path(self, path: str):  # pragma: no cover
        """Sets the path to the analysis.assessment.yml file.

        Argument path can be relative or fully qualified path
        For example "./" will look for analysis.assessment.yml in the current directory
        """
        self.assessment._set_assessment_path(path)
