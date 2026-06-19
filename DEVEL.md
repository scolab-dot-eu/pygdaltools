# Developer guide

## Requirements

- Python 3.9+ for the development toolchain (3.11 recommended)
- GDAL/OGR command line tools installed on the system (`gdal-bin` on Debian/Ubuntu)

The library itself targets Python 3.7+ and has no Python dependencies at runtime.

## Development dependencies

Development dependencies are declared in `pyproject.toml` under
`[project.optional-dependencies.dev]` (pytest, ruff, build, tox, twine).

The `requirements-dev.txt` file is a convenience wrapper that installs the
project in editable mode with those extras:

```
-e .[dev]
```

## Setup

Create and activate a virtualenv inside the project (`.venv` is ignored by git):

```bash
cd pygdaltools
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt
```

If `python3 -m venv` is not available on your system, use `virtualenv` instead:

```bash
virtualenv -p python3.11 .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt
```

Equivalent command without the requirements file:

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

Run the test suite across multiple Python versions:

```bash
tox
```

## Linting

```bash
ruff check gdaltools tests
```

## Building distributions

```bash
python -m build
twine check dist/*
```

Artifacts are written to `dist/`.

## Publishing

### PyPI

1. Bump the version in `gdaltools/metadata.py`.
2. Create a GitHub release for that tag.
3. The `Publish to PyPI` workflow publishes the release artifacts using [trusted publishing](https://docs.pypi.org/trusted-publishers/).

You can also trigger the workflow manually from the Actions tab.

Local upload (requires a PyPI API token):

```bash
python -m build
twine upload dist/*
```

### AWS CodeArtifact

Use the `pygdaltools - Build and Push` workflow from the Actions tab, or upload manually after logging in with the AWS CLI:

```bash
python -m build
aws codeartifact login --tool twine --repository eop --domain <domain> --domain-owner <owner> --region eu-west-3
twine upload --repository codeartifact dist/*
```
