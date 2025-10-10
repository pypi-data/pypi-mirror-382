# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
#
# SPDX-License-Identifier: MIT


from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, RootModel


class IssueResolutionReason(Enum):
    BUILD_TOOL_ISSUE = "BUILD_TOOL_ISSUE"
    CANT_FIX_ISSUE = "CANT_FIX_ISSUE"
    SCANNER_ISSUE = "SCANNER_ISSUE"


class RuleViolationResolutionReason(Enum):
    CANT_FIX_EXCEPTION = "CANT_FIX_EXCEPTION"
    DYNAMIC_LINKAGE_EXCEPTION = "DYNAMIC_LINKAGE_EXCEPTION"
    EXAMPLE_OF_EXCEPTION = "EXAMPLE_OF_EXCEPTION"
    LICENSE_ACQUIRED_EXCEPTION = "LICENSE_ACQUIRED_EXCEPTION"
    NOT_MODIFIED_EXCEPTION = "NOT_MODIFIED_EXCEPTION"
    PATENT_GRANT_EXCEPTION = "PATENT_GRANT_EXCEPTION"


class VulnerabilityResolutionReason(Enum):
    CANT_FIX_VULNERABILITY = "CANT_FIX_VULNERABILITY"
    INEFFECTIVE_VULNERABILITY = "INEFFECTIVE_VULNERABILITY"
    INVALID_MATCH_VULNERABILITY = "INVALID_MATCH_VULNERABILITY"
    MITIGATED_VULNERABILITY = "MITIGATED_VULNERABILITY"
    NOT_A_VULNERABILITY = "NOT_A_VULNERABILITY"
    WILL_NOT_FIX_VULNERABILITY = "WILL_NOT_FIX_VULNERABILITY"
    WORKAROUND_FOR_VULNERABILITY = "WORKAROUND_FOR_VULNERABILITY"


class Issue(BaseModel):
    message: str
    reason: IssueResolutionReason
    comment: str | None = None


class RuleViolation(BaseModel):
    message: str
    reason: RuleViolationResolutionReason
    comment: str | None = None


class Vulnerability(BaseModel):
    id: str
    reason: VulnerabilityResolutionReason
    comment: str | None = None


class OrtResolutions1(BaseModel):
    """
    The OSS-Review-Toolkit (ORT) provides a possibility to resolve issues, rule violations and security
    vulnerabilities in a resolutions file. A full list of all available options can be found at
    https://oss-review-toolkit.org/ort/docs/configuration/resolutions.
    """

    issues: list[Issue]
    rule_violations: list[RuleViolation] | None = None
    vulnerabilities: list[Vulnerability] | None = None


class OrtResolutions2(BaseModel):
    """
    The OSS-Review-Toolkit (ORT) provides a possibility to resolve issues, rule violations and
    security vulnerabilities in a resolutions file. A full list of all available options can be
    found at https://oss-review-toolkit.org/ort/docs/configuration/resolutions.
    """

    issues: list[Issue] | None = None
    rule_violations: list[RuleViolation]
    vulnerabilities: list[Vulnerability] | None = None


class OrtResolutions3(BaseModel):
    """
    The OSS-Review-Toolkit (ORT) provides a possibility to resolve issues, rule violations and
    security vulnerabilities in a resolutions file. A full list of all available options can be
    found at https://oss-review-toolkit.org/ort/docs/configuration/resolutions.
    """

    issues: list[Issue] | None = None
    rule_violations: list[RuleViolation] | None = None
    vulnerabilities: list[Vulnerability]


class OrtResolutions(RootModel[OrtResolutions1 | OrtResolutions2 | OrtResolutions3]):
    root: Annotated[
        OrtResolutions1 | OrtResolutions2 | OrtResolutions3,
        Field(title="ORT resolutions"),
    ]
    """
    The OSS-Review-Toolkit (ORT) provides a possibility to resolve issues, rule violations and
    security vulnerabilities in a resolutions file. A full list of all available options can be
    found at https://oss-review-toolkit.org/ort/docs/configuration/resolutions.
    """
