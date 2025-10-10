# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2025-10-10

### Changed
- No changes

## [1.4.0] - 2025-10-09

### Changed
- No changes

## [1.3.0] - 2025-10-05

### Changed
- No changes

## [1.2.0] - 2025-09-25

### Changed
- No changes

## [1.1.1] - 2025-09-11

### Changed
- No changes

## [1.1.0] - 2025-09-11

### Changed
- No changes

## [1.0.1] - 2025-09-11

### Changed
- No changes - version bump for consistency with other packages

## [1.0.0] - 2025-09-09

### Added
- Initial release of kiarina-lib-redisearch
- RediSearch client with configuration management using pydantic-settings-manager
- Full-text search and vector search capabilities
- Support for both sync and async operations
- Type safety with full type hints and Pydantic validation
- Environment variable configuration support
- Runtime configuration overrides
- Multiple named configurations support
- Comprehensive schema management with field types:
  - Tag fields for categorical data
  - Numeric fields for numerical data
  - Text fields for full-text search
  - Vector fields for similarity search (FLAT and HNSW algorithms)
- Advanced filtering system with query builder
- Index management operations (create, drop, migrate, reset)
- Document operations (set, get, delete)
- Search operations (find, search, count)
- Automatic schema migration support

### Dependencies
- numpy>=2.3.2
- pydantic>=2.11.7
- pydantic-settings>=2.10.1
- pydantic-settings-manager>=2.1.0
- redis>=6.4.0
