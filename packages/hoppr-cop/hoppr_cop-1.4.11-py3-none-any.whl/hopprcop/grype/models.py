"""This file contains auto generated pydantic models for the grype json output.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/grype/models.py
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

from typing import Annotated, Any

from pydantic import BaseModel, Field


class GrypeBaseModel(BaseModel, allow_population_by_field_name=True): ...


class Metrics(GrypeBaseModel):
    base_score: Annotated[float | None, Field(alias="baseScore")] = None
    exploitability_score: Annotated[float | None, Field(alias="exploitabilityScore")] = None
    impact_score: Annotated[float | None, Field(alias="impactScore")] = None


class VendorMetadata(GrypeBaseModel):
    base_severity: str | None = None
    status: str | None = None


class Cvs(GrypeBaseModel):
    source: str | None = None
    type: str | None = None
    version: str
    vector: str
    metrics: Metrics | None = None
    vendor_metadata: Annotated[VendorMetadata | None, Field(alias="vendorMetadata")] = None


class Fix(GrypeBaseModel):
    versions: list[str] = []
    state: str = ""


class Vulnerability(GrypeBaseModel):
    id: str
    data_source: Annotated[str | None, Field(alias="dataSource")] = None
    namespace: str | None = None
    urls: list[str] = []
    description: str | None = None
    severity: str | None = None
    cvss: list[Cvs] = []
    fix: Fix = Fix()
    advisories: list | None = None


class Package(GrypeBaseModel):
    name: str | None = None
    version: str | None = None


class SearchedBy(GrypeBaseModel):
    language: str | None = None
    namespace: str | None = None
    package: Package | None = None


class Found(GrypeBaseModel):
    version_constraint: Annotated[str | None, Field(alias="versionConstraint")] = None
    vulnerability_id: Annotated[str | None, Field(alias="vulnerabilityID")] = None


class MatchDetail(GrypeBaseModel):
    type: str | None = None
    matcher: str | None = None
    searched_by: Annotated[SearchedBy | None, Field(alias="searchedBy")] = None
    found: Found | None = None


class Artifact(GrypeBaseModel):
    id: str | None = None
    name: str | None = None
    version: str | None = None
    type: str | None = None
    locations: list | None = None
    language: str | None = None
    licenses: list | None = None
    cpes: list | None = None
    purl: str
    upstreams: list | None = None


class Match(GrypeBaseModel):
    vulnerability: Vulnerability
    related_vulnerabilities: Annotated[list[Vulnerability], Field(alias="relatedVulnerabilities")]
    match_details: Annotated[list[MatchDetail] | None, Field(alias="matchDetails")] = None
    artifact: Artifact


class Source(GrypeBaseModel):
    type: str | None = None
    target: str | dict[str, Any] | None = None


class Distro(GrypeBaseModel):
    name: str | None = None
    version: str | None = None
    id_like: Annotated[list[str] | None, Field(alias="idLike")] = None


class Search(GrypeBaseModel):
    scope: str | None = None
    unindexed_archives: Annotated[bool | None, Field(alias="unindexed-archives")] = None
    indexed_archives: Annotated[bool | None, Field(alias="indexed-archives")] = None


class DatabaseConfig(GrypeBaseModel):
    cache_dir: Annotated[str | None, Field(alias="cache-dir")] = None
    update_url: Annotated[str | None, Field(alias="update-url")] = None
    ca_cert: Annotated[str | None, Field(alias="ca-cert")] = None
    auto_update: Annotated[bool | None, Field(alias="auto-update")] = None
    validate_by_hash_on_start: Annotated[bool | None, Field(alias="validate-by-hash-on-start")] = None
    validate_age: Annotated[bool | None, Field(alias="validate-age")] = None
    max_allowed_built_age: Annotated[int | None, Field(alias="max-allowed-built-age")] = None


class Maven(GrypeBaseModel):
    search_upstream_by_sha1: Annotated[bool | None, Field(alias="searchUpstreamBySha1")] = None
    base_url: Annotated[str | None, Field(alias="baseUrl")] = None


class ExternalSources(GrypeBaseModel):
    enable: bool | None = None
    maven: Maven | None = None


class LanguageConfigMatch(GrypeBaseModel):
    using_cpes: Annotated[bool | None, Field(alias="using-cpes")] = None
    always_use_cpe_for_stdlib: Annotated[bool | None, Field(alias="always-use-cpe-for-stdlib")] = None


class ConfigMatch(GrypeBaseModel):
    java: LanguageConfigMatch | None = None
    dotnet: LanguageConfigMatch | None = None
    golang: LanguageConfigMatch | None = None
    javascript: LanguageConfigMatch | None = None
    python: LanguageConfigMatch | None = None
    ruby: LanguageConfigMatch | None = None
    rust: LanguageConfigMatch | None = None
    stock: LanguageConfigMatch | None = None


class Dev(GrypeBaseModel):
    profile_cpu: Annotated[bool | None, Field(alias="profile-cpu")] = None
    profile_mem: Annotated[bool | None, Field(alias="profile-mem")] = None


class Registry(GrypeBaseModel):
    insecure_skip_tls_verify: Annotated[bool | None, Field(alias="insecure-skip-tls-verify")] = None
    insecure_use_http: Annotated[bool | None, Field(alias="insecure-use-http")] = None
    auth: list | None = None


class Log(GrypeBaseModel):
    structured: bool | None = None
    level: str | None = None
    file: str | None = None


class Configuration(GrypeBaseModel):
    config_path: Annotated[str | None, Field(alias="configPath")] = None
    verbosity: int | None = None
    output: list[str] = []
    file: str | None = None
    distro: str | None = None
    add_cpes_if_none: Annotated[bool | None, Field(alias="add-cpes-if-none")] = None
    output_template_file: Annotated[str | None, Field(alias="output-template-file")] = None
    quiet: bool | None = None
    check_for_app_update: Annotated[bool | None, Field(alias="check-for-app-update")] = None
    only_fixed: Annotated[bool | None, Field(alias="only-fixed")] = None
    only_notfixed: Annotated[bool | None, Field(alias="only-notfixed")] = None
    platform: str | None = None
    search: Search | None = None
    ignore: list | None = None
    exclude: list | None = None
    db: DatabaseConfig | None = None
    external_sources: Annotated[ExternalSources | None, Field(alias="externalSources")] = None
    match: ConfigMatch | None = None
    dev: Dev | None = None
    fail_on_severity: Annotated[str | None, Field(alias="fail-on-severity")] = None
    registry: Registry | None = None
    log: Log | None = None
    show_suppressed: Annotated[bool | None, Field(alias="show-suppressed")] = None
    by_cve: Annotated[bool | None, Field(alias="by-cve")] = None
    name: str | None = None
    default_image_pull_source: Annotated[str | None, Field(alias="default-image-pull-source")] = None


class Database(GrypeBaseModel):
    built: str | None = None
    schema_version: Annotated[int | None, Field(alias="schemaVersion")] = None
    location: str | None = None
    checksum: str | None = None
    error: None


class Descriptor(GrypeBaseModel):
    name: str | None = None
    version: str | None = None
    configuration: Configuration | None = None
    db: Database | None = None
    timestamp: str | None = None


class GrypeResult(GrypeBaseModel):
    matches: list[Match]
    source: Source | None = None
    distro: Distro | None = None
    descriptor: Descriptor | None = None
