# Changelog

## simtrial-python 0.1.0

- Increment version number to 0.1.0 to follow semantic versioning
  best practices (#6).

## simtrial-python 0.0.1

### New features

- Added a piecewise exponential sampler that mirrors the R implementation using
  inverse-CDF sampling with reproducibility hooks and type hints (#1).

### Testing

- Added pytest tests with 100% code coverage for the sampler, including
  validation, broadcasting, and RNG behaviors (#1).
- Added deterministic R-generated fixtures (`tests/fixtures/`) to
  cross-check Python draws (#1).
