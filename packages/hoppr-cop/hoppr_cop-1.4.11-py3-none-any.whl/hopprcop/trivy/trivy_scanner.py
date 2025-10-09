"""Scan an SBOM using the Trivy CLI.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/trivy/trivy_scanner.py
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
import json
import os
import sys
import tempfile

from pathlib import Path
from subprocess import PIPE, Popen
from typing import TYPE_CHECKING, ClassVar

import rich

from hoppr import Affect, Component, ComponentType, HopprError, Metadata, Sbom, Vulnerability
from hoppr.utils import get_package_url
from typing_extensions import deprecated

from hopprcop.utils import build_bom_dict_from_purls, purl_check, unsupported_purl_feedback
from hopprcop.vulnerability_scanner import VulnerabilitySuper


if TYPE_CHECKING:
    from packageurl import PackageURL


class TrivyScanner(VulnerabilitySuper, author="Aquasec", name="Trivy", offline_mode_supported=True):  # pragma: no cover
    """Interacts with the trivy cli to scan an SBOM."""

    # used to store the operating system component discovered in the provided SBOM for generating the SBOM for trivy
    _os_component: Component | None = None

    trivy_os_distro = None

    required_tools_on_path: ClassVar[list[str]] = ["trivy"]
    supported_types: ClassVar[list[str]] = [
        "cargo",
        "conan",
        "deb",
        "gem",
        "golang",
        "gradle",
        "maven",
        "npm",
        "nuget",
        "pypi",
        "rpm",
    ]

    def __init__(self, offline_mode: bool = False, trivy_os_distro: str | None = None):
        self.offline_mode = offline_mode
        self.trivy_os_distro = trivy_os_distro or os.getenv("OS_DISTRIBUTION", None)
        super().__init__()

    def get_vulnerability_db(self) -> bool:
        """Downloads vulnerability database.

        Returns a boolean representation of success.
        """
        success = False
        dbs = {"database": "--download-db-only", "java database": "--download-java-db-only"}
        for db, flag in dbs.items():
            args = ["trivy", "image", flag, "--no-progress"]
            with Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE) as process:
                # Trivy returns all messages as stderr in the 0.48.0 version.
                # To properly report the status of the database update the return code
                # is the primary check with scraping stderr being secondary.
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    if b"Downloading" in stderr:
                        rich.print(f"TrivyScanner: {db} downloaded")
                    else:
                        rich.print(f"TrivyScanner: No update needed for {db}")

                    success = True
                else:
                    rich.print(f"[yellow]TrivyScanner: Error occurred while updating the {db}[/]")
                    rich.print(f"[yellow]TrivyScanner: {stderr.decode()}[/]")
        return success

    def get_vulnerabilities_for_purl(self, purls: list[str]) -> list[Vulnerability]:
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a list of CycloneDX vulnerabilities.
        """
        bom = build_bom_dict_from_purls([get_package_url(purl) for purl in purls])
        self._add_operating_system_component(bom)

        return self.get_vulnerabilities_for_sbom(Sbom.parse_obj(bom))

    def get_vulnerabilities_for_sbom(self, bom: Sbom) -> list[Vulnerability]:
        """Get the vulnerabilities for a CycloneDx compatible Software Bill of Materials (SBOM).

        Returns a list of CycloneDX vulnerabilities.
        """
        # sourcery skip: low-code-quality
        # Need to give this method a through review in the future and potentially split complexity out
        results: list[Vulnerability] = []

        _win32 = sys.platform == "win32"
        with tempfile.NamedTemporaryFile(mode="w+", delete=not _win32, encoding="utf-8") as bom_file:
            # Remove tools from metadata due to cyclonedx-go only having partial support for spec version 1.5 (as of 0.72.0)
            # Add root component if it doesn't exist since trivy expects for this to be populated
            # TODO: roll back once full support is in cyclonedx-go
            copied_bom = bom.copy(deep=True)
            copied_bom.metadata = copied_bom.metadata or Metadata()
            copied_bom.metadata.tools = None
            copied_bom.metadata.component = copied_bom.metadata.component or Component(
                type=ComponentType.LIBRARY, name="trivycomponent"
            )

            # Trivy treats file type components as applications
            if copied_bom.metadata.component.type == ComponentType.FILE.value:
                copied_bom.metadata.component.type = ComponentType.APPLICATION

            bom_file.write(copied_bom.json())
            bom_file.flush()

            args = ["trivy", "sbom", "--scanners", "vuln", "--format", "cyclonedx", str(bom_file.name)]
            if self.offline_mode:
                args = [*args, "--skip-db-update", "--skip-java-db-update", "--offline-scan"]
            cache = os.getenv("CACHE_DIR")

            # Check for unsupported purl types and report if found
            purls = [component.purl for component in bom.components or [] if component.purl]
            unsupported_purl_feedback(
                self._scanner_name, self.supported_types, [get_package_url(purl) for purl in purls]
            )

            if cache is not None:
                args += ["--cache-dir", cache]

            with Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True) as process:
                stdout, stderr = process.communicate()
                if process.returncode != 0:
                    raise HopprError(f"{self.__class__.__name__} generated an exception: {stderr}")

                if _win32:
                    bom_file.close()
                    Path(bom_file.name).unlink()

            bom_dict = json.loads(stdout)
            purl_by_bom_ref: dict[str, str] = {}
            for component in bom_dict.get("components", []):
                # Component does not have bom_ref or purl, no need for lookup since it would fail
                with contextlib.suppress(KeyError):
                    purl_by_bom_ref[component["bom-ref"]] = component["purl"]

            for vulnerability_dict in bom_dict.get("vulnerabilities", []):
                vulnerability = Vulnerability.parse_obj(vulnerability_dict)
                vulnerability.tools = self.scanner_tools()
                affects: list[Affect] = []
                affects.extend(vulnerability.affects)
                vulnerability.affects = []
                for affect in affects:
                    trivy_purl: str | None = str(affect.ref)
                    if trivy_purl and not trivy_purl.startswith("pkg"):
                        trivy_purl = purl_by_bom_ref.get(affect.ref)
                    if trivy_purl is None:
                        rich.print(f"[yellow]Could not find purl for ref {affect.ref}!")
                    else:
                        for purl in purls:
                            if purl_check(trivy_purl, purl):
                                new_affect = Affect.parse_obj({"ref": purl, "versions": affect.versions})
                                vulnerability.affects.append(new_affect)

                if vulnerability.ratings is not None:
                    results.append(vulnerability)

        return results

    @deprecated("TrivyScanner.get_vulnerabilities_by_purl is deprecated, use TrivyScanner.get_vulnerabilities_for_purl")
    def get_vulnerabilities_by_purl(self, purls: list[PackageURL]) -> dict[str, list[Vulnerability]]:
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """
        bom = build_bom_dict_from_purls(purls)
        self._add_operating_system_component(bom)

        return self.get_vulnerabilities_by_sbom(Sbom.parse_obj(bom))

    @deprecated("TrivyScanner.get_vulnerabilities_by_sbom is deprecated, use TrivyScanner.get_vulnerabilities_for_sbom")
    def get_vulnerabilities_by_sbom(self, bom: Sbom) -> dict[str, list[Vulnerability]]:
        """Accepts a cyclone dx compatible SBOM and returns a list of vulnerabilities.

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """
        results: dict[str, list[Vulnerability]] = {}

        _win32 = sys.platform == "win32"
        with tempfile.NamedTemporaryFile(mode="w+", delete=not _win32, encoding="utf-8") as bom_file:
            # Remove tools from metadata due to cyclonedx-go only having partial support for spec version 1.5 (as of 0.72.0)
            # Add root component if it doesn't exist since trivy expects for this to be populated
            # TODO: roll back once full support is in cyclonedx-go
            copied_bom = bom.copy(deep=True)
            copied_bom.metadata = copied_bom.metadata or Metadata()
            copied_bom.metadata.tools = None
            copied_bom.metadata.component = copied_bom.metadata.component or Component(
                type=ComponentType.LIBRARY, name="trivycomponent"
            )

            bom_file.write(copied_bom.json())
            bom_file.flush()

            args = ["trivy", "sbom", "--scanners", "vuln", "--format", "cyclonedx", str(bom_file.name)]
            if self.offline_mode:
                args = [*args, "--skip-db-update", "--skip-java-db-update", "--offline-scan"]
            cache = os.getenv("CACHE_DIR")

            # Check for unsupported purl types and report if found
            purls = [get_package_url(component.purl) for component in bom.components or [] if component.purl]
            unsupported_purl_feedback(self._scanner_name, self.supported_types, purls)

            if cache is not None:
                args += ["--cache-dir", cache]

            with Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True) as process:
                stdout, stderr = process.communicate()
                if not stdout and stderr:
                    raise HopprError(f"{self.__class__.__name__} generated an exception: {stderr}")

                if _win32:
                    bom_file.close()
                    Path(bom_file.name).unlink()

            bom_dict = json.loads(stdout)

            for vuln_dict in bom_dict["vulnerabilities"]:
                vuln = Vulnerability.parse_obj(vuln_dict)
                for affect in vuln.affects:
                    *_, purl_str = str(affect.ref).split("#")
                    affect.ref = purl_str or affect.ref

                    if vuln.ratings is not None:
                        results.setdefault(affect.ref, [])
                        results[affect.ref].append(vuln)

                vuln.tools = self.scanner_tools()

        return results

    def _add_operating_system_component(self, bom: dict):
        version = None
        distro = None

        if self.trivy_os_distro is not None:
            parts = self.trivy_os_distro.split(":")

            if len(parts) != 2:
                rich.print(f"{self.trivy_os_distro} is an invalid distribution ")
            else:
                distro = parts[0]
                version = parts[1]
        elif self._os_component is not None:
            version = self._os_component.version
            distro = self._os_component.name

        if version is not None and distro is not None:
            component = {
                "bom-ref": "ab16d2bb-90f7-4049-96ce-8c473ba13bd2",
                "type": "operating-system",
                "name": distro,
                "version": version,
            }
            bom["components"].append(component)
