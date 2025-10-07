# Basic Template Forge Example

This example demonstrates the fundamental usage of Template Forge with JSON input and basic template rendering.

## Files in this example:

- `settings.json` - Sample application configuration in JSON format
- `config.yaml` - Template Forge configuration file
- `config_advanced.yaml` - Advanced configuration with static tokens
- `config.ini.j2` - Jinja2 template for generating INI configuration
- `README.md.j2` - Jinja2 template for generating documentation

## Input Data (`settings.json`)

Contains application configuration including:
- Application metadata (name, version, description)
- Database connection settings
- Feature flags and environment settings

## Usage

Run the basic example:

```bash
template-forge config.yaml
```

Run the advanced example:

```bash
template-forge config_advanced.yaml
```

## Expected Output

The command will generate:
- `output/config.ini` - Application configuration file
- `output/README.md` - Project documentation

## Key Concepts Demonstrated

1. **JSON Parsing**: Extract tokens from JSON configuration
2. **Dot Notation**: Access nested values using `app.name`, `database.host`
3. **Template Rendering**: Generate text files from Jinja2 templates
4. **Static Tokens**: Add compile-time values to templates
5. **Multiple Templates**: Generate multiple output files from one configuration