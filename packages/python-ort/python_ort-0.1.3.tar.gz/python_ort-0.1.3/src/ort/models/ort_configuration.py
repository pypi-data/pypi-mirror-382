# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
#
# SPDX-License-Identifier: MIT


from enum import Enum
from pathlib import Path
from typing import Annotated, Any

import yaml
import yaml.parser
from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel

from .package_managers import OrtPackageManagerConfigurations, OrtPackageManagers


class AdvisorConfig(RootModel[dict[str, dict[str, Any]] | None]):
    root: dict[str, dict[str, Any]] | None = None


class Sw360Configuration(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    rest_url: Annotated[AnyUrl, Field(alias="restUrl")]
    auth_url: Annotated[AnyUrl, Field(alias="authUrl")]
    username: str
    password: str | None = None
    client_id: Annotated[str, Field(alias="clientId")]
    client_password: Annotated[str | None, Field(alias="clientPassword")] = None
    token: str | None = None


class LicenseFilePatterns(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    license_filenames: Annotated[list[str] | None, Field(alias="licenseFilenames")] = None
    patent_filenames: Annotated[list[str] | None, Field(alias="patentFilenames")] = None
    other_license_filenames: Annotated[list[str] | None, Field(alias="otherLicenseFilenames")] = None


class Jira(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    host: str | None = None
    username: str | None = None
    password: str | None = None


class Mail(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    host_name: Annotated[str | None, Field(alias="hostName")] = None
    username: str | None = None
    password: str | None = None
    port: int | None = None
    use_ssl: Annotated[bool | None, Field(alias="useSsl")] = None
    from_address: Annotated[str | None, Field(alias="fromAddress")] = None


class ReporterOptions(AdvisorConfig):
    pass


class LocalFileStorage(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    directory: str
    compression: bool | None = None


class S3FileStorage(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    access_key_id: Annotated[str | None, Field(alias="accessKeyId")] = None
    aws_region: Annotated[str | None, Field(alias="awsRegion")] = None
    bucket_name: Annotated[str, Field(alias="bucketName")]
    compression: bool | None = None
    custom_endpoint: Annotated[str | None, Field(alias="customEndpoint")] = None
    secret_access_key: Annotated[str | None, Field(alias="secretAccessKey")] = None


class Connection(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    url: str
    schema_: Annotated[str | None, Field(alias="schema")] = None
    username: str
    password: str | None = None
    sslmode: str | None = None
    sslcert: str | None = None
    sslkey: str | None = None
    sslrootcert: str | None = None
    connection_timeout: Annotated[int | None, Field(alias="connectionTimeout")] = None
    idle_timeout: Annotated[int | None, Field(alias="idleTimeout")] = None
    keepalive_time: Annotated[int | None, Field(alias="keepaliveTime")] = None
    max_lifetime: Annotated[int | None, Field(alias="maxLifetime")] = None
    maximum_pool_size: Annotated[int | None, Field(alias="maximumPoolSize")] = None
    minimum_idle: Annotated[int | None, Field(alias="minimumIdle")] = None


class DetectedLicenseMapping(RootModel[dict[str, str] | None]):
    root: dict[str, str] | None = None


class ScannerConfig(AdvisorConfig):
    pass


class Storages(AdvisorConfig):
    pass


class Severity(Enum):
    HINT = "HINT"
    WARNING = "WARNING"
    ERROR = "ERROR"


class SourceCodeOrigins(Enum):
    ARTIFACT = "ARTIFACT"
    VCS = "VCS"


class StorageTypes(Enum):
    AWS = "aws"
    CLEARLY_DEFINED = "clearlyDefined"
    HTTP = "http"
    LOCAL = "local"
    POSTGRES = "postgres"


class Headers(RootModel[dict[str, bool | float | str] | None]):
    root: dict[str, bool | float | str] | None = None


class Advisor(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    skip_excluded: Annotated[bool | None, Field(alias="skipExcluded")] = None
    config: AdvisorConfig | None = None


class Downloader(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    allow_moving_revisions: Annotated[bool | None, Field(alias="allowMovingRevisions")] = None
    included_license_categories: Annotated[list[str] | None, Field(alias="includedLicenseCategories")] = None
    skip_excluded: Annotated[bool | None, Field(alias="skipExcluded")] = None
    source_code_origins: Annotated[list[SourceCodeOrigins] | None, Field(alias="sourceCodeOrigins")] = None


class Notifier(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    mail: Mail | None = None
    jira: Jira | None = None


class Reporter(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    config: ReporterOptions


class HttpFileStorage(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    url: AnyUrl
    query: str | None = None
    headers: Headers | None = None


class PostgresConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    connection: Connection


class AnalyzerConfigurationSchema(BaseModel):
    """
    Configurations for package managers used by the The OSS-Review-Toolkit (ORT).
    A full list of all available options can be found at
    https://github.com/oss-review-toolkit/ort/blob/main/model/src/main/kotlin/config/AnalyzerConfiguration.kt.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    allow_dynamic_versions: Annotated[bool | None, Field(alias="allowDynamicVersions")] = None
    enabled_package_managers: Annotated[list[OrtPackageManagers] | None, Field(alias="enabledPackageManagers")] = None
    disabled_package_managers: Annotated[list[OrtPackageManagers] | None, Field(alias="disabledPackageManagers")] = None
    package_managers: Annotated[OrtPackageManagerConfigurations | None, Field(alias="packageManagers")] = None
    sw360_configuration: Annotated[Sw360Configuration | None, Field(alias="sw360Configuration")] = None
    skip_excluded: Annotated[bool | None, Field(alias="skipExcluded")] = None


class FileStorage1(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    local_file_storage: Annotated[LocalFileStorage, Field(alias="localFileStorage")]
    http_file_storage: Annotated[HttpFileStorage | None, Field(alias="httpFileStorage")] = None
    s3_file_storage: Annotated[S3FileStorage | None, Field(alias="s3FileStorage")] = None


class FileStorage2(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    local_file_storage: Annotated[LocalFileStorage | None, Field(alias="localFileStorage")] = None
    http_file_storage: Annotated[HttpFileStorage, Field(alias="httpFileStorage")]
    s3_file_storage: Annotated[S3FileStorage | None, Field(alias="s3FileStorage")] = None


class FileStorage3(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    local_file_storage: Annotated[LocalFileStorage | None, Field(alias="localFileStorage")] = None
    http_file_storage: Annotated[HttpFileStorage | None, Field(alias="httpFileStorage")] = None
    s3_file_storage: Annotated[S3FileStorage, Field(alias="s3FileStorage")]


class FileStorage(RootModel[FileStorage1 | FileStorage2 | FileStorage3]):
    root: FileStorage1 | FileStorage2 | FileStorage3


class ProvenanceStorage(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    file_storage: Annotated[FileStorage | None, Field(alias="fileStorage")] = None
    postgres_storage: Annotated[PostgresConfig | None, Field(alias="postgresStorage")] = None


class Analyzer(RootModel[AnalyzerConfigurationSchema]):
    root: AnalyzerConfigurationSchema


class Archive(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    enabled: bool | None = None
    file_storage: Annotated[FileStorage | None, Field(alias="fileStorage")] = None
    postgres_storage: Annotated[PostgresConfig | None, Field(alias="postgresStorage")] = None


class FileListStorage(ProvenanceStorage):
    pass


class Scanner(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    skip_concluded: Annotated[bool | None, Field(alias="skipConcluded")] = None
    skip_excluded: Annotated[bool | None, Field(alias="skipExcluded")] = None
    archive: Archive | None = None
    detected_license_mapping: Annotated[DetectedLicenseMapping | None, Field(alias="detectedLicenseMapping")] = None
    file_list_storage: Annotated[FileListStorage | None, Field(alias="fileListStorage")] = None
    config: ScannerConfig | None = None
    storages: Storages | None = None
    storage_readers: Annotated[list[StorageTypes] | None, Field(alias="storageReaders")] = None
    storage_writers: Annotated[list[StorageTypes] | None, Field(alias="storageWriters")] = None
    ignore_patterns: Annotated[list[str] | None, Field(alias="ignorePatterns")] = None
    provenance_storage: Annotated[ProvenanceStorage | None, Field(alias="provenanceStorage")] = None


class Ort(BaseModel):
    license_file_patterns: Annotated[LicenseFilePatterns | None, Field(alias="licenseFilePatterns")] = None
    severe_issue_threshold: Annotated[Severity | None, Field(alias="severeIssueThreshold")] = None
    severe_rule_violation_threshold: Annotated[Severity | None, Field(alias="severeRuleViolationThreshold")] = None
    enable_repository_package_curations: Annotated[bool | None, Field(alias="enableRepositoryPackageCurations")] = None
    enable_repository_package_configurations: Annotated[
        bool | None, Field(alias="enableRepositoryPackageConfigurations")
    ] = None
    analyzer: Analyzer | None = None
    advisor: Advisor | None = None
    downloader: Downloader | None = None
    scanner: Scanner | None = None
    reporter: Reporter | None = None
    notifier: Notifier | None = None


class OrtConfiguration(BaseModel):
    """
    The main configuration file for the OSS-Review-Toolkit (ORT).
    A full list of all available options can be found at
    https://github.com/oss-review-toolkit/ort/blob/main/model/src/main/resources/reference.yml.
    """

    ort: Ort

    def __init__(self, ort_file: str | Path | None = None, **data: dict[str, Any]) -> None:
        if ort_file:
            if isinstance(ort_file, str):
                ort_file = Path(ort_file)
            try:
                with ort_file.open() as fp:
                    model = yaml.safe_load(fp)
                data.update(model)
            except FileNotFoundError as e:
                raise ValueError(e)
            except yaml.parser.ParserError as e:
                print(f"Error decoding YAML from {ort_file}")
                raise ValueError(e)
            except Exception as e:
                raise ValueError(e)
            super().__init__(**data)
