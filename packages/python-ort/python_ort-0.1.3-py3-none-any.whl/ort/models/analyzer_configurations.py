# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from .package_managers import OrtPackageManagerConfigurations, OrtPackageManagers


class Sw360Configuration(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    rest_url: AnyUrl = Field(..., alias="restUrl")
    auth_url: AnyUrl = Field(..., alias="authUrl")
    username: str
    password: str | None = None
    client_id: str = Field(..., alias="clientId")
    client_password: str | None = Field(None, alias="clientPassword")
    token: str | None = None


class OrtAnalyzerConfigurations(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    allow_dynamic_versions: bool | None = Field(None, alias="allowDynamicVersions")
    enabled_package_managers: list[OrtPackageManagers] | None = Field(None, alias="enabledPackageManagers")
    disabled_package_managers: list[OrtPackageManagers] | None = Field(None, alias="disabledPackageManagers")
    package_managers: OrtPackageManagerConfigurations | None = Field(None, alias="packageManagers")
    sw360_configuration: Sw360Configuration | None = Field(None, alias="sw360Configuration")
    skip_excluded: bool | None = Field(None, alias="skipExcluded")
