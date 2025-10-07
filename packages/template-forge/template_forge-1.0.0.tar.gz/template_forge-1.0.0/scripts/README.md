# Scripts Directory

This directory contains utility scripts for Template Forge development and publishing.

## 📋 Available Scripts

### `publish-check.py`

**Pre-publication verification script** that runs all necessary checks before publishing to PyPI.

#### What It Checks

✅ **Documentation**
- README.md exists and has content
- CHANGELOG.md is updated
- Examples are documented

✅ **Version**
- Semantic versioning format
- Not a development version

✅ **Git**
- No uncommitted changes
- Working directory clean

✅ **Code Quality**
- All tests pass (627 tests)
- Test coverage ≥ 90%
- Type checking (mypy --strict)
- Linting (ruff)

✅ **Security**
- Security scan (bandit)
- Dependency vulnerabilities (safety)

✅ **Build**
- Package builds successfully
- Wheel and source distributions created
- twine validation passes

#### Usage

```bash
# Basic check (skips slow security scans)
python scripts/publish-check.py --skip-slow

# Full check (includes security scans)
python scripts/publish-check.py

# With auto-fix for linting
python scripts/publish-check.py --fix

# Verbose output
python scripts/publish-check.py --verbose

# Help
python scripts/publish-check.py --help
```

#### Options

- `--fix` - Automatically fix linting issues where possible
- `--skip-slow` - Skip security scans (faster for quick checks)
- `--verbose` - Show detailed command output

#### Output

The script provides:
- ✅ **Color-coded results** for each check
- 📊 **Summary** of passed/warned/failed checks
- 🎯 **Final verdict**: Ready/Not Ready for publishing
- 💡 **Actionable messages** for failures

#### Exit Codes

- `0` - All checks passed (ready to publish)
- `1` - Some checks failed (not ready to publish)

#### Example Output

```
======================================================================
Template Forge - Pre-Publication Checks
======================================================================

Root directory: /path/to/template_forge
Fix mode: False
Skip slow checks: True

======================================================================
Documentation
======================================================================

> Checking README.md... [OK] PASSED
  README.md looks good
> Checking CHANGELOG.md... [OK] PASSED
  CHANGELOG.md is up to date
> Checking examples... [OK] PASSED
  Found 9 documented examples

...

======================================================================
Summary
======================================================================

[OK] Passed: 10
[!] Warnings: 2
[X] Failed: 0

[OK] READY FOR PUBLISHING
All checks passed! You can publish to PyPI.
```

#### Integration with CI/CD

Add to your GitHub Actions workflow:

```yaml
- name: Pre-publish checks
  run: python scripts/publish-check.py --skip-slow
```

#### Before Publishing Checklist

Run this script and ensure:
1. All code quality checks pass
2. Test coverage is ≥ 90%
3. No uncommitted changes
4. CHANGELOG.md is updated
5. Version is not a dev version
6. All security checks pass (run without --skip-slow)

## 🚀 Adding New Scripts

When adding new scripts:

1. **Add executable shebang**: `#!/usr/bin/env python3`
2. **Add docstring** explaining purpose and usage
3. **Include argparse** for command-line options
4. **Document in this README**
5. **Add to `.gitignore` any output files**

### Script Template

```python
#!/usr/bin/env python3
"""Brief description of what the script does.

Usage:
    python scripts/script-name.py [options]
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("--option", help="Option description")
    
    args = parser.parse_args()
    
    # Script logic here
    
    return 0  # 0 = success, 1 = failure


if __name__ == "__main__":
    sys.exit(main())
```

## 📚 Related Documentation

- **Publishing Guide**: `docs/publishing.md`
- **Development Guide**: `DEVELOPMENT.md`
- **Contributing**: `CONTRIBUTING.md`
