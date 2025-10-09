"""Gitlab dependency scanning data model."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Extra, Field


class Message(BaseModel):
    """Communication intended for the initiator of a scan."""

    level: Annotated[
        Literal["info", "warn", "fatal"],
        Field(
            description=(
                "Describes the severity of the communication. Use info to communicate"
                " normal scan behaviour; warn to communicate a potentially recoverable"
                " problem, or a partial error; fatal to communicate an issue that"
                " causes the scan to halt."
            ),
            examples=["info"],
        ),
    ]
    value: Annotated[
        str,
        Field(
            description="The message to communicate.",
            examples=["Permission denied, scanning aborted"],
            min_length=1,
        ),
    ]


class Option(BaseModel):
    """A configuration option used for this scan."""

    name: Annotated[
        str,
        Field(
            description="The configuration option name.",
            examples=[
                "DAST_FF_ENABLE_BAS",
                "DOCKER_TLS_CERTDIR",
                "DS_MAX_DEPTH",
                "SECURE_LOG_LEVEL",
            ],
            max_length=255,
            min_length=1,
        ),
    ]
    source: Annotated[
        Literal["argument", "file", "env_variable", "other"] | None,
        Field(description="The source of this option."),
    ] = None
    value: Annotated[
        bool | int | str | None,
        Field(
            description="The value used for this scan.",
            examples=[True, 2, None, "fatal", ""],
        ),
    ]


class Vendor(BaseModel):
    """The vendor/maintainer of the analyzer."""

    name: Annotated[
        str,
        Field(description="The name of the vendor.", examples=["GitLab"], min_length=1),
    ]


class Analyzer(BaseModel):
    """Object defining the analyzer used to perform the scan. Analyzers typically delegate to an underlying scanner to run the scan."""

    id: Annotated[
        str,
        Field(
            description="Unique id that identifies the analyzer.",
            examples=["gitlab-dast"],
            min_length=1,
        ),
    ]
    name: Annotated[
        str,
        Field(
            description=("A human readable value that identifies the analyzer, not required to be unique."),
            examples=["GitLab DAST"],
            min_length=1,
        ),
    ]
    url: Annotated[
        str | None,
        Field(
            description="A link to more information about the analyzer.",
            examples=["https://docs.gitlab.com/ee/user/application_security/dast"],
            regex="^https?://.+",
        ),
    ] = None
    vendor: Annotated[Vendor, Field(description="The vendor/maintainer of the analyzer.")]
    version: Annotated[
        str,
        Field(description="The version of the analyzer.", examples=["1.0.2"], min_length=1),
    ]


class Scanner(BaseModel):
    """Object defining the scanner used to perform the scan."""

    id: Annotated[
        str,
        Field(
            description="Unique id that identifies the scanner.",
            examples=["my-sast-scanner"],
            min_length=1,
        ),
    ]
    name: Annotated[
        str,
        Field(
            description=("A human readable value that identifies the scanner, not required to be unique."),
            examples=["My SAST Scanner"],
            min_length=1,
        ),
    ]
    url: Annotated[
        str | None,
        Field(
            description="A link to more information about the scanner.",
            examples=["https://scanner.url"],
        ),
    ] = None
    version: Annotated[
        str,
        Field(description="The version of the scanner.", examples=["1.0.2"], min_length=1),
    ]
    vendor: Annotated[Vendor, Field(description="The vendor/maintainer of the scanner.")]


class PrimaryIdentifier(BaseModel):
    """Primary ID model for Gitlab Dependency Scanning."""

    type: Annotated[
        str,
        Field(
            description=("for example, cve, cwe, osvdb, usn, or an analyzer-dependent type such as gemnasium)."),
            min_length=1,
        ),
    ]
    name: Annotated[str, Field(description="Human-readable name of the identifier.", min_length=1)]
    url: Annotated[
        str | None,
        Field(
            description="URL of the identifier's documentation.",
            regex="^(https?|ftp)://.+",
        ),
    ] = None
    value: Annotated[
        str,
        Field(description="Value of the identifier, for matching purpose.", min_length=1),
    ]


class Scan(BaseModel):
    """Scan model for Gitlab Dependency Scanning."""

    end_time: Annotated[
        str,
        Field(
            description=("ISO8601 UTC value with format yyyy-mm-ddThh:mm:ss, representing when the scan finished."),
            examples=["2020-01-28T03:26:02"],
            regex="^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$",
        ),
    ]
    messages: list[Message] | None = None
    options: list[Option] | None = None
    analyzer: Annotated[
        Analyzer,
        Field(
            description=(
                "Object defining the analyzer used to perform the scan. Analyzers"
                " typically delegate to an underlying scanner to run the scan."
            )
        ),
    ]
    scanner: Annotated[
        Scanner,
        Field(description="Object defining the scanner used to perform the scan."),
    ]
    start_time: Annotated[
        str,
        Field(
            description=("ISO8601 UTC value with format yyyy-mm-ddThh:mm:ss, representing when the scan started."),
            examples=["2020-02-14T16:01:59"],
            regex="^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$",
        ),
    ]
    status: Annotated[Literal["success", "failure"], Field(description="Result of the scan.")]
    type: Annotated[Literal["dependency_scanning"], Field(description="Type of the scan.")]
    primary_identifiers: Annotated[
        list[PrimaryIdentifier] | None,
        Field(
            description=(
                "An unordered array containing an exhaustive list of primary"
                " identifiers for which the analyzer may return results"
            )
        ),
    ] = None


class Identifier(BaseModel):
    """Identifier model for Gitlab Dependency Scanning."""

    type: Annotated[
        str,
        Field(
            description=("for example, cve, cwe, osvdb, usn, or an analyzer-dependent type such as gemnasium)."),
            min_length=1,
        ),
    ]
    name: Annotated[str, Field(description="Human-readable name of the identifier.", min_length=1)]
    url: Annotated[
        str | None,
        Field(
            description="URL of the identifier's documentation.",
            regex="^(https?|ftp)://.+",
        ),
    ] = None
    value: Annotated[
        str,
        Field(description="Value of the identifier, for matching purpose.", min_length=1),
    ]


class CvssVectors(BaseModel):
    """CVSS Vectors model for Gitlab Dependency Scanning."""

    vendor: Annotated[str | None, Field(min_length=1)] = "unknown"
    vector: Annotated[
        str,
        Field(
            max_length=128,
            min_length=16,
            regex="^((AV:[NAL]|AC:[LMH]|Au:[MSN]|[CIA]:[NPC]|E:(U|POC|F|H|ND)|RL:(OF|TF|W|U|ND)|RC:(UC|UR|C|ND)|CDP:(N|L|LM|MH|H|ND)|TD:(N|L|M|H|ND)|[CIA]R:(L|M|H|ND))/)*(AV:[NAL]|AC:[LMH]|Au:[MSN]|[CIA]:[NPC]|E:(U|POC|F|H|ND)|RL:(OF|TF|W|U|ND)|RC:(UC|UR|C|ND)|CDP:(N|L|LM|MH|H|ND)|TD:(N|L|M|H|ND)|[CIA]R:(L|M|H|ND))$",
        ),
    ]


class CvssVectors3x(BaseModel):
    """Alternate CVSS Vectors model for Gitlab Dependency Scanning."""

    vendor: Annotated[str | None, Field(min_length=1)] = "unknown"
    vector: Annotated[
        str,
        Field(
            max_length=128,
            min_length=32,
            regex="^CVSS:3[.][01]/((AV:[NALP]|AC:[LH]|PR:[NLH]|UI:[NR]|S:[UC]|[CIA]:[NLH]|E:[XUPFH]|RL:[XOTWU]|RC:[XURC]|[CIA]R:[XLMH]|MAV:[XNALP]|MAC:[XLH]|MPR:[XNLH]|MUI:[XNR]|MS:[XUC]|M[CIA]:[XNLH])/)*(AV:[NALP]|AC:[LH]|PR:[NLH]|UI:[NR]|S:[UC]|[CIA]:[NLH]|E:[XUPFH]|RL:[XOTWU]|RC:[XURC]|[CIA]R:[XLMH]|MAV:[XNALP]|MAC:[XLH]|MPR:[XNLH]|MUI:[XNR]|MS:[XUC]|M[CIA]:[XNLH])$",
        ),
    ]


class Link(BaseModel):
    """Link model for Gitlab Dependency Scanning."""

    name: Annotated[str | None, Field(description="Name of the vulnerability details link.")] = None
    url: Annotated[
        str,
        Field(
            description="URL of the vulnerability details document.",
            regex="^(https?|ftp)://.+",
        ),
    ]


class Signature(BaseModel):
    """A calculated tracking signature value and metadata."""

    algorithm: Annotated[str, Field(description="The algorithm used to generate the signature.")]
    value: Annotated[str, Field(description="The result of this signature algorithm.")]


class Item(BaseModel):
    """An item that should be tracked using source-specific tracking methods."""

    file: Annotated[
        str | None,
        Field(description="Path to the file where the vulnerability is located."),
    ] = None
    start_line: Annotated[
        float | None,
        Field(description="The first line of the file that includes the vulnerability."),
    ] = None
    end_line: Annotated[
        float | None,
        Field(description="The last line of the file that includes the vulnerability."),
    ] = None
    signatures: Annotated[
        list[Signature],
        Field(
            description=("An array of calculated tracking signatures for this tracking item."),
            min_items=1,
        ),
    ]


class Tracking(BaseModel):
    """Declares that a series of items should be tracked using source-specific tracking methods."""

    type: Annotated[
        str | None,
        Field(description="Each tracking type must declare its own type."),
    ] = None
    items: list[Item]


class Flag(BaseModel):
    """Informational flags identified and assigned to a vulnerability."""

    type: Annotated[
        Literal["flagged-as-likely-false-positive"],
        Field(description="Result of the scan."),
    ]
    origin: Annotated[str, Field(description="Tool that issued the flag.", min_length=1)]
    description: Annotated[str, Field(description="What the flag is about.", min_length=1)]


class Package(BaseModel):
    """Provides information on the package where the vulnerability is located."""

    name: Annotated[
        str,
        Field(description="Name of the package where the vulnerability is located."),
    ]


class DependencyPath(BaseModel):
    """Dependency Path model for Gitlab Dependency Scanning."""

    iid: Annotated[
        float,
        Field(description=("ID that is unique in the scope of a parent object, and specific to the resource type.")),
    ]


class Dependency(BaseModel):
    """Describes the dependency of a project where the vulnerability is located."""

    package: Annotated[
        Package,
        Field(description=("Provides information on the package where the vulnerability is located.")),
    ]
    version: Annotated[str, Field(description="Version of the vulnerable package.")]
    iid: Annotated[
        float | None,
        Field(description=("ID that identifies the dependency in the scope of a dependency file.")),
    ] = None
    direct: Annotated[
        bool | None,
        Field(description=("Tells whether this is a direct, top-level dependency of the scanned project.")),
    ] = None
    dependency_path: Annotated[
        list[DependencyPath] | None,
        Field(
            description=(
                "Ancestors of the dependency, starting from a direct project"
                " dependency, and ending with an immediate parent of the dependency."
                " The dependency itself is excluded from the path. Direct dependencies"
                " have no path."
            )
        ),
    ] = None


class Location(BaseModel):
    """Identifies the vulnerability's location."""

    file: Annotated[
        str,
        Field(
            description=("Path to the manifest or lock file where the dependency is declared (such as yarn.lock)."),
            min_length=1,
        ),
    ]
    dependency: Annotated[
        Dependency,
        Field(description=("Describes the dependency of a project where the vulnerability is located.")),
    ]


class Fix(BaseModel):
    """Fix model for Gitlab Dependency Scanning."""

    id: Annotated[
        str,
        Field(
            description=("Unique identifier of the vulnerability. This is recommended to be a UUID."),
            examples=["642735a5-1425-428d-8d4e-3c854885a3c9"],
            min_length=1,
        ),
    ]


class Remediation(BaseModel):
    """Remediation model for Gitlab Dependency Scanning."""

    fixes: Annotated[
        list[Fix],
        Field(
            description=("An array of strings that represent references to vulnerabilities fixed by this remediation.")
        ),
    ]
    summary: Annotated[
        str,
        Field(
            description="An overview of how the vulnerabilities were fixed.",
            min_length=1,
        ),
    ]
    diff: Annotated[
        str,
        Field(
            description=("A base64-encoded remediation code diff, compatible with git apply."),
            min_length=1,
        ),
    ]


class DependencyFile(BaseModel):
    """Depnedency File model for Gitlab Dependency Scanning."""

    path: Annotated[str, Field(min_length=1)]
    package_manager: Annotated[str, Field(min_length=1)]
    dependencies: list[Dependency]


class NamedField(BaseModel):
    """Named Field model for Gitlab Dependency Scanning."""

    name: str
    description: str | None = None


class Text(BaseModel):
    """Raw text."""

    type: Literal["text"] = "text"
    value: str


class Url(BaseModel):
    """A single URL."""

    type: Literal["url"] = "url"
    text: str | None = None
    href: Annotated[str, Field(examples=["http://mysite.com"], min_length=1)]


class Code(BaseModel):
    """A codeblock."""

    type: Literal["code"] = "code"
    value: str
    lang: Annotated[str | None, Field(description="A programming language")] = None


class Value(BaseModel):
    """A field that can store a range of types of value."""

    type: Literal["value"] = "value"
    value: float | str | bool


class Diff(BaseModel):
    """A diff."""

    type: Literal["diff"] = "diff"
    before: str
    after: str


class Markdown(BaseModel):
    """GitLab flavoured markdown, see https://docs.gitlab.com/ee/user/markdown.html."""

    type: Literal["markdown"] = "markdown"
    value: Annotated[
        str,
        Field(
            examples=[
                "Here is markdown `inline code` #1 [test](gitlab.com)\n\n![GitLab"
                " Logo](https://about.gitlab.com/images/press/logo/preview/gitlab-logo-white-preview.png)"
            ]
        ),
    ]


class Commit(BaseModel):
    """A commit/tag/branch within the GitLab project."""

    type: Literal["commit"] = "commit"
    value: Annotated[str, Field(description="The commit SHA", min_length=1)]


class FileLocation(BaseModel):
    """A location within a file in the project."""

    type: Literal["file-location"] = "file-location"
    file_name: Annotated[str, Field(min_length=1)]
    line_start: int
    line_end: int | None = None


class ModuleLocation(BaseModel):
    """A location within a binary module of the form module+relative_offset."""

    type: Literal["module-location"] = "module-location"
    module_name: Annotated[str, Field(examples=["compiled_binary"], min_length=1)]
    offset: Annotated[int, Field(examples=[100])]


class Vulnerability(BaseModel):
    """Describes the vulnerability using GitLab Flavored Markdown."""

    id: Annotated[
        str,
        Field(
            description=("Unique identifier of the vulnerability. This is recommended to be a UUID."),
            examples=["642735a5-1425-428d-8d4e-3c854885a3c9"],
            min_length=1,
        ),
    ]
    name: Annotated[
        str | None,
        Field(
            description=("The name of the vulnerability. This must not include the finding's specific information."),
            max_length=255,
        ),
    ] = None
    description: Annotated[
        str | None,
        Field(
            description="A long text section describing the vulnerability more fully.",
            max_length=1048576,
        ),
    ] = None
    severity: Annotated[
        Literal["Info", "Unknown", "Low", "Medium", "High", "Critical"] | None,
        Field(
            description=(
                "How much the vulnerability impacts the software. Possible values are"
                " Info, Unknown, Low, Medium, High, or Critical. Note that some"
                " analyzers may not report all these possible values."
            )
        ),
    ] = None
    solution: Annotated[
        str | None,
        Field(description="Explanation of how to fix the vulnerability.", max_length=7000),
    ] = None
    identifiers: Annotated[
        list[Identifier],
        Field(
            description=(
                "An ordered array of references that identify a vulnerability on"
                " internal or external databases. The first identifier is the Primary"
                " Identifier, which has special meaning."
            ),
            min_items=1,
        ),
    ]
    cvss_vectors: Annotated[
        list[CvssVectors | CvssVectors3x] | None,
        Field(
            description=(
                "An ordered array of CVSS vectors, each issued by a vendor to rate the"
                " vulnerability. The first item in the array is used as the primary"
                " CVSS vector, and is used to filter and sort the vulnerability."
            ),
            max_items=10,
            min_items=1,
        ),
    ] = None
    links: Annotated[
        list[Link] | None,
        Field(
            description=(
                "An array of references to external documentation or articles that describe the vulnerability."
            )
        ),
    ] = None
    details: NamedFieldMapping | None = None
    tracking: Annotated[
        Tracking | None,
        Field(description=("Describes how this vulnerability should be tracked as the project changes.")),
    ] = None
    flags: Annotated[
        list[Flag] | None,
        Field(description="Flags that can be attached to vulnerabilities."),
    ] = None
    location: Annotated[Location, Field(description="Identifies the vulnerability's location.")]


class ReportFormatForGitlabDependencyScanning(BaseModel):
    """This schema provides the the report format for Dependency Scanning analyzers (https://docs.gitlab.com/ee/user/application_security/dependency_scanning)."""

    class Config:
        extra = Extra.allow

    scan: Scan
    schema_: Annotated[
        str | None,
        Field(
            alias="schema",
            description="URI pointing to the validating security report schema.",
            regex="^https?://.+",
        ),
    ] = None
    version: Annotated[
        str,
        Field(
            description="The version of the schema to which the JSON report conforms.",
            regex="^[0-9]+\\.[0-9]+\\.[0-9]+$",
        ),
    ]
    vulnerabilities: Annotated[list[Vulnerability], Field(description="Array of vulnerability objects.")]
    remediations: Annotated[
        list[Remediation] | None,
        Field(
            description=(
                "An array of objects containing information on available remediations, along with patch diffs to apply."
            )
        ),
    ] = None
    dependency_files: Annotated[
        list[DependencyFile],
        Field(description="List of dependency files identified in the project."),
    ]


class NamedList(BaseModel):
    """An object with named and typed fields."""

    type: Literal["named-list"] = "named-list"
    items: NamedFieldMapping | None = None


class ListModel(BaseModel):
    """A list of typed fields."""

    type: Literal["list"] = "list"
    items: list[DetailType]


class Table(BaseModel):
    """A table of typed fields."""

    type: Literal["table"] = "table"
    header: list[DetailType] | None = None
    rows: list[list[DetailType]]


class NamedFieldNamedListItem(NamedField, NamedList):
    """A combination model of NamedField and NamedList to support the definition of named_list/properties/items."""


class NamedFieldListItem(NamedField, ListModel):
    """A combination model of NamedField and ListModel to support the definition of named_list/properties/items."""


class NamedFieldTableItem(NamedField, Table):
    """A combination model of NamedField and Table to support the definition of named_list/properties/items."""


class NamedFieldTextItem(NamedField, Text):
    """A combination model of NamedField and Text to support the definition of named_list/properties/items."""


class NamedFieldUrlItem(NamedField, Url):
    """A combination model of NamedField and Url to support the definition of named_list/properties/items."""


class NamedFieldCodeItem(NamedField, Code):
    """A combination model of NamedField and Code to support the definition of named_list/properties/items."""


class NamedFieldValueItem(NamedField, Value):
    """A combination model of NamedField and Value to support the definition of named_list/properties/items."""


class NamedFieldDiffItem(NamedField, Diff):
    """A combination model of NamedField and Diff to support the definition of named_list/properties/items."""


class NamedFieldMarkdownItem(NamedField, Markdown):
    """A combination model of NamedField and Markdown to support the definition of named_list/properties/items."""


class NamedFieldCommitItem(NamedField, Commit):
    """A combination model of NamedField and Commit to support the definition of named_list/properties/items."""


class NamedFieldFileLocationItem(NamedField, FileLocation):
    """A combination model of NamedField and FileLocation to support the definition of named_list/properties/items."""


class NamedFieldModuleLocationItem(NamedField, ModuleLocation):
    """A combination model of NamedField and ModuleLocation to support the definition of named_list/properties/items."""


DetailType = Annotated[
    NamedList
    | ListModel
    | Table
    | Text
    | Url
    | Code
    | Value
    | Diff
    | Markdown
    | Commit
    | FileLocation
    | ModuleLocation,
    Field(discriminator="type"),
]

NamedFieldMapping = Annotated[
    dict[
        str,
        NamedFieldListItem
        | NamedFieldTableItem
        | NamedFieldTextItem
        | NamedFieldUrlItem
        | NamedFieldCodeItem
        | NamedFieldValueItem
        | NamedFieldDiffItem
        | NamedFieldMarkdownItem
        | NamedFieldCommitItem
        | NamedFieldFileLocationItem
        | NamedFieldModuleLocationItem,
    ],
    Field(default={}),
]

Vulnerability.update_forward_refs()
NamedList.update_forward_refs()
NamedField.update_forward_refs()
NamedFieldNamedListItem.update_forward_refs()
NamedFieldListItem.update_forward_refs()
NamedFieldTableItem.update_forward_refs()
NamedFieldTextItem.update_forward_refs()
NamedFieldUrlItem.update_forward_refs()
NamedFieldCodeItem.update_forward_refs()
NamedFieldValueItem.update_forward_refs()
NamedFieldDiffItem.update_forward_refs()
NamedFieldMarkdownItem.update_forward_refs()
NamedFieldCommitItem.update_forward_refs()
NamedFieldFileLocationItem.update_forward_refs()
NamedFieldModuleLocationItem.update_forward_refs()
