"""Type definitions and configuration models for Template Forge."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class TokenConfig:
    """Configuration for extracting a single token.

    Attributes:
        name: The name of the token to extract.
        key: Dot-notation key path for extraction (e.g., 'app.version').
        default: Default value if extraction fails.
        regex: Optional regex pattern to apply to extracted value.
        transform: Optional transformation to apply (e.g., 'upper', 'lower').
    """

    name: str
    key: str
    default: Optional[Any] = None
    regex: Optional[str] = None
    transform: Optional[str] = None


@dataclass
class InputFileConfig:
    """Configuration for processing a single input file.

    Attributes:
        path: Path to the input file.
        tokens: List of token configurations to extract from this file.
        encoding: File encoding (defaults to 'utf-8').
    """

    path: Union[str, Path]
    tokens: List[TokenConfig] = field(default_factory=list)
    encoding: str = "utf-8"

    def __post_init__(self) -> None:
        """Convert path to Path object and tokens to TokenConfig objects."""
        self.path = Path(self.path)
        self.tokens = [
            TokenConfig(**token) if isinstance(token, dict) else token
            for token in self.tokens
        ]


@dataclass
class TemplateConfig:
    """Configuration for processing a single template.

    Attributes:
        template: Path to the Jinja2 template file.
        output: Path where the rendered output should be written.
        tokens: Additional template-specific tokens.
        encoding: Output file encoding (defaults to 'utf-8').
    """

    template: Union[str, Path]
    output: Union[str, Path]
    tokens: Dict[str, Any] = field(default_factory=dict)
    encoding: str = "utf-8"

    def __post_init__(self) -> None:
        """Convert paths to Path objects."""
        self.template = Path(self.template)
        self.output = Path(self.output)


@dataclass
class ForgeConfig:
    """Main configuration for Template Forge.

    Attributes:
        inputs: List of input file configurations.
        templates: List of template configurations.
        template_dir: Directory containing template files.
        static_tokens: Static tokens to include in all templates.
        jinja_options: Options for Jinja2 environment.
    """

    inputs: List[InputFileConfig] = field(default_factory=list)
    templates: List[TemplateConfig] = field(default_factory=list)
    template_dir: Union[str, Path] = Path()
    static_tokens: Dict[str, Any] = field(default_factory=dict)
    jinja_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Convert configurations to appropriate types."""
        self.template_dir = Path(self.template_dir)
        self.inputs = [
            InputFileConfig(**input_cfg) if isinstance(input_cfg, dict) else input_cfg
            for input_cfg in self.inputs
        ]
        self.templates = [
            TemplateConfig(**tmpl_cfg) if isinstance(tmpl_cfg, dict) else tmpl_cfg
            for tmpl_cfg in self.templates
        ]

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ForgeConfig":
        """Create ForgeConfig from dictionary.

        Args:
            config_dict: Configuration dictionary, typically loaded from YAML.

        Returns:
            ForgeConfig instance.
        """
        return cls(**config_dict)


class TemplateForgeError(Exception):
    """Base exception for Template Forge errors."""

    pass


class ConfigurationError(TemplateForgeError):
    """Raised when configuration is invalid."""

    pass


class ExtractionError(TemplateForgeError):
    """Raised when token extraction fails."""

    pass


class TemplateProcessingError(TemplateForgeError):
    """Raised when template processing fails."""

    pass
