# Publishing Observatory Python SDK to PyPI

This guide explains how to build and publish the Observatory Python SDK to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create an account at https://pypi.org/
   - Create an account at https://test.pypi.org/ (for testing)

2. **Install Build Tools**

```bash
pip install build twine
```

## Building the Package

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Update Version

Update version in these files:
- `pyproject.toml` → `version = "0.1.0"`
- `observatory_mcp/__init__.py` → `__version__ = "0.1.0"`

### 3. Update CHANGELOG

Add release notes to `CHANGELOG.md`

### 4. Build the Package

```bash
python -m build
```

This creates:
- `dist/observatory_mcp-0.1.0.tar.gz` (source distribution)
- `dist/observatory_mcp-0.1.0-py3-none-any.whl` (wheel)

### 5. Verify the Package

```bash
twine check dist/*
```

Expected output:
```
Checking dist/observatory_mcp-0.1.0.tar.gz: PASSED
Checking dist/observatory_mcp-0.1.0-py3-none-any.whl: PASSED
```

## Testing the Package Locally

### Install Locally

```bash
pip install -e .
```

### Run Tests

```bash
pytest --cov=observatory_mcp
```

### Test Installation from Wheel

```bash
pip install dist/observatory_mcp-0.1.0-py3-none-any.whl
```

## Publishing to Test PyPI

### 1. Configure Test PyPI (One-time Setup)

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-PYPI-TOKEN
```

### 2. Upload to Test PyPI

```bash
twine upload --repository testpypi dist/*
```

### 3. Test Installation from Test PyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps observatory-mcp
```

### 4. Verify

```python
import observatory_mcp
print(observatory_mcp.__version__)
```

## Publishing to Production PyPI

### Method 1: Using Trusted Publishing (Recommended)

1. **Configure GitHub Actions**
   - Already set up in `.github/workflows/publish.yml`
   - Uses OpenID Connect (OIDC) - no API tokens needed!

2. **Set Up Trusted Publishing on PyPI**
   - Go to https://pypi.org/manage/account/publishing/
   - Add new publisher:
     - PyPI Project Name: `observatory-mcp`
     - GitHub Repository: `observatory/observatory`
     - Workflow: `publish.yml`
     - Environment: (leave empty)

3. **Create a GitHub Release**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
   
   - Go to GitHub → Releases → Create new release
   - Choose tag `v0.1.0`
   - Write release notes
   - Publish release
   
   GitHub Actions will automatically publish to PyPI!

### Method 2: Manual Upload with Token

1. **Get PyPI API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create new API token
   - Scope: Entire account or specific project
   - Copy token (starts with `pypi-`)

2. **Configure PyPI**

Add to `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN
```

3. **Upload**

```bash
twine upload dist/*
```

4. **Verify**

Visit: https://pypi.org/project/observatory-mcp/

Install:
```bash
pip install observatory-mcp
```

## Post-Publication Checklist

- [ ] Verify package on PyPI: https://pypi.org/project/observatory-mcp/
- [ ] Test installation: `pip install observatory-mcp`
- [ ] Verify imports work
- [ ] Update documentation with new version
- [ ] Announce release (Discord, Twitter, etc.)
- [ ] Create GitHub Release with changelog
- [ ] Update project homepage

## Version Bumping

### Semantic Versioning

- **0.1.0** → **0.1.1** - Bug fixes (patch)
- **0.1.0** → **0.2.0** - New features (minor)
- **0.1.0** → **1.0.0** - Breaking changes (major)

### Files to Update

1. `pyproject.toml` - `version = "x.y.z"`
2. `observatory_mcp/__init__.py` - `__version__ = "x.y.z"`
3. `CHANGELOG.md` - Add new section for version

### Automated Version Bumping (Optional)

Use `bump2version`:

```bash
pip install bump2version

# Patch: 0.1.0 → 0.1.1
bump2version patch

# Minor: 0.1.0 → 0.2.0
bump2version minor

# Major: 0.1.0 → 1.0.0
bump2version major
```

## Troubleshooting

### Upload Failed: File Already Exists

PyPI doesn't allow overwriting versions. Bump version and rebuild:

```bash
# Update version in pyproject.toml and __init__.py
python -m build
twine upload dist/*
```

### Package Name Already Taken

Choose a different name in `pyproject.toml`:

```toml
[project]
name = "observatory-mcp-yourname"
```

### Import Errors After Installation

Check package structure:

```bash
python -m zipfile -l dist/*.whl
```

Ensure `observatory_mcp/` directory is included.

### Authentication Failed

1. Verify token is correct
2. Check `~/.pypirc` format
3. For trusted publishing, verify GitHub settings

## Development Releases

For pre-release versions:

```toml
# pyproject.toml
version = "0.1.0a1"  # Alpha
version = "0.1.0b1"  # Beta
version = "0.1.0rc1" # Release candidate
```

Install with:
```bash
pip install --pre observatory-mcp
```

## Resources

- **PyPI Documentation**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Python Packaging Guide**: https://packaging.python.org/guides/
- **Semantic Versioning**: https://semver.org/

## Quick Reference

```bash
# Build
python -m build

# Check
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ observatory-mcp

# Install from PyPI
pip install observatory-mcp
```
