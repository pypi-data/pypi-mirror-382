# Graphon Client - Build and Publish

## Prerequisites
- Python 3.8+
- Tools:
```bash
python -m pip install --upgrade build twine
```

## 1) Bump the version
Edit `pyproject.toml` and increment:
```toml
[project]
version = "X.Y.Z"
```

## 2) Build distributions
From this directory:
```bash
python -m build
```
Outputs go to `dist/` (`.tar.gz` and `.whl`).

## 3) Verify the distributions
```bash
python -m twine check dist/*
```

## 4) Test upload to TestPyPI (optional but recommended)
Create a token at if not already existing at `https://test.pypi.org/manage/account/token/` and export it:
```bash
export TESTPYPI_TOKEN="<insert_token>"
python -m twine upload --repository testpypi -u __token__ -p "$TESTPYPI_TOKEN" dist/*
```

Test install from TestPyPI (with PyPI as fallback for dependencies):
```bash
python -m venv .venv-test
. .venv-test/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple \
  --extra-index-url https://pypi.org/simple graphon-client==X.Y.Z
python -c "from graphon_client import GraphonClient; print(GraphonClient)"
deactivate
```

## 5) Upload to PyPI
```bash
export PYPI_TOKEN="<insert_token>"
python -m twine upload -u __token__ -p "$PYPI_TOKEN" dist/*
```

Notes:
- PyPI versions are immutable; always bump before rebuilding.
- Package name on PyPI: `graphon-client`; import name: `graphon_client`.