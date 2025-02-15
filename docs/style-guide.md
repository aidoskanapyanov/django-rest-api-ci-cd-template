# Style Guide

## Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages to ensure consistent commit history and enable automated releases and changelog generation.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat:` New features (e.g., `feat: add airplane fuel calculation endpoint`)
- `fix:` Bug fixes (e.g., `fix: correct fuel consumption formula`)
- `docs:` Documentation changes (e.g., `docs: update API endpoints guide`)
- `style:` Code style changes (e.g., `style: format with black`)
- `refactor:` Code refactoring (e.g., `refactor: extract fuel calculation logic`)
- `perf:` Performance improvements (e.g., `perf: optimize database queries`)
- `test:` Adding or modifying tests (e.g., `test: add fuel capacity validation tests`)
- `build:` Build system changes (e.g., `build: update docker configuration`)
- `ci:` CI/CD changes (e.g., `ci: add coverage reporting`)
- `chore:` Other changes (e.g., `chore: update dependencies`)

### Examples

```
feat(api): add endpoint for calculating total fuel consumption

- Implements GET /api/fuel/total endpoint
- Adds validation for passenger count
- Updates API documentation

Closes #123
```

```
fix: prevent negative passenger count

Validates passenger count to ensure it's always positive
```

## Versioning

This project follows [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version for incompatible API changes (1.0.0)
- **MINOR** version for new functionality in a backward compatible manner (1.1.0)
- **PATCH** version for backward compatible bug fixes (1.1.1)

### Automated Releases

- Release versions are automatically generated based on conventional commit messages
- A new version is created when merging to the main branch
- The version number is determined by commit types:
  - `feat:` triggers MINOR version bump
  - `fix:` triggers PATCH version bump
  - `BREAKING CHANGE:` in commit body triggers MAJOR version bump

### Changelog

The changelog is automatically generated from conventional commit messages and includes:

- Version number and release date
- Grouped changes by type (Features, Bug Fixes, etc.)
- Links to related issues and pull requests
- Breaking changes clearly marked

The changelog is updated with each release and can be found in CHANGELOG.md.
