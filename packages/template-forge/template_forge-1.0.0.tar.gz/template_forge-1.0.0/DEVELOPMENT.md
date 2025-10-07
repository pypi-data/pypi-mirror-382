# Development Setup

This document describes the development setup for Template Forge contributors.

## Requirements

- Python 3.8 or higher
- Git
- Pre-commit (for code quality)

## Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CarloFornari/template_forge.git
   cd template_forge
   ```

2. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Development Tools

### Code Quality

We use modern Python development tools:

- **Ruff**: Ultra-fast linter and formatter (replaces black + flake8)
- **MyPy**: Static type checking
- **Pre-commit**: Automated code quality checks
- **Bandit**: Security vulnerability scanning

### Running Quality Checks

```bash
# Run all linting and formatting
hatch run lint:check

# Auto-fix issues
hatch run lint:fix

# Run tests with coverage
hatch run test:cov

# Type checking
mypy template_forge/

# Security scanning
bandit -r template_forge/
```

### Using Hatch Environments

We use Hatch for environment management:

```bash
# List available environments
hatch env show

# Run tests
hatch run test:run

# Run with specific Python version
hatch run +py=3.11 test:run

# Build documentation
hatch run docs:build
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=template_forge

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v
```

### Test Categories

Tests are marked with categories:
- `unit`: Fast unit tests
- `integration`: Integration tests
- `slow`: Long-running tests

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

## Performance Monitoring

Run benchmarks to measure performance:

```bash
python benchmarks.py
```

This will generate `benchmark_results.json` with detailed performance metrics.

## Documentation

### Building Documentation

```bash
hatch run docs:build
```

### Serving Documentation Locally

```bash
hatch run docs:serve
```

Then visit http://localhost:8000

## Release Process

1. Update version in `template_forge/__init__.py`
2. Update `CHANGELOG.md`
3. Create a Git tag: `git tag v1.0.1`
4. Push tag: `git push origin v1.0.1`
5. GitHub Actions will automatically build and publish to PyPI

## CI/CD Pipeline

Our GitHub Actions workflow includes:

- **Testing**: Multi-platform testing (Linux, Windows, macOS) across Python 3.8-3.12
- **Code Quality**: Linting, formatting, and type checking
- **Security**: Vulnerability scanning with Bandit and Safety
- **Documentation**: Automated documentation building
- **Publishing**: Automatic PyPI publishing on releases

## Contributing Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run quality checks: `hatch run lint:check`
5. Run tests: `hatch run test:cov`
6. Commit changes: `git commit -m "feat: add amazing feature"`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Maintenance tasks

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check the documentation at https://template-forge.readthedocs.io