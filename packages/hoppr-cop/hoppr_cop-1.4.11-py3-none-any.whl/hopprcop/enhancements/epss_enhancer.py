"""A vulnerability enhancement that gets and sets an EPSS probability and percentile if applicable.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2024 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/enhancements/epss.py
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

from typing import TYPE_CHECKING

from hoppr import cdx

from hopprcop.enhancements.epss.models import EPSSResult
from hopprcop.utils import api_query
from hopprcop.vulnerability_enhancer import BaseEnhancer


if TYPE_CHECKING:
    from hoppr import Vulnerability


class EpssEnhancer(BaseEnhancer, offline_mode_supported=False):
    """Documents an assessment of impact and exploitability."""

    api_start: str = "https://api.first.org/data/v1/epss?cve="
    chunk_size = 100

    def __init__(self, offline_mode: bool = False, enabled: bool = False):
        self.offline_mode = offline_mode
        self.enabled = enabled

        super().__init__()

    def enhance_vulnerabilities(self, vuln_list: list[Vulnerability]):
        """Apply the EPSS score to a list of vulnerabilities."""
        data_results: dict[str, dict[str, str]] = {}
        id_list = [vuln.id for vuln in vuln_list if vuln.id]

        while id_list:
            chunk, id_list = id_list[: self.chunk_size], id_list[self.chunk_size :]
            self.query_epss_api(",".join(chunk), data_results)

        self.set_epss_score(vuln_list, data_results)

    def query_epss_api(self, query: str, data_results: dict[str, dict[str, str]]):
        """Query the EPSS api.

        Updates data_results with the epss score mapped to the cve id.
        """
        response = api_query(f"{self.api_start}{query}")

        if response.status_code == 200:
            epss_result = EPSSResult(**json.loads(response.content))
            for data in epss_result.data:
                data_results[data.cve] = {"epss": data.epss, "percentile": data.percentile}

    def set_epss_score(self, vuln_list: list[Vulnerability], data_results: dict[str, dict[str, str]]):
        """Set epss score for vulnerabilities.

        Returns a dictionary of vulnerabilities with epss score added if applicable.
        """
        for vuln in [vuln for vuln in vuln_list if vuln.id in data_results]:
            if vuln.id and (data := data_results.get(vuln.id)):
                vuln.ratings = vuln.ratings or []
                prob_rating = cdx.Rating(
                    score=float(data.get("epss", "")),
                    method=cdx.ScoreMethod.other,
                    source=cdx.VulnerabilitySource(name="EPSS-Probability", url=self.api_start + vuln.id),
                )
                percentile_rating = cdx.Rating(
                    score=float(data.get("percentile", "")),
                    method=cdx.ScoreMethod.other,
                    source=cdx.VulnerabilitySource(name="EPSS-Percentile", url=self.api_start + vuln.id),
                )
                vuln.ratings.append(prob_rating)
                vuln.ratings.append(percentile_rating)
