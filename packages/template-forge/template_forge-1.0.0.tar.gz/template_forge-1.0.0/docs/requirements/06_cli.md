# Command-Line Interface - Requirements

## 1. General

**REQ-CLI-001**: The system shall provide a command-line interface (CLI) for all operations.

**REQ-CLI-002**: The CLI shall be invoked using the `template-forge` command.

**REQ-CLI-003**: The CLI shall suppor**REQ-CLI-080**: The `--help` option shall dis**REQ-CLI-100**: The `--validate` flag shall validate the configuration without generating files.

**REQ-CLI-101**: Validation mode shall check:
- Configuration file syntax (valid YAML)
- All referenced input files exist
- All referenced template files exist
- Token extraction keys are valid

**REQ-CLI-102**: Validation mode shall exit with code 0 if validation succeeds.

**REQ-CLI-103**: Validation mode shall exit with code 1 if validation fails.

**REQ-CLI-104**: Validation mode shall display a success message: "Configuration is valid"

**REQ-CLI-105**: Validation mode shall not create any output files or directories.

## 12. Version Information

**REQ-CLI-110**: The `--version` option shall display the current version number.

**REQ-CLI-111**: Version information shall follow the format: "Template Forge X.Y.Z"

**REQ-CLI-112**: The version shall match the version defined in the package metadata.

## 13. Configuration Validation

**REQ-CLI-120**: The CLI shall always validate the configuration file before processing (even in normal mode).

**REQ-CLI-121**: If the configuration file does not exist, the CLI shall display an error and exit with code 1.

**REQ-CLI-122**: If the configuration file is invalid, the CLI shall display an error and exit with code 1.

**REQ-CLI-123**: Configuration validation shall occur before any file generation or processing.

**REQ-CLI-124**: Validation messages shall include: "Validating configuration: <path>"

**REQ-CLI-125**: After successful validation: "Configuration valid. Starting generation..."

## 14. Logging

**REQ-CLI-130**: The CLI shall use Python's standard `logging` module for all output.nsive help message including:
- Tool name and description
- Key features summary
- Usage syntax
- Supported file formats
- Links to documentation and examples

**REQ-CLI-081**: The help message shall use color coding when output to a terminal (TTY).

**REQ-CLI-082**: The help message shall gracefully degrade to plain text when piped or redirected.

**REQ-CLI-083**: The help message shall fit within 80-100 character width for readability.

**REQ-CLI-084**: The help message shall include the GitHub repository link for examples and documentation.

## 10. Verbose Mode

**REQ-CLI-090**: The `-v` or `--verbose` flag shall enable debug-level logging.ython -m template_forge.cli` as an alternative.

**REQ-CLI-004**: The CLI shall return appropriate exit codes (0 for success, non-zero for errors).

## 2. Command Syntax

**REQ-CLI-010**: The basic command syntax shall be: `template-forge [config_file] [options]`

**REQ-CLI-011**: The configuration file path shall be an optional positional argument.

**REQ-CLI-012**: If no configuration file is specified, the system shall use automatic configuration discovery (see REQ-CFG-080-085).

**REQ-CLI-013**: The configuration file path may be relative or absolute.

**REQ-CLI-014**: Relative configuration file paths shall be resolved relative to the current working directory.

## 3. Options and Flags

**REQ-CLI-020**: The CLI shall support the following options:
- `-h, --help`: Display help message and exit
- `-v, --verbose`: Enable verbose logging output
- `--version`: Display version information and exit
- `--validate`: Validate configuration only, do not generate files
- `--validate-templates`: Validate template syntax without generation
- `--dry-run`: Preview operations without writing files
- `--show-variables`: Display all resolved variables
- `--show-variables=<template>`: Show variables for specific template
- `--diff`: Show differences before applying changes
- `--no-color`: Disable colored output
- `--init`: Create new configuration interactively
- `--init=<template>`: Create configuration from template (basic, python, cpp, web)
- `--no-hooks`: Skip post-generation hook execution
- `--config <path>`: Explicitly specify configuration file path

**REQ-CLI-021**: Short and long forms of options shall be equivalent in functionality.

**REQ-CLI-022**: Options may appear before or after the configuration file argument.

**REQ-CLI-023**: Multiple short options cannot be combined (e.g., `-vh` is not supported).

**REQ-CLI-024**: The CLI shall support automatic configuration discovery if no config file is specified.

## 4. Dry Run Mode

**REQ-CLI-030**: The CLI shall support a `--dry-run` flag to preview operations without making changes.

**REQ-CLI-031**: In dry run mode, the system shall:
- Validate configuration
- Process all input files and extract tokens
- Render templates to memory
- Display what files would be created/modified
- NOT write any output files to disk

**REQ-CLI-032**: Dry run output shall show:
- List of files that would be created
- List of files that would be modified (if they already exist)
- File paths and sizes
- Summary statistics (X files would be created)

**REQ-CLI-033**: Dry run mode shall use a distinctive indicator for each action:
```
[DRY RUN] Would create: src/main.cpp (2.5 KB)
[DRY RUN] Would modify: README.md (1.2 KB)
[DRY RUN] Would create: config/settings.json (450 bytes)
```

**REQ-CLI-034**: Dry run mode shall exit with code 0 if all operations would succeed.

**REQ-CLI-035**: Dry run mode shall exit with code 1 if any operation would fail (e.g., template error).

**REQ-CLI-036**: Dry run mode shall work in combination with `--verbose` for detailed preview.

## 5. Variable Preview

**REQ-CLI-040**: The CLI shall support a `--show-variables` flag to display all resolved variables.

**REQ-CLI-041**: Variable preview shall show:
- All static tokens with their values
- All extracted tokens with their values and source files
- Template-specific token overrides
- Final merged token context for each template

**REQ-CLI-042**: Variable preview output format:
```
Static Tokens:
  author: "John Doe"
  year: 2025
  license: "MIT"

Extracted from data.json:
  app_name: "MyApp"
  version: "1.0.0"
  modules: ["auth", "api", "database"]

Template: app.py.j2
  All available variables:
    - author (string): "John Doe"
    - year (number): 2025
    - license (string): "MIT"
    - app_name (string): "MyApp"
    - version (string): "1.0.0"
    - modules (list): ["auth", "api", "database"]
```

**REQ-CLI-043**: Variable preview shall support a `--show-variables=<template>` syntax to show variables for a specific template only.

**REQ-CLI-044**: Variable preview shall indicate the type of each variable (string, number, list, dict).

**REQ-CLI-045**: Variable preview shall show nested structure for dict and list types.

**REQ-CLI-046**: Variable preview shall highlight which tokens would be undefined in templates.

**REQ-CLI-047**: Variable preview can be combined with `--dry-run` to show both variables and file operations.

## 6. Diff Preview

**REQ-CLI-050**: The CLI shall support a `--diff` flag to show differences before applying changes.

**REQ-CLI-051**: Diff preview shall only show differences for files that already exist.

**REQ-CLI-052**: Diff preview shall use unified diff format (similar to `git diff`).

**REQ-CLI-053**: Diff preview shall respect code preservation markers when showing diffs.

**REQ-CLI-054**: Diff preview output format:
```
Diff for README.md:
--- README.md (existing)
+++ README.md (new)
@@ -1,4 +1,4 @@
 # MyApp
-Version: 1.0.0
+Version: 1.1.0
 
 A sample application.
```

**REQ-CLI-055**: Diff preview shall use colors when output is a terminal:
- Red for removed lines (lines starting with `-`)
- Green for added lines (lines starting with `+`)
- Cyan for line number headers (lines starting with `@@`)

**REQ-CLI-056**: Diff preview shall support a `--no-color` flag to disable colored output.

**REQ-CLI-057**: Diff preview shall show a summary:
```
Summary:
  README.md: 1 addition, 1 deletion
  src/main.cpp: 15 additions, 3 deletions
  Total: 2 files changed, 16 additions(+), 4 deletions(-)
```

**REQ-CLI-058**: Diff preview can be combined with `--dry-run` to preview without applying.

**REQ-CLI-059**: Without `--dry-run`, diff preview shall wait for user confirmation before applying changes.

## 7. Interactive Initialization

**REQ-CLI-060**: The CLI shall support an `--init` flag to create a new configuration interactively.

**REQ-CLI-061**: Interactive init shall prompt for:
- Project name
- Input file paths (optional, can skip)
- Template directory (default: `./templates`)
- Output directory (default: `./output`)
- Whether to create example templates

**REQ-CLI-062**: Interactive init shall validate user inputs:
- Paths must be valid and accessible
- File references must exist
- Directory paths will be created if they don't exist

**REQ-CLI-063**: Interactive init shall provide sensible defaults shown in brackets:
```
Project name: [my-project]
Template directory [./templates]:
Output directory [./output]:
```

**REQ-CLI-064**: Interactive init shall support pressing Enter to accept defaults.

**REQ-CLI-065**: Interactive init shall create:
- A `config.yaml` file with the user's inputs
- Template directory (if it doesn't exist)
- Example template files (if requested)
- Example input files (if requested)

**REQ-CLI-066**: Interactive init shall not overwrite existing `config.yaml` without confirmation:
```
config.yaml already exists. Overwrite? [y/N]:
```

**REQ-CLI-067**: Interactive init shall display next steps after creation:
```
✓ Configuration created: config.yaml
✓ Template directory created: templates/
✓ Example template created: templates/example.txt.j2

Next steps:
  1. Edit templates/example.txt.j2
  2. Run: template-forge config.yaml
  3. See output in output/
```

**REQ-CLI-068**: Interactive init shall support `--init=<template>` to create from a template:
- `--init=basic`: Minimal configuration
- `--init=python`: Python project template
- `--init=cpp`: C++ project template
- `--init=web`: Web project template

## 8. Better Error Context

**REQ-CLI-070**: Error messages shall include actionable context and suggestions.

**REQ-CLI-071**: File not found errors shall suggest:
- Checking the file path
- Using absolute path if relative path fails
- Verifying working directory

**REQ-CLI-072**: Template errors shall show:
- Template file name and path
- Line number where error occurred
- Snippet of problematic code (3 lines before/after)
- Specific error type and message
- Suggestion for fix

**REQ-CLI-073**: Undefined variable errors shall show:
- Variable name
- Template where it's used
- Available variables in context
- Suggestion to add to static_tokens or inputs

**REQ-CLI-074**: YAML syntax errors shall show:
- Configuration file path
- Line and column number
- Problematic YAML snippet
- What was expected vs. what was found
- Link to YAML validator tool

**REQ-CLI-075**: Example enhanced error messages:
```
ERROR: Template rendering failed
  Template: templates/main.cpp.j2 (line 42)
  Error: Undefined variable 'module_version'
  
  Snippet:
    40 | const char* VERSION = "{{ version }}";
    41 | const char* MODULE = "{{ module_name }}";
  > 42 | const char* MODULE_VERSION = "{{ module_version }}";
    43 | 
    44 | int main() {
  
  Available variables in this template:
    - version, module_name, author, year
  
  Suggestion:
    Add 'module_version' to your config.yaml:
    
    static_tokens:
      module_version: "1.0.0"
```

**REQ-CLI-076**: Error messages shall use color coding when output to terminal:
- Red for "ERROR:" prefix
- Yellow for warnings
- Cyan for file paths and line numbers
- Bold for suggestions

## 9. Help Message

**REQ-CLI-080**: The `--help` option shall display a comprehensive help message including:
- Tool name and description
- Key features summary
- Usage syntax
- Supported file formats
- Links to documentation and examples

**REQ-CLI-031**: The help message shall use color coding when output to a terminal (TTY).

**REQ-CLI-032**: The help message shall gracefully degrade to plain text when piped or redirected.

**REQ-CLI-033**: The help message shall fit within 80-100 character width for readability.

**REQ-CLI-034**: The help message shall include the GitHub repository link for examples and documentation.

## 5. Verbose Mode

**REQ-CLI-090**: The `-v` or `--verbose` flag shall enable debug-level logging.

**REQ-CLI-091**: In verbose mode, all DEBUG, INFO, WARNING, and ERROR messages shall be displayed.

**REQ-CLI-092**: In normal mode (non-verbose), only INFO, WARNING, and ERROR messages shall be displayed.

**REQ-CLI-093**: Verbose mode shall include stack traces for exceptions.

**REQ-CLI-094**: Verbose mode shall show detailed token extraction and template processing steps.

## 11. Validation Mode

**REQ-CLI-100**: The `--validate` flag shall validate the configuration without generating files.

**REQ-CLI-051**: Validation mode shall check:
- Configuration file syntax (valid YAML)
- All referenced input files exist
- All referenced template files exist
- Token extraction keys are valid

**REQ-CLI-052**: Validation mode shall exit with code 0 if validation succeeds.

**REQ-CLI-053**: Validation mode shall exit with code 1 if validation fails.

**REQ-CLI-054**: Validation mode shall display a success message: "Configuration is valid"

**REQ-CLI-055**: Validation mode shall not create any output files or directories.

## 7. Version Information

**REQ-CLI-060**: The `--version` option shall display the current version number.

**REQ-CLI-061**: Version information shall follow the format: "Template Forge X.Y.Z"

**REQ-CLI-062**: The version shall match the version defined in the package metadata.

## 8. Configuration Validation

**REQ-CLI-070**: The CLI shall always validate the configuration file before processing (even in normal mode).

**REQ-CLI-071**: If the configuration file does not exist, the CLI shall display an error and exit with code 1.

**REQ-CLI-072**: If the configuration file is invalid, the CLI shall display an error and exit with code 1.

**REQ-CLI-073**: Configuration validation shall occur before any file generation or processing.

**REQ-CLI-074**: Validation messages shall include: "Validating configuration: <path>"

**REQ-CLI-075**: After successful validation: "Configuration valid. Starting generation..."

## 9. Logging

**REQ-CLI-130**: The CLI shall use Python's standard `logging` module for all output.

**REQ-CLI-131**: Log messages shall include timestamp, logger name, and level.

**REQ-CLI-132**: Log format shall be: `YYYY-MM-DD HH:MM:SS,mmm - logger - LEVEL - message`

**REQ-CLI-133**: The CLI shall log to standard output (stdout).

**REQ-CLI-134**: Error messages shall be clearly distinguishable with ERROR level.

## 15. Exit Codes

**REQ-CLI-140**: The CLI shall use the following exit codes:
- `0`: Success (generation or validation completed without errors)
- `1`: Error (configuration invalid, file not found, processing error)
- `130`: User interrupt (Ctrl+C)

**REQ-CLI-141**: All exceptions shall be caught and converted to appropriate exit codes.

**REQ-CLI-142**: The CLI shall not crash with unhandled exceptions in normal operation.

## 16. Error Handling

**REQ-CLI-150**: The CLI shall catch `KeyboardInterrupt` (Ctrl+C) and exit gracefully.

**REQ-CLI-151**: On keyboard interrupt, the CLI shall log: "Operation cancelled by user"

**REQ-CLI-152**: Configuration file errors shall display the file path and error description.

**REQ-CLI-153**: Template processing errors shall display the template name and error details.

**REQ-CLI-154**: Input file errors shall display the input file path and error details.

**REQ-CLI-155**: In verbose mode, full stack traces shall be displayed for debugging.

**REQ-CLI-156**: In normal mode, stack traces shall be suppressed for cleaner output.

## 17. File Path Handling

**REQ-CLI-160**: The CLI shall accept both relative and absolute paths for the configuration file.

**REQ-CLI-161**: Paths containing spaces shall be properly handled (quoted or escaped).

**REQ-CLI-162**: Tilde (`~`) expansion shall be supported for home directory paths.

**REQ-CLI-163**: Symbolic links shall be followed for all file paths.

## 18. Color Support

**REQ-CLI-170**: The CLI help message shall use ANSI color codes when output is a terminal.

**REQ-CLI-171**: Colors shall be automatically disabled when output is piped or redirected.

**REQ-CLI-172**: The CLI shall detect TTY using `sys.stdout.isatty()`.

**REQ-CLI-173**: Color codes shall be used for:
- Section headers: Yellow + Bold
- Commands/examples: Green
- Keywords: Cyan
- Important text: Bold

## 19. Examples

### Basic Usage
```bash
# Generate files from configuration
template-forge config.yaml

# Generate with verbose output
template-forge config.yaml -v
template-forge config.yaml --verbose

# Validate configuration only
template-forge config.yaml --validate

# Display help
template-forge --help
template-forge -h

# Display version
template-forge --version
```

### Exit Code Examples
```bash
# Success
$ template-forge config.yaml
$ echo $?
0

# Configuration not found
$ template-forge missing.yaml
ERROR - Configuration file not found: missing.yaml
$ echo $?
1

# User cancellation
$ template-forge config.yaml
^C
INFO - Operation cancelled by user
$ echo $?
130
```

### Path Examples
```bash
# Relative path
template-forge config.yaml
template-forge ./examples/basic/config.yaml
template-forge ../other-project/config.yaml

# Absolute path
template-forge /home/user/project/config.yaml
template-forge /opt/templates/config.yaml

# Home directory
template-forge ~/projects/myapp/config.yaml

# Spaces in path (quoted)
template-forge "my config.yaml"
template-forge 'path with spaces/config.yaml'
```

### Verbose Output Example
```bash
$ template-forge config.yaml -v
2025-10-03 10:30:15,123 - root - INFO - Validating configuration: config.yaml
2025-10-03 10:30:15,125 - root - INFO - Configuration valid. Starting generation...
2025-10-03 10:30:15,127 - template_forge.core - INFO - Starting template generation with config: config.yaml
2025-10-03 10:30:15,128 - template_forge.core - DEBUG - Loading configuration from config.yaml
2025-10-03 10:30:15,130 - template_forge.core - INFO - Processing JSON file: data.json
2025-10-03 10:30:15,131 - template_forge.core - DEBUG - Extracted token: app_name = MyApp
2025-10-03 10:30:15,132 - template_forge.core - DEBUG - Extracted token: version = 1.0.0
2025-10-03 10:30:15,133 - template_forge.core - INFO - Processing template: app.py.j2
2025-10-03 10:30:15,135 - template_forge.core - INFO - Generated output: src/app.py
2025-10-03 10:30:15,136 - template_forge.core - INFO - Template generation completed
```

### Validation Example
```bash
$ template-forge config.yaml --validate
2025-10-03 10:30:20,456 - root - INFO - Validating configuration: config.yaml
2025-10-03 10:30:20,458 - root - INFO - Configuration is valid
$ echo $?
0

$ template-forge bad_config.yaml --validate
2025-10-03 10:30:25,789 - root - INFO - Validating configuration: bad_config.yaml
2025-10-03 10:30:25,790 - root - ERROR - Configuration validation failed: Input file not found: missing.json
2025-10-03 10:30:25,791 - root - ERROR - Configuration validation failed. Aborting.
$ echo $?
1
```

## 20. Integration with Package Manager

**REQ-CLI-180**: The CLI entry point shall be registered in `pyproject.toml` under `[project.scripts]`.

**REQ-CLI-181**: The CLI shall be installed as `template-forge` command when the package is installed.

**REQ-CLI-182**: The CLI shall be available immediately after installation via pip.

**REQ-CLI-183**: The CLI shall work from any directory after installation.

## 21. Backwards Compatibility

**REQ-CLI-190**: Future versions shall maintain backwards compatibility with existing command-line syntax.

**REQ-CLI-191**: New options shall be added as optional flags to preserve existing behavior.

**REQ-CLI-192**: Deprecated options shall display warnings before being removed in major versions.

**REQ-CLI-193**: Configuration file format changes shall be backwards compatible or provide migration tools.
