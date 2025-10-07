# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-10-07

### Added
- **MyPy configuration** with relaxed settings for gradual type safety adoption (38 type errors to fix incrementally)
- **Comprehensive ruff linting** with additional rules: D (pydocstyle), ARG, SIM, ICN, PIE, T20, PYI, PT, Q, RSE, RET, TID, TCH, RUF
- **Coverage threshold** enforcement at 75% minimum (with goal of 80% after correlation.py tests)
- **Type checking support** configured in pyproject.toml (not enforced in CI yet)
- **Consolidated dependency structure** with simplified `[dev]` group
- **Automated version bumping** capability via Makefile
- **Enhanced Makefile** aligned with project template:
  - `help` - Self-documenting default target
  - `quality` - Run all quality checks (ruff format + ruff check)
  - `test-cov` - Tests with coverage in tests/htmlcov/
  - `test-fast` - Parallel test execution
  - `install-dev` - Install with dev dependencies
  - `bump-version` - Automated version management
  - `docs` - Generate HTML documentation from nhandu tutorials
- **Simplified CI/CD** with `quality.yml` workflow (ruff + tests, mypy disabled temporarily)
- **Test markers** for better organization (slow, integration, unit, performance, large_data)
- **Coverage reporting** with term-missing, HTML (tests/htmlcov/), and XML outputs
- **Comprehensive pytest configuration** in pyproject.toml
- **Dependabot** configuration for automated dependency updates

### Changed
- **BREAKING**: Migrated from **hatchling to setuptools** build backend
- **BREAKING**: **Version now managed dynamically** from `__init__.py` (single source of truth)
- **BREAKING**: Simplified optional dependencies - use `pip install asymcat[dev]` instead of multiple groups
- **BREAKING**: Removed CLI tool (`asymcat` command) - library-only package
- **Makefile simplified** to match freqprob template (removed emojis, venv auto-detection, granular targets)
- **Coverage output location** moved to `tests/htmlcov/` (from root `htmlcov/`)
- **Line length increased to 120** (from template's 100) for better code readability
- **Ruff docstring convention** changed to numpy (matches existing codebase)
- **Package distribution** excludes large datasets (wiktionary.tsv, cmudict.tsv, pokemon.tsv, mushrooms.tsv) - reduced from 5.6MB to <100KB
- **Generated HTML docs** excluded from distribution (tutorials source .py files included)
- Migrated CHANGELOG to Keep a Changelog format with semantic versioning
- Updated freqprob dependency to >=0.4.0 with Lidstone API compatibility
- Consolidated pytest configuration from pytest.ini to pyproject.toml
- Updated CI/CD to simplified quality workflow (faster, clearer)
- Enhanced .gitignore with modern Python patterns and tests/htmlcov/
- Updated GitHub Actions workflows to use consolidated dependencies

### Removed
- **Scripts directory utilities**: `bump_version.py`, `setup-local-testing.sh`, `test-local.sh` (use Makefile instead)
- **Sphinx documentation infrastructure**: `docs/source/` directory and all Sphinx dependencies (use nhandu only)
- **Unused dependencies**:
  - Development: jupyter, jupyterlab, ipywidgets, notebook, nbconvert
  - Visualization: plotly, bokeh, altair (from optional dependencies)
  - Profiling: memory_profiler, line_profiler
  - Machine learning: scikit-learn (from dev deps)
  - Type stubs: types-tabulate, types-setuptools
  - Security (from Makefile): bandit, safety moved to optional manual use
- **Hatch build system** and all `[tool.hatch.*]` configurations
- **`.github/workflows-archive/`** directory
- **BREAKING**: CLI entry point (`asymcat.__main__:main`) - reduces complexity, improves coverage
- **BREAKING**: Granular optional dependency groups (test, lint, typecheck, security, dev-tools, docs, jupyter, performance)
- Complex CI/CD workflows (build.yml, security.yml) - archived for reference
- Obsolete dependencies: black, isort, flake8, pre-commit, bump2version
- pytest.ini file (consolidated into pyproject.toml)

### Fixed
- **Package size bloat** - reduced from 5.6MB to <100KB by excluding large datasets and generated files
- **Build configuration** for setuptools (removed license classifier conflict with MIT license field)
- **Ruff configuration** to ignore phonetic symbols (IPA) as ambiguous unicode (RUF001, RUF002, RUF003)
- **Test coverage output** location consistency (now tests/htmlcov/ everywhere)
- **GitHub workflow** coverage threshold aligned to 75%
- **Citation version** in README updated to 0.4.0 and year to 2025
- Lidstone API calls for freqprob 0.4.0 compatibility (use `gamma=` parameter)
- Type checking errors with proper type: ignore annotations

### Migration Guide

#### For Users
No changes required. Core functionality unchanged.

#### For Developers

**Dependency Installation:**
```bash
# Before (v0.3.1)
pip install -e ".[test,lint,typecheck,security,dev-tools]"

# After (v0.4.0)
pip install -e ".[dev]"  # All dev tools included
```

**CI/CD Updates:**
```yaml
# Before
- pip install ".[test]"
- pip install ".[security]"

# After
- pip install -e ".[dev]"
```

**CLI Usage:**
The CLI has been removed. Use the library API directly:
```python
# Instead of: asymcat input.tsv --scorers mle pmi
import asymcat
data = asymcat.read_sequences("input.tsv")
cooccs = asymcat.collect_cooccs(data)
scorer = asymcat.scorer.CatScorer(cooccs)
mle_scores = scorer.mle()
pmi_scores = scorer.pmi()
```

## [0.3.1] - 2024-10-04

### Added
- Enhanced documentation with 4 interactive Jupyter notebooks (1.4MB+ examples)
  - `Simple_Examples.ipynb` (278KB) - Perfect starting point
  - `Demo.ipynb` (221KB) - Visualization showcase
  - `Academic_Analysis_Tutorial.ipynb` (44KB) - Research-grade examples
  - `EXAMPLES_WITH_PLOTS.ipynb` (903KB) - Publication-ready analysis
- Publication-ready examples with academic-grade analysis workflows
- Real-world applications: linguistics, ecology, machine learning case studies
- Advanced visualizations with heatmaps and statistical distributions
- All notebooks pre-executed with committed outputs for immediate viewing
- Bootstrap confidence intervals and permutation testing examples
- GitHub Actions workflow for automated notebook execution and validation

### Changed
- Migrated to Ruff for unified linting and formatting (replaced black, isort, flake8)
- Fixed GitHub Actions CI/CD workflows and notebook execution
- Systematically fixed majority of mypy type checking errors
- Migrated build system from setuptools to Hatch
- Enhanced freqprob integration with version compatibility
- Fixed linting issues to ensure all CI workflows pass locally
- Updated Python requirement to 3.10+ across all configurations

### Fixed
- Notebook execution in GitHub Actions with proper timeout and error handling
- Version synchronization between pyproject.toml and __init__.py
- Type checking errors throughout codebase
- Remaining GitHub Actions issues with branch references and versions

## [0.3.0] - 2023-XX-XX

### Changed
- **BREAKING**: Renamed package from `catcoocc` to `asymcat`
  - Better reflects the library's focus on asymmetric categorical association analysis
  - More intuitive and descriptive name for users

### Migration Guide

**Upgrading from catcoocc to asymcat:**

```python
# Before (catcoocc)
import catcoocc

# After (asymcat)
import asymcat
```

All APIs remain the same, only the package name changed.

## [0.2.3] - 2020-06-29

### Added
- Initial PyPI release as `catcoocc`
- Core package infrastructure

## [0.2.2] - 2020-XX-XX

### Added
- Function for inverting a scorer
- Scorer inversion utilities

## [0.2.1] - 2020-XX-XX

### Added
- Basic functions for double series correlation
- Correlation analysis capabilities

## [0.2.0] - 2019-XX-XX

### Added
- Initial public release
- Core asymmetric association measures:
  - Maximum Likelihood Estimation (MLE)
  - Pointwise Mutual Information (PMI)
  - Chi-square test
  - Fisher's exact test
  - Cramér's V
  - Goodman and Kruskal's lambda
  - Jaccard index
  - Mutual information
  - Conditional entropy
  - Theil's U
  - Log-likelihood ratio
- Sequence and presence-absence matrix readers
- N-gram support with configurable window sizes
- Co-occurrence collection from aligned sequences
- Basic visualization utilities
- Scorer transformation and scaling functions

---

## Version History

- **0.4.0** - Modernization: simplified deps, enhanced tooling, Keep a Changelog, removed CLI
- **0.3.1** - Documentation: Jupyter notebooks, Ruff migration, Hatch build, freqprob updates
- **0.3.0** - Renamed from catcoocc to asymcat
- **0.2.3** - First PyPI release (as catcoocc)
- **0.2.2** - Scorer inversion
- **0.2.1** - Double series correlation
- **0.2.0** - Initial release

[Unreleased]: https://github.com/tresoldi/asymcat/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/tresoldi/asymcat/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/tresoldi/asymcat/releases/tag/v0.3.1
[0.3.0]: https://github.com/tresoldi/asymcat/releases/tag/v0.3.0
[0.2.3]: https://github.com/tresoldi/asymcat/releases/tag/catcoocc0.2.3
[0.2.2]: https://github.com/tresoldi/asymcat/releases/tag/v0.2.2
[0.2.1]: https://github.com/tresoldi/asymcat/releases/tag/v0.2.1
[0.2.0]: https://github.com/tresoldi/asymcat/releases/tag/v0.2.0
