#!/usr/bin/env python3
r"""Pre-publication check script for Template Forge.

This script runs all necessary checks before publishing to PyPI:
- Test suite with coverage
- Type checking (mypy)
- Linting (ruff)
- Security scanning (bandit, safety)
- Version validation
- Build verification
- Documentation checks

Usage:
    python scripts/publish-check.py [--fix] [--skip-slow]

Options:
    --fix         Automatically fix issues where possible (linting)
    --skip-slow   Skip slow check        if failed:
            print(f"\n{Color.RED}{Color.BOLD}[X] NOT READY FOR PUBLISHING{Color.END}")
            print("Fix the failed checks before publishing to PyPI.")
        elif warnings:
            print(f"\n{Color.YELLOW}{Color.BOLD}[!] READY WITH WARNINGS{Color.END}")
            print("Review warnings before publishing to PyPI.")
        else:
            print(f"\n{Color.GREEN}{Color.BOLD}[OK] READY FOR PUBLISHING{Color.END}")
            print("All checks passed! You can publish to PyPI.")ty scans)
    --verbose     Show detailed output
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Color:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


class CheckResult:
    """Result of a check."""

    def __init__(
        self, name: str, passed: bool, message: str = "", warning: bool = False
    ):
        """Initialize a check result.

        Args:
            name: Name of the check
            passed: Whether the check passed
            message: Optional message providing details
            warning: Whether this is a warning rather than a failure
        """
        self.name = name
        self.passed = passed
        self.message = message
        self.warning = warning


class PublishChecker:
    """Run all pre-publication checks."""

    def __init__(
        self, fix: bool = False, skip_slow: bool = False, verbose: bool = False
    ):
        """Initialize the publish checker.

        Args:
            fix: Whether to automatically fix issues where possible
            skip_slow: Whether to skip slow checks like security scans
            verbose: Whether to show detailed output
        """
        self.fix = fix
        self.skip_slow = skip_slow
        self.verbose = verbose
        self.results: List[CheckResult] = []
        self.root_dir = Path(__file__).parent.parent

    def run_command(self, cmd: List[str]) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        if self.verbose:
            print(f"  Running: {' '.join(cmd)}")

        result = subprocess.run(  # noqa: S603 - commands are from trusted source (publish script)
            cmd, capture_output=True, text=True, cwd=self.root_dir
        )

        return result.returncode, result.stdout, result.stderr

    def print_header(self, text: str) -> None:
        """Print a section header."""
        print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.END}")
        print(f"{Color.BOLD}{Color.CYAN}{text}{Color.END}")
        print(f"{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.END}\n")

    def print_check(self, name: str) -> None:
        """Print check name."""
        print(f"{Color.BLUE}> {name}...{Color.END}", end=" ", flush=True)

    def print_result(self, result: CheckResult) -> None:
        """Print check result."""
        if result.passed:
            print(f"{Color.GREEN}[OK] PASSED{Color.END}")
            if result.message:
                print(f"  {result.message}")
        elif result.warning:
            print(f"{Color.YELLOW}[!] WARNING{Color.END}")
            if result.message:
                print(f"  {Color.YELLOW}{result.message}{Color.END}")
        else:
            print(f"{Color.RED}[X] FAILED{Color.END}")
            if result.message:
                print(f"  {Color.RED}{result.message}{Color.END}")

    def add_result(self, result: CheckResult) -> None:
        """Add a check result."""
        self.results.append(result)
        self.print_result(result)

    def check_tests(self) -> None:
        """Run test suite."""
        self.print_check("Running test suite")

        returncode, stdout, _stderr = self.run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
        )

        if returncode == 0:
            # Extract test count
            match = re.search(r"(\d+) passed", stdout)
            count = match.group(1) if match else "unknown"
            self.add_result(CheckResult("Tests", True, f"{count} tests passed"))
        else:
            # Extract failure info
            failures = re.findall(r"FAILED (.*?) -", stdout)
            message = f"Tests failed. Failed tests: {', '.join(failures[:3])}"
            if len(failures) > 3:
                message += f" and {len(failures) - 3} more"
            self.add_result(CheckResult("Tests", False, message))

    def check_coverage(self) -> None:
        """Check test coverage."""
        self.print_check("Checking test coverage")

        returncode, stdout, _stderr = self.run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov=template_forge",
                "--cov-report=term-missing",
                "--cov-fail-under=89",
                "tests/",
            ]
        )

        # Extract coverage percentage
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
        coverage = match.group(1) if match else "unknown"

        if returncode == 0:
            self.add_result(CheckResult("Coverage", True, f"Coverage: {coverage}%"))
        else:
            self.add_result(
                CheckResult(
                    "Coverage", False, f"Coverage {coverage}% is below 89% threshold"
                )
            )

    def check_mypy(self) -> None:
        """Run type checker."""
        self.print_check("Running type checker (mypy)")

        returncode, stdout, _stderr = self.run_command(
            [sys.executable, "-m", "mypy", "template_forge", "--strict"]
        )

        if returncode == 0:
            self.add_result(CheckResult("Type checking", True, "No type errors"))
        else:
            # Extract error count
            match = re.search(r"Found (\d+) error", stdout)
            error_count = match.group(1) if match else "unknown"
            self.add_result(
                CheckResult("Type checking", False, f"Found {error_count} type errors")
            )

    def check_ruff(self) -> None:
        """Run linter."""
        self.print_check("Running linter (ruff)")

        cmd = [sys.executable, "-m", "ruff", "check", "template_forge/"]
        if self.fix:
            cmd.append("--fix")

        returncode, stdout, _stderr = self.run_command(cmd)

        if returncode == 0:
            message = "No linting issues"
            if self.fix and stdout:
                message = "Fixed all auto-fixable issues"
            self.add_result(CheckResult("Linting", True, message))
        else:
            # Count issues
            issue_count = len(
                [
                    line
                    for line in stdout.split("\n")
                    if line.strip() and not line.startswith("Found")
                ]
            )
            self.add_result(
                CheckResult("Linting", False, f"Found {issue_count} linting issues")
            )

    def check_bandit(self) -> None:
        """Run security scanner."""
        if self.skip_slow:
            self.print_check("Security scan (bandit) - SKIPPED")
            self.add_result(
                CheckResult(
                    "Security (bandit)",
                    True,
                    "Skipped (use --skip-slow=false to run)",
                    warning=True,
                )
            )
            return

        self.print_check("Running security scan (bandit)")

        returncode, stdout, _stderr = self.run_command(
            [sys.executable, "-m", "bandit", "-r", "template_forge/", "-q"]
        )

        if returncode == 0:
            self.add_result(
                CheckResult("Security (bandit)", True, "No security issues")
            )
        else:
            # Extract issue count
            match = re.search(
                r"Total issues \(by severity\):.*?(\d+)", stdout, re.DOTALL
            )
            if match:
                message = (
                    "Found security issues. Run 'bandit -r template_forge/' for details"
                )
                self.add_result(CheckResult("Security (bandit)", False, message))
            else:
                self.add_result(
                    CheckResult(
                        "Security (bandit)",
                        False,
                        "Security scan completed with warnings",
                    )
                )

    def check_safety(self) -> None:
        """Check for vulnerable dependencies."""
        if self.skip_slow:
            self.print_check("Dependency security (safety) - SKIPPED")
            self.add_result(
                CheckResult(
                    "Dependency security",
                    True,
                    "Skipped (use --skip-slow=false to run)",
                    warning=True,
                )
            )
            return

        self.print_check("Checking dependency security (safety)")

        # Check if safety is installed
        returncode, _, _ = self.run_command(
            [sys.executable, "-m", "pip", "show", "safety"]
        )

        if returncode != 0:
            self.add_result(
                CheckResult(
                    "Dependency security",
                    True,
                    "safety not installed (install with: pip install safety)",
                    warning=True,
                )
            )
            return

        returncode, stdout, _stderr = self.run_command(
            [sys.executable, "-m", "safety", "check"]
        )

        if returncode == 0 or "No known security vulnerabilities found" in stdout:
            self.add_result(
                CheckResult("Dependency security", True, "No vulnerable dependencies")
            )
        else:
            self.add_result(
                CheckResult(
                    "Dependency security",
                    False,
                    "Found vulnerable dependencies. Run 'safety check' for details",
                )
            )

    def check_version(self) -> None:
        """Validate version format and consistency."""
        self.print_check("Checking version consistency")

        # Read version from __init__.py
        init_file = self.root_dir / "template_forge" / "__init__.py"
        content = init_file.read_text(encoding="utf-8")

        version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)

        if not version_match:
            self.add_result(
                CheckResult("Version", False, "__version__ not found in __init__.py")
            )
            return

        version = version_match.group(1)

        # Check semantic versioning format
        if not re.match(r"^\d+\.\d+\.\d+(-[a-z0-9]+)?$", version):
            self.add_result(
                CheckResult(
                    "Version",
                    False,
                    f"Version '{version}' doesn't follow semantic versioning",
                )
            )
            return

        # Check if it's a development version
        if "-dev" in version:
            self.add_result(
                CheckResult(
                    "Version",
                    False,
                    f"Development version '{version}' - update before publishing",
                    warning=True,
                )
            )
            return

        self.add_result(CheckResult("Version", True, f"Version: {version}"))

    def check_changelog(self) -> None:
        """Check if CHANGELOG.md is updated."""
        self.print_check("Checking CHANGELOG.md")

        changelog = self.root_dir / "CHANGELOG.md"

        if not changelog.exists():
            self.add_result(
                CheckResult("Changelog", False, "CHANGELOG.md not found", warning=True)
            )
            return

        content = changelog.read_text(encoding="utf-8")

        # Check if there's an unreleased section or recent date
        if "[Unreleased]" in content:
            self.add_result(
                CheckResult(
                    "Changelog",
                    False,
                    "CHANGELOG.md has [Unreleased] section - update with release version",
                    warning=True,
                )
            )
            return

        # Check for recent dates (last 30 days would be ideal, but we'll just check format)
        if re.search(r"\[.*?\]\s*-\s*202[0-9]-\d{2}-\d{2}", content):
            self.add_result(
                CheckResult("Changelog", True, "CHANGELOG.md is up to date")
            )
        else:
            self.add_result(
                CheckResult(
                    "Changelog", False, "CHANGELOG.md may need updating", warning=True
                )
            )

    def check_git_status(self) -> None:
        """Check git status for uncommitted changes."""
        self.print_check("Checking git status")

        returncode, stdout, _stderr = self.run_command(["git", "status", "--porcelain"])

        if returncode != 0:
            self.add_result(
                CheckResult(
                    "Git status",
                    False,
                    "Not a git repository or git not available",
                    warning=True,
                )
            )
            return

        if stdout.strip():
            changed_files = [
                line.strip() for line in stdout.split("\n") if line.strip()
            ]
            self.add_result(
                CheckResult(
                    "Git status",
                    False,
                    f"Uncommitted changes in {len(changed_files)} file(s). Commit before publishing.",
                    warning=True,
                )
            )
        else:
            self.add_result(CheckResult("Git status", True, "Working directory clean"))

    def check_build(self) -> None:
        """Test building the package."""
        self.print_check("Testing package build")

        # Clean previous builds
        for pattern in ["dist", "build", "*.egg-info"]:
            for path in self.root_dir.glob(pattern):
                if path.is_dir():
                    import shutil

                    shutil.rmtree(path)

        # Build package
        returncode, _stdout, _stderr = self.run_command([sys.executable, "-m", "build"])

        if returncode != 0:
            self.add_result(CheckResult("Build", False, "Package build failed"))
            return

        # Check dist contents
        dist_dir = self.root_dir / "dist"
        if not dist_dir.exists():
            self.add_result(CheckResult("Build", False, "dist/ directory not created"))
            return

        files = list(dist_dir.glob("*"))
        whl_files = [f for f in files if f.suffix == ".whl"]
        tar_files = [f for f in files if f.name.endswith(".tar.gz")]

        if not whl_files or not tar_files:
            self.add_result(
                CheckResult("Build", False, "Missing wheel or source distribution")
            )
            return

        # Check with twine
        returncode, _stdout, _stderr = self.run_command(
            [sys.executable, "-m", "twine", "check", "dist/*"]
        )

        if returncode == 0:
            self.add_result(
                CheckResult(
                    "Build",
                    True,
                    f"Built {len(whl_files)} wheel(s) and {len(tar_files)} source dist(s)",
                )
            )
        else:
            self.add_result(CheckResult("Build", False, "twine check failed"))

    def check_readme(self) -> None:
        """Check README.md exists and has content."""
        self.print_check("Checking README.md")

        readme = self.root_dir / "README.md"

        if not readme.exists():
            self.add_result(CheckResult("README", False, "README.md not found"))
            return

        content = readme.read_text(encoding="utf-8")

        # Check minimum length
        if len(content) < 500:
            self.add_result(
                CheckResult(
                    "README",
                    False,
                    "README.md seems too short (< 500 chars)",
                    warning=True,
                )
            )
            return

        # Check for key sections
        required_sections = ["install", "usage", "example"]
        missing = [s for s in required_sections if s.lower() not in content.lower()]

        if missing:
            self.add_result(
                CheckResult(
                    "README",
                    False,
                    f"README.md may be missing sections: {', '.join(missing)}",
                    warning=True,
                )
            )
        else:
            self.add_result(CheckResult("README", True, "README.md looks good"))

    def check_examples(self) -> None:
        """Check that examples exist and are documented."""
        self.print_check("Checking examples")

        examples_dir = self.root_dir / "examples"

        if not examples_dir.exists():
            self.add_result(
                CheckResult(
                    "Examples", False, "examples/ directory not found", warning=True
                )
            )
            return

        example_dirs = [
            d
            for d in examples_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        if not example_dirs:
            self.add_result(
                CheckResult("Examples", False, "No examples found", warning=True)
            )
            return

        # Check each example has a README
        missing_readme = [
            d.name for d in example_dirs if not (d / "README.md").exists()
        ]

        if missing_readme:
            self.add_result(
                CheckResult(
                    "Examples",
                    False,
                    f"Examples missing README.md: {', '.join(missing_readme)}",
                    warning=True,
                )
            )
        else:
            self.add_result(
                CheckResult(
                    "Examples", True, f"Found {len(example_dirs)} documented examples"
                )
            )

    def run_all_checks(self) -> bool:
        """Run all checks and return overall success."""
        self.print_header("Template Forge - Pre-Publication Checks")

        print(f"Root directory: {self.root_dir}")
        print(f"Fix mode: {self.fix}")
        print(f"Skip slow checks: {self.skip_slow}")

        # Documentation checks
        self.print_header("Documentation")
        self.check_readme()
        self.check_changelog()
        self.check_examples()

        # Version checks
        self.print_header("Version")
        self.check_version()

        # Git checks
        self.print_header("Git")
        self.check_git_status()

        # Code quality checks
        self.print_header("Code Quality")
        self.check_tests()
        self.check_coverage()
        self.check_mypy()
        self.check_ruff()

        # Security checks
        self.print_header("Security")
        self.check_bandit()
        self.check_safety()

        # Build checks
        self.print_header("Package Build")
        self.check_build()

        # Print summary
        self.print_summary()

        # Return overall success
        failures = [r for r in self.results if not r.passed and not r.warning]
        return len(failures) == 0

    def print_summary(self) -> None:
        """Print summary of all checks."""
        self.print_header("Summary")

        passed = [r for r in self.results if r.passed and not r.warning]
        warnings = [r for r in self.results if r.warning]
        failed = [r for r in self.results if not r.passed and not r.warning]

        print(f"{Color.GREEN}[OK] Passed: {len(passed)}{Color.END}")
        print(f"{Color.YELLOW}[!] Warnings: {len(warnings)}{Color.END}")
        print(f"{Color.RED}[X] Failed: {len(failed)}{Color.END}")

        if warnings:
            print(f"\n{Color.YELLOW}Warnings:{Color.END}")
            for r in warnings:
                print(f"  • {r.name}: {r.message}")

        if failed:
            print(f"\n{Color.RED}Failed:{Color.END}")
            for r in failed:
                print(f"  • {r.name}: {r.message}")

        print()

        if failed:
            print(f"{Color.RED}{Color.BOLD}❌ NOT READY FOR PUBLISHING{Color.END}")
            print("Fix the failed checks before publishing to PyPI.")
        elif warnings:
            print(f"{Color.YELLOW}{Color.BOLD}⚠️  READY WITH WARNINGS{Color.END}")
            print("Review warnings before publishing to PyPI.")
        else:
            print(f"{Color.GREEN}{Color.BOLD}✅ READY FOR PUBLISHING{Color.END}")
            print("All checks passed! You can publish to PyPI.")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run pre-publication checks for Template Forge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues where possible (linting)",
    )
    parser.add_argument(
        "--skip-slow", action="store_true", help="Skip slow checks (security scans)"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    checker = PublishChecker(
        fix=args.fix, skip_slow=args.skip_slow, verbose=args.verbose
    )
    success = checker.run_all_checks()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
