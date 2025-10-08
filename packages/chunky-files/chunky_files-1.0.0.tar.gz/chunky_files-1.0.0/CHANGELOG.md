# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-07

### Added
- Stable chunk identifiers (`<doc_id>#chunk-0000`) with configurable metadata keys/templates and per-chunk `chunk_count`/`source_document` fields.

## [0.4.0] - 2025-09-30

### Changed
- Optional `tree` extra now installs `tree-sitter==0.20.1` plus bundled grammars for consistent Tree-sitter support (C/C++/HTML/Bash).

## [0.3.0] - 2025-09-30

### Added
- Language-aware chunkers for Python, Markdown, JSON/YAML, plain text, Fortran, and Tree-sitter powered C/C++/HTML support.
- Registry bootstrap that pre-registers the built-in chunkers for common extensions.
- Unit tests covering the new chunkers and regression coverage for the sliding-window fallback.

## [0.2.2] - 2025-09-30
### Fixed
- Pinned the release workflow to `pypa/gh-action-pypi-publish@release/v1` and added a `twine check` gate, eliminating spurious "missing Name/Version" errors during automated publishes.
- Corrected the Sphinx intersphinx configuration so Read the Docs builds resolve the Python inventory without manual tweaks.

## [0.2.1] - 2025-09-30

### Changed
- Renamed the published distribution to `chunky-files` and refreshed packaging metadata for the new name.

### Fixed
- Ensured `pyproject.toml` ships in the sdist include list to keep build metadata intact across platforms.

## [0.2.0] - TBD
### Added
- Changelog (`CHANGELOG.md`; this file).
- Release process section added to the existing `README.md`
- `PYPI_TOKEN`, `TEST_PYPI_TOKEN`, and `CODECOV_TOKEN` added to github secrets
- `.env` and other common evironment file name added to the `.gitignore` for token security.

### Changes
- Release workflow updated to have matching secrets name.

### Fixes
- Updated dependencies and improve type hints in codebase (ruff compliance).
- Update build tooling installation in release .
- Included pyproject.toml in sdist build targets.

## [0.1.0] - 2025-09-30
### Added
- Initial project scaffolding with Hatchling build system and CI/release workflows.
- Core chunking data models (`Document`, `Chunk`, `ChunkerConfig`).
- Sliding-window fallback chunker with metadata-rich outputs.
- `ChunkPipeline` orchestration, registry, and filesystem loader.
- Sphinx documentation skeleton and Read the Docs configuration.
- Pytest and Ruff tooling with baseline tests for the sliding-window chunker.
