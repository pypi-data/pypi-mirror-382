# Glob Patterns Example

This example demonstrates **REQ-ADV-001**: Processing multiple input files using glob patterns.

## Feature

Template Forge can process multiple files at once using glob patterns in the configuration:

```yaml
inputs:
  - path: "data/*.json"        # All JSON files in data/
  - path: "configs/**/*.yaml"  # All YAML files recursively
```

## What This Example Shows

1. **Multiple File Processing**: Using glob patterns to process multiple input files
2. **Merge Strategies**: Combining data from multiple files (shallow vs deep merge)
3. **Token Namespacing**: Each file's data is available under its filename

## Files

- `config.yaml` - Configuration with glob patterns
- `data/user1.json` - First user data file
- `data/user2.json` - Second user data file
- `data/user3.json` - Third user data file
- `templates/user-report.md.j2` - Template that uses data from all files
- `templates/combined-config.yaml.j2` - Template showing data merging

## Running the Example

```bash
# From this directory
template-forge config.yaml

# Or from project root
template-forge examples/glob-patterns/config.yaml
```

## Expected Output

- `output/user-report.md` - Report combining all user data
- `output/combined-config.yaml` - Merged configuration from all files

## Key Features Demonstrated

### 1. Glob Pattern Matching

```yaml
inputs:
  - path: "data/*.json"
    format: json
```

This will process all `.json` files in the `data/` directory.

### 2. Merge Strategies

```yaml
inputs:
  - path: "data/*.json"
    merge_strategy: deep  # Deep merge for nested structures
```

- `shallow`: Top-level keys only (default)
- `deep`: Recursive merge of nested dictionaries

### 3. Token Access

Each file's data is namespaced by filename:

```jinja2
{{ user1.name }}  {# From user1.json #}
{{ user2.name }}  {# From user2.json #}
{{ user3.name }}  {# From user3.json #}
```

### 4. Merged Tokens

With deep merge, common structures are combined:

```jinja2
{% for user in users %}  {# Merged list from all files #}
  - {{ user.name }}: {{ user.email }}
{% endfor %}
```

## Requirement Coverage

- ✅ **REQ-ADV-001**: Glob pattern support for multiple file processing
- ✅ **REQ-ADV-006**: Merge strategies (shallow and deep)
- ✅ **REQ-EXT-027**: Support multiple input files in a single configuration

## Use Cases

1. **Multi-Environment Configs**: Process dev.json, staging.json, prod.json
2. **Batch Processing**: Generate reports from multiple data files
3. **Data Aggregation**: Combine data from multiple sources
4. **Team Configurations**: Merge settings from multiple team members
