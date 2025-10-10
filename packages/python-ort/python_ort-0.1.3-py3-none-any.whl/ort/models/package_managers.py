# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class OrtPackageManagers(Enum):
    """
    Enumeration of supported package managers in ORT.

    This enum represents a variety of package managers across different programming ecosystems.
    """

    bazel = "Bazel"
    bower = "Bower"
    bundler = "Bundler"
    cargo = "Cargo"
    carthage = "Carthage"
    cocoa_pods = "CocoaPods"
    composer = "Composer"
    conan = "Conan"
    go_mod = "GoMod"
    gradle = "Gradle"
    gradle_inspector = "GradleInspector"
    maven = "Maven"
    npm = "NPM"
    nu_get = "NuGet"
    pip = "PIP"
    pipenv = "Pipenv"
    pnpm = "PNPM"
    poetry = "Poetry"
    pub = "Pub"
    sbt = "SBT"
    spdx_document_file = "SpdxDocumentFile"
    stack = "Stack"
    swift_pm = "SwiftPM"
    unmanaged = "Unmanaged"
    yarn = "Yarn"
    yarn2 = "Yarn2"


class PackageManagerConfigs(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    must_run_after: list[OrtPackageManagers] | None = Field(None, alias="mustRunAfter")
    options: Any | None = None


class OrtPackageManagerConfigurations(RootModel[dict[str, PackageManagerConfigs]]):
    root: dict[str, PackageManagerConfigs]
