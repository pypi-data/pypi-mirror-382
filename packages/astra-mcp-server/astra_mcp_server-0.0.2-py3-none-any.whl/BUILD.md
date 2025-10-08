# Building and Releasing astra-mcp-server

This document provides instructions for building the package and creating new releases.

## TLDR

```bash
uv pip install --upgrade build
uv pip install --upgrade twine
uv build
uv twine upload dist/*
```

## Prerequisites

Make sure you have the following tools installed:
- `uv` (Python package manager)
- `git` (version control)
- `twine` (for PyPI uploads)

## Development Build

For local development and testing:

```bash
# Install build dependencies
uv pip install --upgrade build

# Build the package locally
uv build
```

This will create distribution files in the `dist/` directory.

## Creating a New Release

### 1. Update Version Numbers

Before creating a release, update the version number in both configuration files:

**Update `pyproject.toml`:**
```toml
[project]
name = "astra-mcp-server"
version = "0.0.2"  # Update this version
```

**Update `setup.py`:**
```python
setup(
    name="astra-mcp-server",
    version="0.0.2",  # Update this version
    # ... rest of configuration
)
```

### 2. Commit Version Changes

```bash
# Add the modified files
git add pyproject.toml setup.py

# Commit the version bump
git commit -m "Bump version to 0.0.2"
```

### 3. Create Git Tag

```bash
# Create and push the git tag
git tag -a v0.0.2 -m "Release version 0.0.2"
git push origin v0.0.2
```

### 4. Build Distribution Packages

```bash
# Clean previous builds
rm -rf dist/

# Build the package
uv build
```

This creates:
- `dist/astra_mcp_server-0.0.2-py3-none-any.whl` (wheel package)
- `dist/astra_mcp_server-0.0.2.tar.gz` (source distribution)

### 5. Test the Build (Optional)

```bash
# Install twine for testing
uv pip install twine

# Check the package for common issues
twine check dist/*
```

### 6. Upload to PyPI

**For TestPyPI (recommended for testing):**
```bash
twine upload --repository testpypi dist/*
```

**For Production PyPI:**
```bash
twine upload dist/*
```

### 7. Push Changes to Repository

```bash
# Push the version commit
git push origin main
```

## Complete Release Workflow

Here's a complete example for releasing version `0.0.2`:

```bash
# 1. Update version in both files (manually edit pyproject.toml and setup.py)
# 2. Commit changes
git add pyproject.toml setup.py
git commit -m "Bump version to 0.0.2"

# 3. Create and push tag
git tag -a v0.0.2 -m "Release version 0.0.2"
git push origin v0.0.2

# 4. Build packages
rm -rf dist/
uv build

# 5. Test build (optional)
twine check dist/*

# 6. Upload to PyPI
twine upload dist/*

# 7. Push changes
git push origin main
```


## Troubleshooting

### Common Issues

1. **Version mismatch**: Ensure both `pyproject.toml` and `setup.py` have the same version
2. **Build failures**: Check that all dependencies are properly specified
3. **Upload failures**: Verify PyPI credentials and package name availability

