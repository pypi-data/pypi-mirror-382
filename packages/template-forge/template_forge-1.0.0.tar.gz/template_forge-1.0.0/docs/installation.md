# Installation

## From PyPI (Recommended)

Install Template Forge using pip:

```bash
pip install template-forge
```

## From Source

For development or to get the latest features:

```bash
git clone https://github.com/CarloFornari/template_forge.git
cd template_forge
pip install -e ".[dev]"
```

## Requirements

- Python 3.8 or higher
- PyYAML 6.0.1+
- Jinja2 3.1.2+

## Verification

Verify the installation:

```bash
template-forge --help
```

Or in Python:

```python
import template_forge
print(template_forge.__version__)
```