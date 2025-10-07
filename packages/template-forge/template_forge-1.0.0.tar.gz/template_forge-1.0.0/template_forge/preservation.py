#!/usr/bin/env python3
"""Content preservation functionality for Template Forge.

This module handles preservation of content between @PRESERVE_START and @PRESERVE_END
markers, allowing custom code to survive template regeneration.
"""

import logging
from pathlib import Path
from typing import Dict, List


class PreservationHandler:
    """Handle preservation of content between @PRESERVE_START and @PRESERVE_END markers.

    This class provides functionality to extract preserved content from existing files
    and inject it back into newly generated content during template processing.

    Attributes:
        PRESERVE_START: Start marker for preserved content.
        PRESERVE_END: End marker for preserved content.
        logger: Logger instance for this handler.

    Example:
        >>> handler = PreservationHandler()
        >>> preserved = handler.extract_preserved_content(Path("existing_file.txt"))
        >>> new_content = handler.inject_preserved_content("template_output", preserved)
    """

    PRESERVE_START = "@PRESERVE_START"
    PRESERVE_END = "@PRESERVE_END"

    def __init__(self) -> None:
        """Initialize the preservation handler."""
        self.logger = logging.getLogger(__name__)

    def extract_preserved_content(self, file_path: Path) -> Dict[str, str]:
        """Extract preserved content blocks from an existing file.

        Blocks are matched by their identifier (REQ-PRV-050-053), not by position.

        Args:
            file_path: Path to the existing file to extract preserved content from.

        Returns:
            Dictionary mapping block identifier to preserved content string.
            Key is the identifier from @PRESERVE_START identifier marker.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If preserve markers are mismatched or malformed.
        """
        if not file_path.exists():
            self.logger.warning(
                f"Could not read file {file_path} for preservation: File does not exist"
            )
            return {}

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.logger.warning(
                f"Could not read file {file_path} for preservation: {e}"
            )
            return {}

        try:
            return self._parse_preserved_blocks(content)
        except ValueError as e:
            # REQ-PRV-071, REQ-PRV-072: Malformed markers logged, processing continues
            self.logger.error(f"Malformed preservation markers in {file_path}: {e}")
            return {}

    def _parse_preserved_blocks(self, content: str) -> Dict[str, str]:
        """Parse preserved content blocks from text content.

        Uses identifier-based matching (REQ-PRV-050-053, REQ-PRV-014).

        Args:
            content: Text content to parse for preserve markers.

        Returns:
            Dictionary mapping block identifier to preserved content.

        Raises:
            ValueError: If preserve markers are mismatched or have duplicate identifiers.
        """
        preserved_blocks: Dict[str, str] = {}
        lines = content.splitlines(keepends=True)

        in_preserve_block = False
        preserve_start_line = -1
        current_identifier: str = ""
        current_preserved_content: List[str] = []

        for line_num, line in enumerate(lines):
            line_stripped = line.strip()

            if self.PRESERVE_START in line_stripped:
                if in_preserve_block:
                    raise ValueError(
                        f"Found nested {self.PRESERVE_START} at line {line_num + 1}. "
                        f"Previous block started at line {preserve_start_line + 1}."
                    )

                # Extract identifier from marker (REQ-PRV-014, REQ-PRV-020)
                # Format: @PRESERVE_START identifier
                marker_pos = line_stripped.find(self.PRESERVE_START)
                after_marker = line_stripped[
                    marker_pos + len(self.PRESERVE_START) :
                ].strip()

                if not after_marker:
                    raise ValueError(
                        f"Missing identifier in {self.PRESERVE_START} at line {line_num + 1}. "
                        f"Format: @PRESERVE_START identifier"
                    )

                # The identifier is the first word after the marker
                current_identifier = after_marker.split()[0]

                # Check for duplicate identifiers (REQ-PRV-033)
                if current_identifier in preserved_blocks:
                    raise ValueError(
                        f"Duplicate preserved block identifier '{current_identifier}' "
                        f"at line {line_num + 1}. Each block must have a unique identifier."
                    )

                in_preserve_block = True
                preserve_start_line = line_num
                current_preserved_content = []
                self.logger.debug(
                    f"Found preserve start '{current_identifier}' at line {line_num + 1}"
                )

            elif self.PRESERVE_END in line_stripped:
                if not in_preserve_block:
                    raise ValueError(
                        f"Found {self.PRESERVE_END} at line {line_num + 1} "
                        f"without matching {self.PRESERVE_START}"
                    )

                # Verify identifier matches (REQ-PRV-021)
                marker_pos = line_stripped.find(self.PRESERVE_END)
                after_marker = line_stripped[
                    marker_pos + len(self.PRESERVE_END) :
                ].strip()

                if after_marker:
                    # The identifier is the first word after the marker
                    end_identifier = after_marker.split()[0]
                    if end_identifier != current_identifier:
                        raise ValueError(
                            f"Mismatched identifiers at line {line_num + 1}: "
                            f"started with '{current_identifier}' but ended with '{end_identifier}'"
                        )

                # Store the preserved content (excluding the marker lines)
                preserved_content = "".join(current_preserved_content)
                preserved_blocks[current_identifier] = preserved_content

                self.logger.debug(
                    f"Found preserve end '{current_identifier}' at line {line_num + 1}, "
                    f"preserved {len(current_preserved_content)} lines"
                )

                in_preserve_block = False
                preserve_start_line = -1
                current_identifier = ""
                current_preserved_content = []

            elif in_preserve_block:
                # Collect content inside preserve block
                current_preserved_content.append(line)

        if in_preserve_block:
            raise ValueError(
                f"Unclosed {self.PRESERVE_START} block '{current_identifier}' starting at line "
                f"{preserve_start_line + 1}"
            )

        self.logger.info(f"Extracted {len(preserved_blocks)} preserved content blocks")
        return preserved_blocks

    def inject_preserved_content(
        self, template_output: str, preserved_blocks: Dict[str, str]
    ) -> str:
        """Inject preserved content back into template output.

        Uses identifier-based matching (REQ-PRV-050-053).

        Args:
            template_output: The newly generated template output.
            preserved_blocks: Dictionary of preserved content blocks to inject (identifier -> content).

        Returns:
            Template output with preserved content injected between markers.

        Raises:
            ValueError: If template structure doesn't match preserved blocks.
        """
        if not preserved_blocks:
            return template_output

        lines = template_output.splitlines(keepends=True)
        result_lines = []

        in_preserve_block = False
        current_identifier = None
        identifiers_found = set()

        for line_num, line in enumerate(lines):
            line_stripped = line.strip()

            if self.PRESERVE_START in line_stripped:
                if in_preserve_block:
                    raise ValueError(
                        f"Found nested {self.PRESERVE_START} at line {line_num + 1} in template output"
                    )

                # Extract identifier
                marker_pos = line_stripped.find(self.PRESERVE_START)
                after_marker = line_stripped[
                    marker_pos + len(self.PRESERVE_START) :
                ].strip()

                if not after_marker:
                    raise ValueError(
                        f"Missing identifier in {self.PRESERVE_START} at line {line_num + 1}"
                    )

                # The identifier is the first word after the marker
                current_identifier = after_marker.split()[0]
                identifiers_found.add(current_identifier)

                in_preserve_block = True
                result_lines.append(line)  # Keep the start marker

                # Inject preserved content if available (REQ-PRV-041, REQ-PRV-051)
                if current_identifier in preserved_blocks:
                    preserved_content = preserved_blocks[current_identifier]
                    result_lines.append(preserved_content)
                    self.logger.debug(
                        f"Injected preserved content for block '{current_identifier}'"
                    )
                else:
                    # No preserved content - keep template default (REQ-PRV-043)
                    self.logger.debug(
                        f"No preserved content found for block '{current_identifier}', using template default"
                    )

            elif self.PRESERVE_END in line_stripped:
                if not in_preserve_block:
                    raise ValueError(
                        f"Found {self.PRESERVE_END} at line {line_num + 1} without matching {self.PRESERVE_START} in template output"
                    )

                # Verify identifier matches
                marker_pos = line_stripped.find(self.PRESERVE_END)
                after_marker = line_stripped[
                    marker_pos + len(self.PRESERVE_END) :
                ].strip()

                if after_marker:
                    # The identifier is the first word after the marker
                    end_identifier = after_marker.split()[0]
                    if end_identifier != current_identifier:
                        raise ValueError(
                            f"Mismatched identifiers at line {line_num + 1}: "
                            f"started with '{current_identifier}' but ended with '{end_identifier}'"
                        )

                result_lines.append(line)  # Keep the end marker
                in_preserve_block = False
                current_identifier = None

            elif not in_preserve_block:
                # Outside preserve block, keep the line
                result_lines.append(line)

            # Inside preserve block: skip template content, we already added preserved content

        if in_preserve_block:
            raise ValueError(
                f"Unclosed preserve block '{current_identifier}' in template output"
            )

        # Check for preserved blocks that no longer exist in template (REQ-PRV-042, REQ-PRV-053)
        lost_blocks = set(preserved_blocks.keys()) - identifiers_found
        if lost_blocks:
            self.logger.warning(
                f"The following preserved blocks exist in the old file but not in the new template: "
                f"{', '.join(sorted(lost_blocks))}. These blocks will be lost."
            )

        return "".join(result_lines)
