# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, RootModel

from .analyzer_configurations import OrtAnalyzerConfigurations
from .package_managers import OrtPackageManagerConfigurations, PackageManagerConfigs


class OrtRepositoryConfigurationLicenseChoicesPackageLicenseChoiceLicenseChoice(BaseModel):
    given: str | None = None
    choice: str


class OrtRepositoryConfigurationLicenseChoicesPackageLicenseChoice(BaseModel):
    package_id: str
    license_choices: list[OrtRepositoryConfigurationLicenseChoicesPackageLicenseChoiceLicenseChoice]


class OrtRepositoryConfigurationLicenseChoices(BaseModel):
    package_license_choices: list[OrtRepositoryConfigurationLicenseChoicesPackageLicenseChoice] | None = None
    repository_license_choices: list[Any] | None = None


class OrtRepositoryConfigurationSnippetChoiceProvenance(BaseModel):
    url: str


class OrtRepositoryConfigurationSnippetChoiceChoiceGivenSourceLocation(BaseModel):
    path: str
    start_line: int
    end_line: int


class OrtRepositoryConfigurationSnippetChoiceChoiceGiven(BaseModel):
    source_location: OrtRepositoryConfigurationSnippetChoiceChoiceGivenSourceLocation | None = None


class IssueResolutionReason(Enum):
    build_tool_issue = "BUILD_TOOL_ISSUE"
    cant_fix_issue = "CANT_FIX_ISSUE"
    scanner_issue = "SCANNER_ISSUE"


class RuleViolationResolutionReason(Enum):
    cant_fix_exception = "CANT_FIX_EXCEPTION"
    dynamic_linkage_exception = "DYNAMIC_LINKAGE_EXCEPTION"
    example_of_exception = "EXAMPLE_OF_EXCEPTION"
    license_acquired_exception = "LICENSE_ACQUIRED_EXCEPTION"
    not_modified_exception = "NOT_MODIFIED_EXCEPTION"
    patent_grant_exception = "PATENT_GRANT_EXCEPTION"


class VulnerabilityResolutionReason(Enum):
    cant_fix_vulnerability = "CANT_FIX_VULNERABILITY"
    ineffective_vulnerability = "INEFFECTIVE_VULNERABILITY"
    invalid_match_vulnerability = "INVALID_MATCH_VULNERABILITY"
    mitigated_vulnerability = "MITIGATED_VULNERABILITY"
    not_a_vulnerability = "NOT_A_VULNERABILITY"
    will_not_fix_vulnerability = "WILL_NOT_FIX_VULNERABILITY"
    workaround_for_vulnerability = "WORKAROUND_FOR_VULNERABILITY"


class VcsMatcherVcsMatcher(BaseModel):
    path: str | None = None
    revision: str | None = None
    type: str
    url: str | None = None


class VcsMatcherVcsMatcher1(BaseModel):
    path: str | None = None
    revision: str | None = None
    type: str | None = None
    url: str


class VcsMatcherVcsMatcher2(BaseModel):
    path: str | None = None
    revision: str
    type: str | None = None
    url: str | None = None


class VcsMatcherVcsMatcher3(BaseModel):
    path: str
    revision: str | None = None
    type: str | None = None
    url: str | None = None


class VcsMatcher(
    RootModel[VcsMatcherVcsMatcher | VcsMatcherVcsMatcher1 | VcsMatcherVcsMatcher2 | VcsMatcherVcsMatcher3]
):
    root: VcsMatcherVcsMatcher | VcsMatcherVcsMatcher1 | VcsMatcherVcsMatcher2 | VcsMatcherVcsMatcher3


class Hash(BaseModel):
    value: str
    algorithm: str


class PackageConfigurationSchemaSourceCodeOrigin(Enum):
    vcs = "VCS"
    artifact = "ARTIFACT"


class PackageConfigurationSchemaLicenseFindingCurationReason(Enum):
    code = "CODE"
    data_of = "DATA_OF"
    documentation_of = "DOCUMENTATION_OF"
    incorrect = "INCORRECT"
    not_detected = "NOT_DETECTED"
    reference = "REFERENCE"


class LicenseFindingCurations(BaseModel):
    comment: str | None = None
    concluded_license: str
    detected_license: str | None = None
    line_count: int | None = None
    path: str
    reason: PackageConfigurationSchemaLicenseFindingCurationReason
    start_lines: int | str | None = None


class PathExcludeReason(Enum):
    build_tool_of = "BUILD_TOOL_OF"
    data_file_of = "DATA_FILE_OF"
    documentation_of = "DOCUMENTATION_OF"
    example_of = "EXAMPLE_OF"
    optional_component_of = "OPTIONAL_COMPONENT_OF"
    other = "OTHER"
    provided_by = "PROVIDED_BY"
    test_of = "TEST_OF"
    test_tool_of = "TEST_TOOL_OF"


VcsMatcherVcsMatcher4 = VcsMatcherVcsMatcher


VcsMatcherVcsMatcher5 = VcsMatcherVcsMatcher1


VcsMatcherVcsMatcher6 = VcsMatcherVcsMatcher2


VcsMatcherVcsMatcher7 = VcsMatcherVcsMatcher3


class VcsMatcherModel(
    RootModel[VcsMatcherVcsMatcher4 | VcsMatcherVcsMatcher5 | VcsMatcherVcsMatcher6 | VcsMatcherVcsMatcher7]
):
    root: VcsMatcherVcsMatcher4 | VcsMatcherVcsMatcher5 | VcsMatcherVcsMatcher6 | VcsMatcherVcsMatcher7


class PathIncludeReason(Enum):
    source_of = "SOURCE_OF"


class ScopeExcludeReason(Enum):
    build_dependency_of = "BUILD_DEPENDENCY_OF"
    dev_dependency_of = "DEV_DEPENDENCY_OF"
    documentation_dependency_of = "DOCUMENTATION_DEPENDENCY_OF"
    provided_dependency_of = "PROVIDED_DEPENDENCY_OF"
    test_dependency_of = "TEST_DEPENDENCY_OF"
    runtime_dependency_of = "RUNTIME_DEPENDENCY_OF"


class SnippetChoiceReason(Enum):
    no_relevant_finding = "NO_RELEVANT_FINDING"
    original_finding = "ORIGINAL_FINDING"
    other = "OTHER"


class OrtRepositoryConfigurationIncludesPath(BaseModel):
    pattern: str = Field(
        ...,
        description="A glob to match the path of the project definition file, relative to the root of the repository.",
    )
    reason: PathIncludeReason
    comment: str | None = None


class OrtRepositoryConfigurationIncludes(BaseModel):
    paths: list[OrtRepositoryConfigurationIncludesPath] | None = None


class OrtRepositoryConfigurationExcludesPath(BaseModel):
    pattern: str = Field(
        ...,
        description="A glob to match the path of the project definition file, relative to the root of the repository.",
    )
    reason: PathExcludeReason
    comment: str | None = None


class OrtRepositoryConfigurationExcludesScope(BaseModel):
    pattern: str
    reason: ScopeExcludeReason
    comment: str | None = None


class OrtRepositoryConfigurationExcludes(BaseModel):
    paths: list[OrtRepositoryConfigurationExcludesPath] | None = None
    scopes: list[OrtRepositoryConfigurationExcludesScope] | None = None


class OrtRepositoryConfigurationSnippetChoiceChoiceChoice(BaseModel):
    purl: str | None = None
    reason: SnippetChoiceReason
    comment: str | None = None


class OrtRepositoryConfigurationSnippetChoiceChoice(BaseModel):
    given: OrtRepositoryConfigurationSnippetChoiceChoiceGiven
    choice: OrtRepositoryConfigurationSnippetChoiceChoiceChoice


class OrtRepositoryConfigurationSnippetChoice(BaseModel):
    provenance: OrtRepositoryConfigurationSnippetChoiceProvenance
    choices: list[OrtRepositoryConfigurationSnippetChoiceChoice]


class PackageManagerConfigurationSchema(RootModel[dict[str, PackageManagerConfigs]]):
    root: dict[str, PackageManagerConfigs]


class ResolutionsSchemaResolutionsSchemaIssue(BaseModel):
    message: str
    reason: IssueResolutionReason
    comment: str | None = None


class ResolutionsSchemaResolutionsSchemaRuleViolation(BaseModel):
    message: str
    reason: RuleViolationResolutionReason
    comment: str | None = None


class ResolutionsSchemaResolutionsSchemaVulnerability(BaseModel):
    id: str
    reason: VulnerabilityResolutionReason
    comment: str | None = None


class ResolutionsSchemaResolutionsSchema(BaseModel):
    issues: list[ResolutionsSchemaResolutionsSchemaIssue]
    rule_violations: list[ResolutionsSchemaResolutionsSchemaRuleViolation] | None = None
    vulnerabilities: list[ResolutionsSchemaResolutionsSchemaVulnerability] | None = None


ResolutionsSchemaResolutionsSchema1Issue = ResolutionsSchemaResolutionsSchemaIssue


ResolutionsSchemaResolutionsSchema1RuleViolation = ResolutionsSchemaResolutionsSchemaRuleViolation


ResolutionsSchemaResolutionsSchema1Vulnerability = ResolutionsSchemaResolutionsSchemaVulnerability


class ResolutionsSchemaResolutionsSchema1(BaseModel):
    issues: list[ResolutionsSchemaResolutionsSchema1Issue] | None = None
    rule_violations: list[ResolutionsSchemaResolutionsSchema1RuleViolation]
    vulnerabilities: list[ResolutionsSchemaResolutionsSchema1Vulnerability] | None = None


ResolutionsSchemaResolutionsSchema2Issue = ResolutionsSchemaResolutionsSchemaIssue


ResolutionsSchemaResolutionsSchema2RuleViolation = ResolutionsSchemaResolutionsSchemaRuleViolation


ResolutionsSchemaResolutionsSchema2Vulnerability = ResolutionsSchemaResolutionsSchemaVulnerability


class ResolutionsSchemaResolutionsSchema2(BaseModel):
    issues: list[ResolutionsSchemaResolutionsSchema2Issue] | None = None
    rule_violations: list[ResolutionsSchemaResolutionsSchema2RuleViolation] | None = None
    vulnerabilities: list[ResolutionsSchemaResolutionsSchema2Vulnerability]


class ResolutionsSchema(
    RootModel[
        ResolutionsSchemaResolutionsSchema | ResolutionsSchemaResolutionsSchema1 | ResolutionsSchemaResolutionsSchema2
    ]
):
    root: (
        ResolutionsSchemaResolutionsSchema | ResolutionsSchemaResolutionsSchema1 | ResolutionsSchemaResolutionsSchema2
    ) = Field(
        ...,
        description="The OSS-Review-Toolkit (ORT) provides a possibility to resolve issues, rule violations and "
        "security vulnerabilities in a resolutions file. A full list of all available options can be found at "
        "https://oss-review-toolkit.org/ort/docs/configuration/resolutions.",
        title="ORT resolutions",
    )


class CurationsSchemaCurationsSchemaItemCurationsBinaryArtifact(BaseModel):
    url: str
    hash: Hash


CurationsSchemaCurationsSchemaItemCurationsSourceArtifact = CurationsSchemaCurationsSchemaItemCurationsBinaryArtifact


class CurationsSchemaCurationsSchemaItemCurations(BaseModel):
    comment: str | None = None
    authors: list[str] | None = None
    concluded_license: str | None = None
    cpe: str | None = None
    declared_license_mapping: dict[str, Any] | None = None
    description: str | None = None
    homepage_url: str | None = None
    purl: str | None = None
    binary_artifact: CurationsSchemaCurationsSchemaItemCurationsBinaryArtifact | None = None
    source_artifact: CurationsSchemaCurationsSchemaItemCurationsSourceArtifact | None = None
    vcs: VcsMatcher | None = None
    is_metadata_only: bool | None = None
    is_modified: bool | None = None


class CurationsSchemaCurationsSchemaItem(BaseModel):
    id: str
    curations: CurationsSchemaCurationsSchemaItemCurations


class CurationsSchema(RootModel[list[CurationsSchemaCurationsSchemaItem]]):
    root: list[CurationsSchemaCurationsSchemaItem] = Field(
        ...,
        description="The OSS-Review-Toolkit (ORT) provides a possibility to correct metadata and set "
        "the concluded license for specific packages (dependencies) in curation files. A full list of all available "
        "options can be found at https://oss-review-toolkit.org/ort/docs/configuration/package-curations.",
        title="ORT curations",
    )


class LicenseFindingCurationsModel(BaseModel):
    path: str
    start_lines: int | str | None = None
    line_count: int | None = None
    detected_license: str | None = None
    concluded_license: str
    reason: PackageConfigurationSchemaLicenseFindingCurationReason
    comment: str | None = None


class OrtRepositoryConfigurationCurations(BaseModel):
    license_findings: list[LicenseFindingCurationsModel]
    packages: CurationsSchema | None = None


class OrtRepositoryConfigurationCurations1(BaseModel):
    license_findings: list[LicenseFindingCurationsModel] | None = None
    packages: CurationsSchema


class OrtRepositoryConfiguration(BaseModel):
    """
    Represents the configuration for an OSS-Review-Toolkit (ORT) repository.

    This class defines various configuration options for analyzing, including, excluding,
    resolving, and curating artifacts in a repository. It also provides settings for package
    configurations, license choices, and snippet choices.

    Usage:
        Instantiate this class to specify repository-level configuration for ORT analysis.
        Each field corresponds to a specific aspect of the repository's configuration.
    """

    analyzer: OrtAnalyzerConfigurations | None = None
    includes: OrtRepositoryConfigurationIncludes | None = Field(
        None, description="Defines which parts of a repository should be included."
    )
    excludes: OrtRepositoryConfigurationExcludes | None = Field(
        None, description="Defines which parts of a repository should be excluded."
    )
    resolutions: ResolutionsSchema | None = None
    curations: OrtRepositoryConfigurationCurations | OrtRepositoryConfigurationCurations1 | None = Field(
        None, description="Curations for artifacts in a repository."
    )
    package_configurations: list[OrtPackageManagerConfigurations] | None = Field(
        None, description="A configuration for a specific package and provenance."
    )
    license_choices: OrtRepositoryConfigurationLicenseChoices | None = Field(
        None, description="A configuration to select a license from a multi-licensed package."
    )
    snippet_choices: list[OrtRepositoryConfigurationSnippetChoice] | None = Field(
        None, description="A configuration to select a snippet from a package with multiple snippet findings."
    )
