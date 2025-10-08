# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], [markdownlint],
and this project adheres to [Semantic Versioning].

## [Unreleased]

-

## [0.2.16] - 2025-10-07

### Changed in 0.2.16

- Renamed classes

## [0.2.15] - 2025-09-30

### Changed in 0.2.15

- Moved "schema" to "typedef"

## [0.2.14] - 2025-09-30

### Changed in 0.2.14

- Update workflows

## [0.2.13] - 2025-09-24

### Changed in 0.2.13

- Fix issue with checksums

## [0.2.12] - 2025-09-24

### Changed in 0.2.12

- Fix workflow

## [0.2.11] - 2025-09-23

### Added in 0.2.11

- Add/Rename utility programs in `bin` directory.
- Make HTML/JSON files in `docs` directory.
- Tests which pull test data directly from SenzingSDK

### Changed in 0.2.11

- Update `senzingsdk-RFC8927.json` massively.
- Change Python's `typedef` to `senzing-typedef`

## [0.2.10] - 2025-07-02

### Changed in 0.2.10

- Change `SzConfig.AddDataSource` to `SzConfig.RegisterDataSource`
- Change `SzConfig.DeleteDataSource` to `SzConfig.UnregisterDataSource`
- Change `SzConfig.GetDataSources` to `SzConfig.GetDataSourceRegistry`
- Change `SzDiagnostic.CheckDatastorePerformance` to `SzDiagnostic.CheckRepositoryPerformance`
- Change `SzDiagnostic.GetDatastoreInfo` to `SzDiagnostic.GetRepositoryInfo`
- Change `SzEngine.CloseExport` to `SzEngine.CloseExportReport`
- Change `SzEngine.PreprocessRecord` to ``SzEngine.GetRecordPreview`

## [0.2.9] - 2025-06-17

### Changed in 0.2.9

- Change `SzConfigManagerGetConfigsResponse` to `SzConfigManagerGetConfigRepositoryResponse`

## [0.2.8] - 2025-04-21

### Changed in 0.2.8

- Updated dependencies

## [0.2.7] - 2024-09-04

### Added in 0.2.7

- Change SzConfig.`GetConfigList` to `SzConfig.GetConfigs`

## [0.2.6] - 2024-05-13

### Added in 0.2.6

- Improved the "unknown" responses:
  - SzEngineFetchNextResponse
  - SzEngineGetRedoRecordResponse
  - SzEngineGetStatsResponse
  - SzEngineStreamExportJsonEntityReportResponse
  - SzEngineWhyRecordInEntityResponse

## [0.2.5] - 2024-05-10

### Added in 0.2.5

- SzDiagnosticGetDatastoreInfoResponse
- SzDiagnosticGetFeatureResponse
- SzEngineFindInterestingEntitiesByEntityIdResponse
- SzEngineFindInterestingEntitiesByRecordIdResponse
- SzEngineWhyRecordInEntityResponse

### Changed in 0.2.5

- SzConfigExportConfigResponse
- SzDiagnosticCheckDatastorePerformanceResponse

### Removed in 0.2.5

- SzEngineReplaceRecordResponse

## [0.2.4] - 2024-04-02

### Changed in 0.2.4

- Change from `SzConfigmgr` to `SzConfigManager`

## [0.2.3] - 2024-03-28

### Changed in 0.2.3

- Changed repository from "g2-sdk-json-type-definition" to "sz-sdk-json-type-definition"

## [0.2.2] - 2024-03-27

### Changed in 0.2.2

- Changed prefix from "G2" to Sz"

## [0.2.1] - 2024-02-22

### Changed in 0.2.1

- Added unit testing
- 0.2.x is for Senzing version 3.x.  The 0.3.x is for 4.x

## [0.2.0] - 2023-12-29

### Changed in 0.2.0

- Migrated from `github.com/senzing/` to `github.com/senzing-garage`

## [0.1.1] - 2023-07-05

### Added to 0.1.1

- Rename `test_cases_all.py` to `test_cases.py`
- Added tests

## [0.1.0] - 2023-07-05

### Added to 0.1.0

- Initial draft of Senzing returned JSON object model

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[markdownlint]: https://dlaa.me/markdownlint/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
