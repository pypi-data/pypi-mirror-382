#!/usr/bin/env python3
"""Post-generation hook execution module for Template Forge.

This module handles executing post-generation commands with error handling,
timeouts, conditional execution, and environment variable support.
"""

import logging
import os
import subprocess  # nosec B404 - needed for hook execution
from pathlib import Path
from typing import Any, Dict

from jinja2 import DictLoader, Environment


class HookExecutor:
    """Execute post-generation hooks with error handling and timeout support.

    Implements requirements REQ-AUT-001 through REQ-AUT-093 for post-generation
    automation hooks including command execution, error handling, timeouts,
    and conditional execution.
    """

    def __init__(
        self, config: Dict[str, Any], tokens: Dict[str, Any], config_file: Path
    ):
        """Initialize hook executor.

        Args:
            config: Configuration dictionary
            tokens: Resolved tokens for conditional evaluation
            config_file: Path to config file (for relative path resolution)
        """
        self.config = config
        self.tokens = tokens
        self.config_dir = config_file.parent
        self.logger = logging.getLogger(__name__)
        self._hooks_warning_shown = False

    def execute_post_generate_hooks(self, dry_run: bool = False) -> bool:
        """Execute post-generation hooks.

        Args:
            dry_run: If True, display hooks without executing

        Returns:
            True if all hooks succeeded or were skipped, False if any failed

        Implements:
            - REQ-AUT-010: Execute after all templates generated
            - REQ-AUT-011: Not executed if template generation fails
            - REQ-AUT-073: Display hooks in dry-run without executing
        """
        hooks_config = self.config.get("hooks", {})
        post_gen_hooks = hooks_config.get("post_generate", [])

        if not post_gen_hooks:
            return True

        # REQ-AUT-071: Show security warning on first hook execution
        if not self._hooks_warning_shown and not dry_run:
            self.logger.info(
                "Executing post-generation hooks. Review commands in config for security."
            )
            self._hooks_warning_shown = True

        # REQ-AUT-073: Dry-run mode displays hooks
        if dry_run:
            self.logger.info(
                f"[DRY RUN] Would execute {len(post_gen_hooks)} post-generation hooks:"
            )
            for idx, hook in enumerate(post_gen_hooks, 1):
                cmd = hook.get("command", "")
                desc = hook.get("description", "No description")
                working_dir = hook.get("working_dir", ".")
                self.logger.info(f"  {idx}. {desc}: {cmd}")
                if working_dir != ".":
                    self.logger.info(f"     (in {working_dir}/)")
            return True

        self.logger.info(
            f"Running post-generation hooks ({len(post_gen_hooks)} hooks)..."
        )

        all_success = True
        for idx, hook in enumerate(post_gen_hooks, 1):
            # REQ-AUT-003: Extract hook configuration
            command = hook.get("command")
            if not command:
                self.logger.warning(
                    f"[{idx}/{len(post_gen_hooks)}] Hook missing 'command', skipping"
                )
                continue

            description = hook.get("description", command)
            working_dir = hook.get("working_dir", ".")
            on_error = hook.get("on_error", "warn")
            timeout = hook.get("timeout", 300)
            when_condition = hook.get("when")

            # REQ-AUT-030-033: Conditional execution
            if when_condition:
                try:
                    # Use Jinja2 to evaluate condition with tokens
                    env = Environment(loader=DictLoader({}))  # nosec B701 - autoescape intentionally False for condition evaluation
                    template = env.from_string(
                        f"{{% if {when_condition} %}}true{{% endif %}}"
                    )
                    condition_result = template.render(**self.tokens)
                    if condition_result != "true":
                        self.logger.debug(
                            f"[{idx}/{len(post_gen_hooks)}] Skipping '{description}' "
                            f"(condition '{when_condition}' not met)"
                        )
                        continue
                except Exception as e:
                    self.logger.warning(
                        f"[{idx}/{len(post_gen_hooks)}] Failed to evaluate condition "
                        f"'{when_condition}': {e}, skipping hook"
                    )
                    continue

            # REQ-AUT-005: Log hook execution
            self.logger.info(f"[{idx}/{len(post_gen_hooks)}] {description}")
            self.logger.info(f"  → {command}")

            # REQ-AUT-050-052: Resolve working directory
            if working_dir != ".":
                work_path = Path(working_dir)
                if not work_path.is_absolute():
                    work_path = self.config_dir / work_path

                # REQ-AUT-051: Working dir must exist
                if not work_path.exists():
                    msg = f"Working directory does not exist: {work_path}"
                    self.logger.error(f"  ✗ {msg}")
                    if on_error == "fail":
                        return False
                    elif on_error == "warn":
                        all_success = False
                    continue

                cwd = str(work_path)
            else:
                cwd = None

            # REQ-AUT-006: Set environment variables
            process_env: Dict[str, str] = os.environ.copy()
            process_env["TEMPLATE_FORGE_CONFIG"] = str(
                self.config_dir / self.config.get("config_file", "config.yaml")
            )
            process_env["TEMPLATE_FORGE_OUTPUT_DIR"] = str(self.config_dir)

            # REQ-AUT-012-016: Execute command in shell
            try:
                result = subprocess.run(
                    command,
                    shell=True,  # nosec B602 - shell=True needed for hook commands with pipes/redirects
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    env=process_env,
                )

                # REQ-AUT-015: Log output at appropriate levels
                if result.stdout:
                    for line in result.stdout.strip().split("\n"):
                        self.logger.info(f"    {line}")

                if result.stderr:
                    for line in result.stderr.strip().split("\n"):
                        self.logger.warning(f"    {line}")

                # REQ-AUT-020-021: Handle errors based on on_error setting
                if result.returncode != 0:
                    msg = f"Failed with exit code {result.returncode}"
                    self.logger.warning(f"  ✗ {msg}")

                    if on_error == "fail":
                        return False
                    elif on_error == "warn":
                        all_success = False
                    # on_error == 'ignore': continue silently
                else:
                    self.logger.info("  ✓ Completed successfully")

            except subprocess.TimeoutExpired:
                # REQ-AUT-022: Timeout error message
                msg = f"Hook '{description}' timed out after {timeout} seconds"
                self.logger.warning(f"  ✗ {msg}")

                if on_error == "fail":
                    return False
                elif on_error == "warn":
                    all_success = False

            except FileNotFoundError:
                # REQ-AUT-023: Command not found suggestion
                msg = "Hook command failed: command not found\nSuggestion: Ensure the command is installed and in your PATH"
                self.logger.error(f"  ✗ {msg}")

                if on_error == "fail":
                    return False
                elif on_error == "warn":
                    all_success = False

            except Exception as e:
                msg = f"Hook execution error: {e}"
                self.logger.error(f"  ✗ {msg}")

                if on_error == "fail":
                    return False
                elif on_error == "warn":
                    all_success = False

        return all_success
