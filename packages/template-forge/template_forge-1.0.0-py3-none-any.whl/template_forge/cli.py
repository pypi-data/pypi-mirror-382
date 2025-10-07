#!/usr/bin/env python3
"""Command-line interface for Template Forge."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .core import TemplateForge


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"  # Magenta
    BLUE = "\033[94m"  # Blue
    CYAN = "\033[96m"  # Cyan
    GREEN = "\033[92m"  # Green
    YELLOW = "\033[93m"  # Yellow
    RED = "\033[91m"  # Red
    BOLD = "\033[1m"  # Bold
    UNDERLINE = "\033[4m"  # Underline
    END = "\033[0m"  # Reset

    _color_enabled = True  # Can be disabled with --no-color

    @staticmethod
    def is_tty() -> bool:
        """Check if stdout is a TTY (terminal)."""
        return sys.stdout.isatty()

    @classmethod
    def disable_colors(cls) -> None:
        """Disable all color output."""
        cls._color_enabled = False

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text if output is a TTY and colors are enabled."""
        if cls._color_enabled and cls.is_tty():
            return f"{color}{text}{cls.END}"
        return text


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    # Define color helpers
    c = Colors.colorize
    bold = Colors.BOLD
    green = Colors.GREEN
    yellow = Colors.YELLOW
    magenta = Colors.HEADER

    parser = argparse.ArgumentParser(
        prog="template-forge",
        description=f"""
{c("TEMPLATE FORGE", bold + magenta)}

Transform structured data into code, configuration, and documentation
with powerful template-driven generation using Jinja2.

Template Forge extracts data from structured files (JSON, YAML, XML, ARXML)
and uses Jinja2 templates to generate any text-based output.

{c("KEY FEATURES:", bold + yellow)}
  {c("•", green)} Extract tokens from JSON, YAML, XML, and ARXML files
  {c("•", green)} Navigate nested data structures with dot notation
  {c("•", green)} Full Jinja2 templating power (loops, conditionals, filters)
  {c("•", green)} Preserve custom code sections during regeneration
  {c("•", green)} Transform and filter data during extraction
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{c("USAGE:", bold + yellow)}
  {c("template-forge config.yaml", green)}              # Generate from config
  {c("template-forge config.yaml -v", green)}           # Verbose output
  {c("template-forge config.yaml --validate", green)}   # Validate only

{c("SUPPORTED FORMATS:", bold + yellow)}
  {c("JSON", bold)} (.json)  {c("YAML", bold)} (.yaml, .yml)  {c("XML", bold)} (.xml)  {c("ARXML", bold)} (.arxml)

{c("LEARN MORE:", bold + yellow)}
  {c("Examples:", bold)}      https://github.com/CarloFornari/template_forge/tree/main/examples
  {c("Documentation:", bold)} https://github.com/CarloFornari/template_forge#readme
  {c("Report Issues:", bold)} https://github.com/CarloFornari/template_forge/issues
""",
    )

    parser.add_argument(
        "config",
        type=Path,
        nargs="?",  # Make config file optional
        help="YAML configuration file path (optional, auto-discovers if not specified)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration only (do not generate files)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without writing files (REQ-CLI-030-036)",
    )

    parser.add_argument(
        "--show-variables",
        nargs="?",
        const="__all__",
        metavar="TEMPLATE",
        help="Display all resolved variables or for specific template (REQ-CLI-040-047)",
    )

    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show differences before applying changes (REQ-CLI-050-058)",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    parser.add_argument(
        "--init",
        nargs="?",
        const="basic",
        metavar="TEMPLATE",
        help="Create a new project configuration (templates: basic, python, cpp, web) (REQ-CLI-140-141)",
    )

    parser.add_argument(
        "--no-hooks",
        action="store_true",
        help="Skip execution of post-generation hooks (REQ-AUT-090)",
    )

    parser.add_argument(
        "--version", action="version", version=f"Template Forge {__version__}"
    )

    return parser


def discover_config() -> Optional[Path]:
    """Discover configuration file automatically (REQ-CFG-080-085).

    Searches in the following order:
    1. config.yaml
    2. config.yml
    3. .template-forge.yaml
    4. .template-forge.yml
    5. template-forge.yaml
    6. template-forge.yml

    Returns:
        Path to found configuration file, or None if not found.
    """
    search_order = [
        "config.yaml",
        "config.yml",
        ".template-forge.yaml",
        ".template-forge.yml",
        "template-forge.yaml",
        "template-forge.yml",
    ]

    for filename in search_order:
        config_path = Path(filename)
        if config_path.exists():
            logging.info(f"Discovered configuration file: {config_path}")
            return config_path

    return None


def validate_config(config_file: Path) -> bool:
    """Validate configuration file without generating output."""
    try:
        TemplateForge(config_file)
        return True
    except Exception as e:
        logging.error(f"Configuration validation failed: {e}")
        return False


def show_variables(config_file: Path, template_filter: Optional[str] = None) -> None:
    """Display all resolved variables (REQ-CLI-040-047)."""
    import yaml

    from .core import StructuredDataExtractor

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Extract tokens
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        print(
            Colors.colorize("\n=== Resolved Variables ===\n", Colors.BOLD + Colors.CYAN)
        )

        # Show static tokens
        if config.get("static_tokens"):
            print(Colors.colorize("Static Tokens:", Colors.BOLD + Colors.YELLOW))
            for key, value in config["static_tokens"].items():
                value_str = (
                    repr(value) if isinstance(value, (list, dict)) else str(value)
                )
                print(f"  {Colors.colorize(key, Colors.GREEN)}: {value_str}")
            print()

        # Show namespace-organized tokens
        if "inputs" in config:
            for input_config in config["inputs"]:
                namespace = input_config.get("namespace", "unknown")
                file_path = input_config.get("path", "unknown")

                if namespace in tokens:
                    print(
                        Colors.colorize(
                            f"Namespace '{namespace}' (from {file_path}):",
                            Colors.BOLD + Colors.YELLOW,
                        )
                    )
                    namespace_tokens = tokens[namespace]
                    if isinstance(namespace_tokens, dict):
                        for key, value in namespace_tokens.items():
                            value_str = (
                                repr(value)
                                if isinstance(value, (list, dict))
                                else str(value)
                            )
                            if len(value_str) > 100:
                                value_str = value_str[:97] + "..."
                            print(
                                f"  {Colors.colorize(namespace + '.' + key, Colors.GREEN)}: {value_str}"
                            )
                    print()

        # Show template-specific variables if filter provided
        if template_filter and template_filter != "__all__":
            print(
                Colors.colorize(
                    f"\nTemplate-specific variables for: {template_filter}",
                    Colors.BOLD + Colors.CYAN,
                )
            )
            print("(Not yet implemented - shows all variables above)")

        print(
            Colors.colorize(
                f"Total namespaces: {len([k for k in tokens.keys() if k not in (config.get('static_tokens', {}).keys())])}",
                Colors.BOLD,
            )
        )

    except Exception as e:
        logging.error(f"Error displaying variables: {e}")
        sys.exit(1)


def init_project(template_type: str = "basic") -> None:
    """Create a new project configuration (REQ-CLI-140-141).

    Args:
        template_type: Type of project template (basic, python, cpp, web)
    """
    config_file = Path("config.yaml")

    # Check if config already exists
    if config_file.exists():
        print(Colors.colorize("Error: config.yaml already exists!", Colors.RED))
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            print("Init cancelled.")
            return

    # Template configurations
    templates = {
        "basic": {
            "static_tokens": {
                "project_name": "MyProject",
                "version": "1.0.0",
                "author": "Your Name",
            },
            "templates": [{"template": "README.md.j2", "output": "README.md"}],
        },
        "python": {
            "static_tokens": {
                "project_name": "my_python_project",
                "version": "0.1.0",
                "author": "Your Name",
                "python_version": "3.8",
            },
            "templates": [
                {"template": "setup.py.j2", "output": "setup.py"},
                {"template": "README.md.j2", "output": "README.md"},
            ],
        },
        "cpp": {
            "static_tokens": {
                "project_name": "MyCppProject",
                "version": "1.0.0",
                "author": "Your Name",
                "cpp_standard": "17",
            },
            "templates": [
                {"template": "CMakeLists.txt.j2", "output": "CMakeLists.txt"},
                {"template": "main.cpp.j2", "output": "src/main.cpp"},
            ],
        },
        "web": {
            "static_tokens": {
                "project_name": "MyWebApp",
                "version": "1.0.0",
                "author": "Your Name",
            },
            "templates": [
                {"template": "index.html.j2", "output": "public/index.html"},
                {"template": "package.json.j2", "output": "package.json"},
            ],
        },
    }

    if template_type not in templates:
        print(Colors.colorize(f"Unknown template type: {template_type}", Colors.RED))
        print(f"Available templates: {', '.join(templates.keys())}")
        sys.exit(1)

    config = templates[template_type]

    # Write configuration file
    try:
        import yaml

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        # Use ASCII-safe character for cross-platform compatibility
        print(Colors.colorize(f"[OK] Created {config_file}", Colors.GREEN))
        print(f"\nProject type: {Colors.colorize(template_type, Colors.CYAN)}")
        print("\nNext steps:")
        print("1. Create a 'templates/' directory")
        print("2. Add your Jinja2 template files (.j2)")
        print("3. Run: template-forge")
        print(f"\nEdit {config_file} to customize your configuration.")

    except Exception as e:
        print(Colors.colorize(f"Error creating configuration: {e}", Colors.RED))
        sys.exit(1)


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Handle --no-color flag (REQ-CLI-056)
    if parsed_args.no_color:
        Colors.disable_colors()

    # Setup logging
    setup_logging(parsed_args.verbose)

    # Handle --init mode (REQ-CLI-140-141)
    if parsed_args.init is not None:
        init_project(parsed_args.init)
        sys.exit(0)

    # Determine configuration file (explicit or auto-discovered)
    config_file = parsed_args.config

    if config_file is None:
        # Auto-discover configuration (REQ-CLI-012, REQ-CFG-080)
        config_file = discover_config()
        if config_file is None:
            logging.error(
                "No configuration file specified and auto-discovery failed.\n"
                "Searched for: config.yaml, config.yml, .template-forge.yaml, "
                ".template-forge.yml, template-forge.yaml, template-forge.yml\n"
                "Please create a configuration file or specify one explicitly."
            )
            sys.exit(1)
    else:
        # Validate explicitly specified configuration file exists
        if not config_file.exists():
            logging.error(f"Configuration file not found: {config_file}")
            sys.exit(1)

    try:
        # Handle --show-variables mode (REQ-CLI-040-047)
        if parsed_args.show_variables is not None:
            show_variables(config_file, parsed_args.show_variables)
            sys.exit(0)

        # Always validate configuration first
        logging.info(f"Validating configuration: {config_file}")
        if not validate_config(config_file):
            logging.error("Configuration validation failed. Aborting.")
            sys.exit(1)

        if parsed_args.validate:
            # Validation-only mode - already validated above
            logging.info("Configuration is valid")
            sys.exit(0)

        # Handle --dry-run mode (REQ-CLI-030-036)
        if parsed_args.dry_run:
            logging.info(
                "Configuration valid. Running in DRY-RUN mode (no files will be written)..."
            )
            forge = TemplateForge(config_file)
            forge.run(
                dry_run=True, show_diff=parsed_args.diff, no_hooks=parsed_args.no_hooks
            )
            sys.exit(0)

        # Handle --diff mode (REQ-CLI-050-058)
        if parsed_args.diff:
            logging.info("Configuration valid. Generating with diff preview...")
            forge = TemplateForge(config_file)
            forge.run(dry_run=False, show_diff=True, no_hooks=parsed_args.no_hooks)
        else:
            # Normal operation mode - proceed with generation
            logging.info("Configuration valid. Starting generation...")
            forge = TemplateForge(config_file)
            forge.run(no_hooks=parsed_args.no_hooks)

    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if parsed_args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
