"""Setup hoppr-cop as a plugin for hoppr.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/hoppr_plugin/hopprcop_plugin.py
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

from pathlib import Path
from typing import TYPE_CHECKING, Final

from hoppr import BomAccess, HopprPlugin, Result, Vulnerability, hoppr_process

import hopprcop

from hopprcop.combined.combined_scanner import CombinedScanner
from hopprcop.reporting import Reporting
from hopprcop.reporting.models import ReportFormat


if TYPE_CHECKING:
    from hoppr import HopprContext


class HopprCopPlugin(HopprPlugin):
    """Hoppr plugin wrapper for hoppr-cop integration."""

    class ComponentVulnerabilityWrapper:
        """Wrapper for the vulnerabilities associated with a component."""

        def __init__(
            self,
            serial_number: str,
            version: int,
            vulnerabilities: list[Vulnerability] | None = None,
        ):
            self.serial_number = serial_number
            self.version = version
            self.vulnerabilities = vulnerabilities or []

    products: Final[list[str]] = ["generic/*", "generic/hopprcop-vulnerability-results-details/*"]  # type: ignore[misc]

    EMBEDDED_VEX: Final[str] = "embedded_cyclone_dx_vex"
    LINKED_VEX: Final[str] = "linked_cyclone_dx_vex"

    bom_access = BomAccess.FULL_ACCESS

    DEFAULT_SCANNERS: Final[list[str]] = [
        "hopprcop.gemnasium.gemnasium_scanner.GemnasiumScanner",
        "hopprcop.grype.grype_scanner.GrypeScanner",
        "hopprcop.trivy.trivy_scanner.TrivyScanner",
        "hopprcop.ossindex.oss_index_scanner.OSSIndexScanner",
    ]

    def __init__(self, context: HopprContext, config: dict | None = None) -> None:
        super().__init__(context, config)

        self.config = self.config or {}
        frmts: list[str] = self.config.get("result_formats", [self.EMBEDDED_VEX])
        self.formats: list[ReportFormat] = []

        # Correct format strings to bridge legacy naming and cli naming
        if self.EMBEDDED_VEX in frmts:
            self.formats.append(ReportFormat.CYCLONE_DX)
        if self.LINKED_VEX in frmts:
            self.formats.append(ReportFormat.LINKED_VEX)
        self.formats.extend(
            [ReportFormat[fmt.upper()] for fmt in frmts if fmt not in {self.LINKED_VEX, self.EMBEDDED_VEX}]
        )

        output_dir = Path(self.config.get("output_dir", self.context.collect_root_dir / "generic"))
        output_dir.mkdir(parents=True, exist_ok=True)

        self.reporting = Reporting(
            output_path=output_dir,
            base_name=self.config.get("base_report_name", "hopprcop-vulnerability-results"),
        )

        self.results: list[Vulnerability] = []

    def get_version(self) -> str:
        """__version__ required for all HopprPlugin implementations."""
        return hopprcop.__version__

    @hoppr_process
    def pre_stage_process(self) -> Result:
        """Supply SBOM to hoppr cop to perform vulnerabilty check."""
        self.get_logger().info("[ Executing hopprcop vulnerability check ]")

        parsed_bom = self.context.delivered_sbom

        combined_scanner = CombinedScanner()
        combined_scanner.set_scanners((self.config or {}).get("scanners", self.DEFAULT_SCANNERS))

        try:
            self.results = combined_scanner.get_vulnerabilities_for_sbom(parsed_bom)
        except Exception as exc:
            return Result.fail(message=str(exc))

        self.reporting.generate_vulnerability_reports(self.formats, self.results, parsed_bom)

        self.get_logger().flush()

        return Result.success(return_obj=parsed_bom)
