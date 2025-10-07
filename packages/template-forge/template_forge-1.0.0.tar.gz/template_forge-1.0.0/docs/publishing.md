# 📦 Publishing Template Forge to PyPI

This guide explains how to publish Template Forge to the Python Package Index (PyPI).

---

## Prerequisites

1. **PyPI Account**: [Register at pypi.org](https://pypi.org/account/register/)
2. **Test PyPI Account** (optional but recommended): [Register at test.pypi.org](https://test.pypi.org/account/register/)
3. **API Tokens**: Create API tokens for both PyPI and Test PyPI

---

## Pre-Publication Checklist

### ✅ Automated Checks

**Use the publish-check script for automated verification:**

```bash
# Quick check (skips slow security scans)
python scripts/publish-check.py --skip-slow

# Full check (includes security scans)
python scripts/publish-check.py

# With auto-fix for linting
python scripts/publish-check.py --fix
```

The script checks:
- ✅ All tests pass (627 tests)
- ✅ Test coverage ≥ 90%
- ✅ Type checking (mypy --strict)
- ✅ Linting (ruff)
- ✅ Security scans (bandit, safety)
- ✅ Version format and consistency
- ✅ Git status (no uncommitted changes)
- ✅ Documentation (README, CHANGELOG, examples)
- ✅ Package builds successfully

### ✅ Manual Checks

If not using the automated script, run these manually:

### ✅ Code Quality

```bash
# Run all tests
pytest

# Check test coverage
pytest --cov=template_forge --cov-report=html
# or line coverage in terminal text format 
pytest --cov=template_forge --cov-report=term-missing tests/

# Run linter
ruff check template_forge/

# Run type checker
mypy template_forge/

# Security scan
bandit -r template_forge/
safety scan
```

### ✅ Documentation

- [ ] README.md is complete and PyPI-friendly
- [ ] QUICKSTART.md provides a 5-minute tutorial
- [ ] docs/getting-started.md is comprehensive
- [ ] All examples run without errors
- [ ] API documentation is up to date
- [ ] CHANGELOG.md lists all changes

### ✅ Version Management

1. Update version in `template_forge/__init__.py`:
```python
__version__ = "1.0.0"  # Use semantic versioning
```

2. Update CHANGELOG.md:
```markdown
## [1.0.0] - 2025-10-04

### Added
- Initial release
- Universal data support (JSON, YAML, XML, ARXML)
- Full Jinja2 template processing
- Code preservation with markers
- Hooks and automation
- 7 comprehensive examples
- Complete documentation
```

3. Create git tag:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### ✅ Package Metadata

Check `pyproject.toml`:
- [ ] Correct version
- [ ] Accurate description
- [ ] Valid classifiers
- [ ] All URLs work
- [ ] Dependencies are correct
- [ ] Keywords are relevant

---

## Build the Package

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Build Distribution Files

```bash
# Install build tools
pip install --upgrade build twine

# Build the package
python -m build
```

This creates:
- `dist/template-forge-X.Y.Z-py3-none-any.whl` - Wheel distribution
- `dist/template-forge-X.Y.Z.tar.gz` - Source distribution

### 3. Check the Build

```bash
# Check package metadata
twine check dist/*

# List package contents
tar -tzf dist/template-forge-*.tar.gz
```

Verify that:
- [ ] README.md is included
- [ ] LICENSE is included
- [ ] examples/ directory is included
- [ ] All Python files are present
- [ ] No unwanted files (e.g., `__pycache__`, `.pyc`)

---

## Test on Test PyPI (Recommended)

### 1. Upload to Test PyPI

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for your Test PyPI API token.

### 2. Test Installation

```bash
# Create a clean virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    template-forge

# Test it works
template-forge --version

# Run an example
cd examples/basic
template-forge config.yaml

# Clean up
deactivate
rm -rf test_env
```

### 3. Check Test PyPI Page

Visit: `https://test.pypi.org/project/template-forge/`

Verify:
- [ ] README renders correctly
- [ ] Links work
- [ ] Metadata is correct
- [ ] Version is correct

---

## Publish to PyPI

### 1. Final Verification

```bash
# Make absolutely sure everything is ready
pytest
git status  # Should be clean
git log -1  # Verify latest commit
```

### 2. Upload to PyPI

```bash
twine upload dist/*
```

Enter your PyPI API token when prompted.

### 3. Verify Publication

Visit: `https://pypi.org/project/template-forge/`

Test installation:
```bash
# In a fresh environment
pip install template-forge
template-forge --version
```

---

## Post-Publication

### 1. Announce the Release

- [ ] Create GitHub release with changelog
- [ ] Update project README if needed
- [ ] Share on social media/communities
- [ ] Update documentation links

### 2. Monitor

- [ ] Check PyPI download stats
- [ ] Monitor GitHub issues
- [ ] Respond to community feedback

### 3. Prepare for Next Release

```bash
# Bump version for development
# In template_forge/__init__.py:
__version__ = "1.1.0-dev"

# Commit
git add template_forge/__init__.py
git commit -m "Bump version to 1.1.0-dev"
git push
```

---

## Automation (Optional)

### GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Store your PyPI API token in GitHub Secrets as `PYPI_API_TOKEN`.

---

## Troubleshooting

### Build Errors

**Problem**: Missing files in distribution
**Solution**: Check `MANIFEST.in` and ensure all needed files are included

**Problem**: Wrong version
**Solution**: Update `template_forge/__init__.py` and rebuild

### Upload Errors

**Problem**: `403 Forbidden` error
**Solution**: Check your API token permissions

**Problem**: Version already exists
**Solution**: Bump version number (you can't overwrite existing versions)

**Problem**: File size too large
**Solution**: Ensure you're not including unnecessary files (check `.gitignore` and `MANIFEST.in`)

### Installation Errors

**Problem**: Dependencies not installing
**Solution**: Check `dependencies` in `pyproject.toml`

**Problem**: Import errors
**Solution**: Verify package structure and `__init__.py` files

---

## Best Practices

1. **Semantic Versioning**: Use MAJOR.MINOR.PATCH
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

2. **Changelog**: Always maintain CHANGELOG.md

3. **Testing**: Never publish without passing tests

4. **Git Tags**: Tag every release

5. **Documentation**: Keep docs in sync with code

6. **Deprecation**: Warn users before removing features

---

## Quick Reference

```bash
# Complete publish workflow

# 1. Update version
vim template_forge/__init__.py

# 2. Update changelog
vim CHANGELOG.md

# 3. Run tests
pytest

# 4. Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# 5. Check build
twine check dist/*

# 6. Test on Test PyPI (optional)
twine upload --repository testpypi dist/*

# 7. Publish to PyPI
twine upload dist/*

# 8. Tag release
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0

# 9. Create GitHub release
```

---

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [Writing a Good README](https://packaging.python.org/guides/making-a-pypi-friendly-readme/)

---

**Ready to share Template Forge with the world!** 🚀
