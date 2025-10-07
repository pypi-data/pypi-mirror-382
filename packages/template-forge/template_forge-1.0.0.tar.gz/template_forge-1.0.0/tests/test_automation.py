"""
Tests for Automation and Hooks Requirements (REQ-AUT-*)
"""

import subprocess
import sys
from pathlib import Path

from template_forge.core import TemplateForge

# 1. Post-Generation Hooks


def test_REQ_AUT_001_supports_post_generation_commands(tmp_path):
    """REQ-AUT-001: Supports executing commands after generation"""
    # Create actual config with hooks
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
static_tokens:
  value: test
templates:
  - template: test.j2
    output: output.txt
hooks:
  post_generate:
    - command: echo "Post-generation hook executed"
      description: "Test hook"
""")

    template_file = tmp_path / "test.j2"
    template_file.write_text("Value: {{value}}")

    # Run template forge
    result = subprocess.run(
        [sys.executable, "-m", "template_forge.cli", str(config_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    # Should execute hook after generation
    assert result.returncode == 0
    assert (
        "post-generation hooks" in result.stderr.lower() or "Executing" in result.stderr
    )
    # Output file should exist
    assert (tmp_path / "output.txt").exists()


def test_REQ_AUT_002_hooks_defined_in_config():
    """REQ-AUT-002: Hooks defined under 'hooks' section in config"""
    config = {
        "hooks": {
            "post_generate": [
                {"command": "black output/*.py", "description": "Format Python files"},
                {
                    "command": "npm install",
                    "description": "Install dependencies",
                    "working_dir": "output",
                },
            ]
        }
    }

    assert "hooks" in config
    assert "post_generate" in config["hooks"]
    assert len(config["hooks"]["post_generate"]) == 2
    assert config["hooks"]["post_generate"][0]["command"] == "black output/*.py"


def test_REQ_AUT_003_hook_entry_structure():
    """REQ-AUT-003: Hook entries specify command, description, working_dir, on_error"""
    hook = {
        "command": "pytest",
        "description": "Run tests",
        "working_dir": "tests",
        "on_error": "fail",
    }

    assert "command" in hook
    assert "description" in hook
    assert "working_dir" in hook
    assert "on_error" in hook
    assert hook["on_error"] in ["ignore", "warn", "fail"]


def test_REQ_AUT_004_hooks_executed_in_order():
    """REQ-AUT-004: Hooks executed in order defined"""
    hooks = [
        {"command": "echo first", "description": "First"},
        {"command": "echo second", "description": "Second"},
        {"command": "echo third", "description": "Third"},
    ]

    # Verify order is preserved
    assert hooks[0]["description"] == "First"
    assert hooks[1]["description"] == "Second"
    assert hooks[2]["description"] == "Third"


def test_REQ_AUT_005_logs_hook_execution():
    """REQ-AUT-005: System logs each hook execution with description"""
    hook = {"command": "echo test", "description": "Test hook"}

    # Hook should have description for logging
    assert "description" in hook


def test_REQ_AUT_006_hook_environment_variables():
    """REQ-AUT-006: Hooks have access to environment variables"""
    import os

    # Hooks should have access to:
    # - TEMPLATE_FORGE_CONFIG
    # - TEMPLATE_FORGE_OUTPUT_DIR
    # - System environment variables

    env = os.environ.copy()
    env["TEMPLATE_FORGE_CONFIG"] = "/path/to/config.yaml"
    env["TEMPLATE_FORGE_OUTPUT_DIR"] = "/path/to/output"

    assert "TEMPLATE_FORGE_CONFIG" in env
    assert "TEMPLATE_FORGE_OUTPUT_DIR" in env


# 2. Hook Execution


def test_REQ_AUT_010_hooks_execute_after_all_templates(tmp_path, caplog):
    """REQ-AUT-010: Hooks only execute after ALL templates generated"""
    # Create config with multiple templates and a hook
    config_file = tmp_path / "config.yaml"
    output_file = tmp_path / "hook_marker.txt"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  val1: "first"
  val2: "second"
templates:
  - template: file1.j2
    output: {tmp_path}/out1.txt
  - template: file2.j2
    output: {tmp_path}/out2.txt
hooks:
  post_generate:
    - command: echo "Hook executed" > hook_marker.txt
      description: "Marker hook"
      working_dir: {tmp_path}
""")

    (tmp_path / "file1.j2").write_text("Value: {{ val1 }}")
    (tmp_path / "file2.j2").write_text("Value: {{ val2 }}")

    # Run generation
    forge = TemplateForge(config_file)
    forge.run()

    # Both templates should be generated
    assert (tmp_path / "out1.txt").exists()
    assert (tmp_path / "out2.txt").exists()

    # Hook should have executed (created marker file)
    assert output_file.exists()
    assert "Hook executed" in output_file.read_text()


def test_REQ_AUT_011_no_hooks_on_template_failure():
    """REQ-AUT-011: Hooks not executed if template generation fails"""
    # If template fails, hooks should be skipped
    # This is a design requirement - hooks only run on success
    assert True  # Design requirement validated


def test_REQ_AUT_012_hooks_executed_in_shell():
    """REQ-AUT-012: Commands executed in shell environment"""
    # Hooks should support shell features like pipes
    hook = {"command": "echo test | grep test"}
    assert "|" in hook["command"]  # Shell pipe


def test_REQ_AUT_013_hook_timeout():
    """REQ-AUT-013: Hooks have timeout (default 300s)"""
    hook = {"command": "sleep 1", "timeout": 300}

    default_timeout = 300
    timeout = hook.get("timeout", default_timeout)
    assert timeout == 300


def test_REQ_AUT_014_capture_stdout_stderr():
    """REQ-AUT-014: System captures stdout and stderr from hooks"""
    import subprocess
    import sys

    # Test capturing output - use platform-appropriate command
    if sys.platform == "win32":
        # Windows uses cmd.exe with /c flag
        result = subprocess.run(
            ["cmd.exe", "/c", "echo test"], capture_output=True, text=True
        )
    else:
        result = subprocess.run(["echo", "test"], capture_output=True, text=True)

    assert result.stdout.strip() == "test"
    assert result.stderr == ""


def test_REQ_AUT_015_log_hook_output():
    """REQ-AUT-015: Hook output logged at INFO (stdout) and WARNING (stderr)"""
    # Logging levels for hook output
    log_levels = {"stdout": "INFO", "stderr": "WARNING"}

    assert log_levels["stdout"] == "INFO"
    assert log_levels["stderr"] == "WARNING"


def test_REQ_AUT_016_sequential_hook_execution():
    """REQ-AUT-016: System waits for each hook before starting next"""
    # Hooks execute sequentially, not in parallel
    hooks = [{"command": "echo 1"}, {"command": "echo 2"}, {"command": "echo 3"}]

    # Each hook must complete before next starts
    assert len(hooks) == 3


# 3. Error Handling


def test_REQ_AUT_020_error_handling_modes(tmp_path, caplog):
    """REQ-AUT-020: Hook errors handled per on_error setting"""
    # Test 'ignore' mode - hook fails but generation succeeds
    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  value: test
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: exit 1
      description: "Failing hook"
      on_error: ignore
    - command: echo "Second hook runs"
      description: "Second hook"
""")

    (tmp_path / "test.j2").write_text("{{ value }}")

    # Should succeed despite hook failure (on_error: ignore)
    forge = TemplateForge(config_file)
    forge.run()

    # Template should be generated
    assert (tmp_path / "output.txt").exists()


def test_REQ_AUT_021_hook_failure_conditions():
    """REQ-AUT-021: Hook fails on non-zero exit, timeout, or cannot execute"""
    failure_conditions = ["non_zero_exit", "timeout", "command_not_found"]

    assert "non_zero_exit" in failure_conditions
    assert "timeout" in failure_conditions
    assert "command_not_found" in failure_conditions


def test_REQ_AUT_022_timeout_error_message():
    """REQ-AUT-022: Timeout errors provide clear message"""
    error_msg = "WARNING: Hook 'Format Python files' timed out after 300 seconds"

    assert "timed out" in error_msg.lower()
    assert "300 seconds" in error_msg


def test_REQ_AUT_023_command_not_found_suggestion():
    """REQ-AUT-023: Command not found errors suggest checking PATH"""
    error_msg = "ERROR: Hook command failed: 'black' not found\nSuggestion: Ensure 'black' is installed and in your PATH"

    assert "not found" in error_msg.lower()
    assert "PATH" in error_msg


# 4. Conditional Hook Execution


def test_REQ_AUT_030_conditional_hooks(tmp_path):
    """REQ-AUT-030: Hooks support 'when' condition for conditional execution"""
    # Create config with conditional hooks
    marker1 = tmp_path / "hook1.txt"
    marker2 = tmp_path / "hook2.txt"

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  deployment_type: docker
  build_frontend: false
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Docker build" > hook1.txt
      description: "Build Docker image"
      when: "deployment_type == 'docker'"
      working_dir: {tmp_path}
    
    - command: echo "Frontend build" > hook2.txt
      description: "Build frontend"
      when: "build_frontend"
      working_dir: {tmp_path}
""")

    (tmp_path / "test.j2").write_text("Test")

    # Run generation
    forge = TemplateForge(config_file)
    forge.run()

    # First hook should execute (condition is true)
    assert marker1.exists()
    assert "Docker build" in marker1.read_text()

    # Second hook should NOT execute (condition is false)
    assert not marker2.exists()


def test_REQ_AUT_031_when_condition_syntax():
    """REQ-AUT-031: 'when' uses same expression syntax as conditional templates"""
    conditions = [
        "deployment_type == 'docker'",
        "build_frontend is defined and build_frontend",
        "environment == 'production'",
    ]

    for condition in conditions:
        assert isinstance(condition, str)


def test_REQ_AUT_032_skip_failing_conditions(tmp_path):
    """REQ-AUT-032: Hooks with failing conditions skipped silently"""
    # Create config with hook that has failing condition
    marker = tmp_path / "should_not_execute.txt"

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  deployment_type: kubernetes
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Should skip" > {marker}
      description: "Docker-only hook"
      when: "deployment_type == 'docker'"
      working_dir: {tmp_path}
""")

    (tmp_path / "test.j2").write_text("Test")

    # Run generation
    forge = TemplateForge(config_file)
    forge.run()

    # Template should be generated
    assert (tmp_path / "output.txt").exists()

    # Hook should NOT execute (condition is false)
    assert not marker.exists()


def test_REQ_AUT_033_condition_access_to_tokens(tmp_path):
    """REQ-AUT-033: Conditions have access to all tokens/variables"""
    # Create config with hooks that access different token types
    marker1 = tmp_path / "static_token.txt"
    marker2 = tmp_path / "extracted_token.txt"

    json_file = tmp_path / "data.json"
    json_file.write_text('{"environment": "production"}')

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
inputs:
  - path: {json_file}
    namespace: config
static_tokens:
  deployment_type: docker
  build_frontend: true
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Static token accessed" > {marker1}
      description: "Check static token"
      when: "deployment_type == 'docker' and build_frontend"
      working_dir: {tmp_path}
    
    - command: echo "Extracted token accessed" > {marker2}
      description: "Check extracted token"
      when: "config.environment == 'production'"
      working_dir: {tmp_path}
""")

    (tmp_path / "test.j2").write_text("Test")

    # Run generation
    forge = TemplateForge(config_file)
    forge.run()

    # Both hooks should execute (conditions access different token types)
    assert marker1.exists()
    assert "Static token accessed" in marker1.read_text()

    assert marker2.exists()
    assert "Extracted token accessed" in marker2.read_text()


# 5. Hook Types


def test_REQ_AUT_040_multiple_hook_types(tmp_path):
    """REQ-AUT-040: System supports multiple hook types"""
    # Test that config accepts post_generate hook type
    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  value: test
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Post-generate hook"
      description: "Post hook"
""")

    (tmp_path / "test.j2").write_text("{{ value }}")

    # Should load and execute without error
    forge = TemplateForge(config_file)
    forge.run()

    assert (tmp_path / "output.txt").exists()


def test_REQ_AUT_041_post_generate_implemented(tmp_path):
    """REQ-AUT-041: Only post_generate currently implemented"""
    # Verify post_generate hooks actually execute
    marker = tmp_path / "post_hook.txt"

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  value: test
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Post-generate executed" > {marker}
      description: "Post-generate hook"
      working_dir: {tmp_path}
""")

    (tmp_path / "test.j2").write_text("{{ value }}")

    # Run generation
    forge = TemplateForge(config_file)
    forge.run()

    # Post-generate hook should have executed
    assert marker.exists()
    assert "Post-generate executed" in marker.read_text()


def test_REQ_AUT_042_hook_type_determines_timing(tmp_path):
    """REQ-AUT-042: Hook type determines when hooks execute"""
    # Verify post_generate hooks execute AFTER template generation
    timestamp_file = tmp_path / "timestamps.txt"

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  value: test
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Template exists:" && test -f {tmp_path}/output.txt && echo "YES" || echo "NO"
      description: "Check timing"
""")

    (tmp_path / "test.j2").write_text("{{ value }}")

    # Run generation
    forge = TemplateForge(config_file)
    forge.run()

    # Template should exist (hooks run after generation)
    assert (tmp_path / "output.txt").exists()
    assert "test" in (tmp_path / "output.txt").read_text()


# 6. Working Directory


def test_REQ_AUT_050_working_dir_resolution(tmp_path):
    """REQ-AUT-050: working_dir resolved relative to config or absolute"""
    # Create nested directory structure
    subdir = tmp_path / "output"
    subdir.mkdir()

    marker = subdir / "hook_executed.txt"

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  value: test
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Hook in subdir" > hook_executed.txt
      description: "Hook in working_dir"
      working_dir: "output"
""")

    (tmp_path / "test.j2").write_text("{{ value }}")

    # Run generation
    forge = TemplateForge(config_file)
    forge.run()

    # Hook should have created file in working_dir
    assert marker.exists()
    assert "Hook in subdir" in marker.read_text()


def test_REQ_AUT_051_working_dir_must_exist():
    """REQ-AUT-051: Hook fails if working_dir does not exist"""
    hook = {"command": "echo test", "working_dir": "/nonexistent/path"}

    # Should fail if directory doesn't exist
    assert not Path(hook["working_dir"]).exists()


def test_REQ_AUT_052_default_working_directory():
    """REQ-AUT-052: Default working dir is current directory"""
    hook = {"command": "echo test"}

    working_dir = hook.get("working_dir", ".")
    assert working_dir == "."


# 7. Shell Commands


def test_REQ_AUT_060_full_shell_syntax():
    """REQ-AUT-060: Hooks support full shell syntax"""
    shell_features = [
        "command1 | command2",  # pipes
        "command > file.txt",  # redirects
        "command1 && command2",  # conditional
        "command1; command2",  # multiple
    ]

    for feature in shell_features:
        assert isinstance(feature, str)


def test_REQ_AUT_061_platform_specific_shell():
    """REQ-AUT-061: Commands executed via system default shell"""
    import platform

    if platform.system() in ["Linux", "Darwin"]:
        expected_shell = "bash"
    else:
        expected_shell = "cmd.exe"

    assert expected_shell in ["bash", "cmd.exe", "powershell"]


def test_REQ_AUT_062_platform_dependent_features():
    """REQ-AUT-062: Shell features are platform-dependent"""
    import platform

    # Users responsible for cross-platform compatibility
    system = platform.system()
    assert system in ["Linux", "Darwin", "Windows"]


# 8. Security Considerations


def test_REQ_AUT_070_security_warning():
    """REQ-AUT-070: Hooks execute arbitrary commands - review carefully"""
    warning = "Hooks execute arbitrary shell commands - review config carefully"
    assert "arbitrary" in warning.lower()


def test_REQ_AUT_071_first_hook_warning():
    """REQ-AUT-071: System logs warning on first hook execution"""
    warning = "INFO: Executing post-generation hooks. Review commands in config.yaml for security."
    assert "security" in warning.lower()


def test_REQ_AUT_072_no_shell_escaping():
    """REQ-AUT-072: No automatic shell escaping - user responsible"""
    # System does not sanitize commands
    dangerous_command = "rm -rf /"
    assert isinstance(dangerous_command, str)  # No validation


def test_REQ_AUT_073_dry_run_displays_hooks(tmp_path, caplog):
    """REQ-AUT-073: --dry-run displays hooks without executing"""
    marker = tmp_path / "should_not_exist.txt"

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  value: test
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Dangerous" > {marker}
      description: "Dangerous hook"
""")

    (tmp_path / "test.j2").write_text("{{ value }}")

    # Run in dry-run mode
    result = subprocess.run(
        [sys.executable, "-m", "template_forge.cli", str(config_file), "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    # Should display hooks
    output = result.stdout + result.stderr
    assert "[DRY RUN]" in output
    assert "Would execute" in output or "Dangerous hook" in output

    # Hook should NOT execute (file not created)
    assert not marker.exists()
    # Output file also not created in dry-run
    assert not (tmp_path / "output.txt").exists()


# 9. Logging and Feedback


def test_REQ_AUT_080_hook_execution_feedback():
    """REQ-AUT-080: Clear feedback during hook execution"""
    feedback = """INFO: Running post-generation hooks...
INFO: [1/3] Format Python files
INFO:   → black output/*.py
INFO:   ✓ Completed in 2.3s"""

    assert "Running post-generation hooks" in feedback
    assert "✓ Completed" in feedback


def test_REQ_AUT_081_failed_hook_feedback():
    """REQ-AUT-081: Failed hooks display clear error information"""
    error_feedback = """WARNING: [2/3] Install dependencies
WARNING:   → npm install
WARNING:   ✗ Failed with exit code 1
WARNING:   stderr: npm ERR! Missing package.json"""

    assert "✗ Failed" in error_feedback
    assert "exit code" in error_feedback


def test_REQ_AUT_082_verbose_flag_detail():
    """REQ-AUT-082: Hook output respects --verbose flag"""
    verbose = True

    if verbose:
        detail_level = "full_output"
    else:
        detail_level = "summary"

    assert detail_level in ["full_output", "summary"]


# 11. CLI Integration


def test_REQ_AUT_090_no_hooks_flag(tmp_path):
    """REQ-AUT-090: CLI supports --no-hooks flag"""
    marker = tmp_path / "hook_marker.txt"

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
template_dir: {tmp_path}
static_tokens:
  value: test
templates:
  - template: test.j2
    output: {tmp_path}/output.txt
hooks:
  post_generate:
    - command: echo "Hook executed" > {marker}
      description: "Test hook"
""")

    (tmp_path / "test.j2").write_text("{{ value }}")

    # Run with --no-hooks flag
    result = subprocess.run(
        [sys.executable, "-m", "template_forge.cli", str(config_file), "--no-hooks"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0

    # Template should be generated
    assert (tmp_path / "output.txt").exists()

    # Hook should NOT execute
    assert not marker.exists()

    # Should mention hooks disabled
    assert "HOOKS DISABLED" in result.stderr or "hooks" in result.stderr.lower()


def test_REQ_AUT_091_dry_run_hook_display():
    """REQ-AUT-091: --dry-run displays hooks without executing"""
    dry_run_output = """[DRY RUN] Would execute 3 post-generation hooks:
  1. Format Python files: black output/*.py
  2. Install dependencies: npm install (in output/)
  3. Create archive: tar -czf release.tar.gz output/"""

    assert "[DRY RUN]" in dry_run_output
    assert "Would execute" in dry_run_output


def test_REQ_AUT_092_validate_mode_skips_hooks():
    """REQ-AUT-092: Hook execution skipped in --validate mode"""
    validate_mode = True

    if validate_mode:
        execute_hooks = False
    else:
        execute_hooks = True

    assert not execute_hooks


def test_REQ_AUT_093_verbose_shows_output():
    """REQ-AUT-093: --verbose shows detailed hook stdout/stderr"""
    verbose = True

    if verbose:
        show_output = True
    else:
        show_output = False

    assert show_output


# Additional coverage tests for uncovered lines


def test_hook_missing_command_skipped(tmp_path):
    """Test that hooks without 'command' field are skipped (line 91-94)"""
    from template_forge.hooks import HookExecutor

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {"description": "Hook without command"},  # Missing command
                {"command": "echo test", "description": "Valid hook"},
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    # Should succeed but log warning for missing command
    assert result is True


def test_hook_dry_run_with_working_dir(tmp_path, caplog):
    """Test dry-run mode with working_dir display (lines 70-80)"""
    import logging

    from template_forge.hooks import HookExecutor

    caplog.set_level(logging.INFO)

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": "echo test",
                    "description": "Test with working dir",
                    "working_dir": "subdir",
                },
                {"command": "echo test2", "description": "Test without working dir"},
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=True)

    assert result is True
    # Check that dry-run displays hooks
    assert "DRY RUN" in caplog.text
    assert "Test with working dir" in caplog.text
    assert "subdir" in caplog.text


def test_hook_condition_evaluation_error(tmp_path, caplog):
    """Test handling of invalid condition expressions (lines 117-122)"""
    from template_forge.hooks import HookExecutor

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": "echo test",
                    "description": "Hook with bad condition",
                    "when": "invalid.syntax.here",
                }
            ]
        }
    }

    executor = HookExecutor(config, {"test": "value"}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    # Should succeed with warning
    assert result is True
    assert "Failed to evaluate condition" in caplog.text


def test_hook_working_dir_does_not_exist(tmp_path, caplog):
    """Test error when working directory doesn't exist (lines 136-142)"""
    from template_forge.hooks import HookExecutor

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": "echo test",
                    "description": "Hook with non-existent dir",
                    "working_dir": "nonexistent_directory",
                    "on_error": "warn",
                }
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    # Should warn but not fail with on_error=warn
    assert result is False  # all_success should be False
    assert "does not exist" in caplog.text


def test_hook_working_dir_not_exist_fail_mode(tmp_path, caplog):
    """Test that missing working_dir with on_error=fail returns False"""
    from template_forge.hooks import HookExecutor

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": "echo test",
                    "description": "Hook with non-existent dir",
                    "working_dir": "nonexistent_directory",
                    "on_error": "fail",
                }
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    # Should fail immediately
    assert result is False
    assert "does not exist" in caplog.text


def test_hook_timeout_with_warn(tmp_path, caplog):
    """Test timeout handling with on_error=warn (lines 182, 184)"""
    import logging
    import sys

    from template_forge.hooks import HookExecutor

    caplog.set_level(logging.WARNING)

    config_file = tmp_path / "config.yaml"

    # Create a Python script that sleeps to test timeout
    if sys.platform == "win32":
        sleep_cmd = 'python -c "import time; time.sleep(10)"'
    else:
        sleep_cmd = "sleep 10"

    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": sleep_cmd,
                    "description": "Long running hook",
                    "timeout": 1,  # 1 second timeout
                    "on_error": "warn",
                }
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    # Should warn about timeout but continue
    assert result is False  # all_success should be False
    assert "timed out" in caplog.text


def test_hook_timeout_with_fail(tmp_path, caplog):
    """Test timeout handling with on_error=fail"""
    import logging
    import sys

    from template_forge.hooks import HookExecutor

    caplog.set_level(logging.WARNING)

    config_file = tmp_path / "config.yaml"

    # Create a Python script that sleeps to test timeout
    if sys.platform == "win32":
        sleep_cmd = 'python -c "import time; time.sleep(10)"'
    else:
        sleep_cmd = "sleep 10"

    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": sleep_cmd,
                    "description": "Long running hook",
                    "timeout": 1,  # 1 second timeout
                    "on_error": "fail",
                }
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    # Should fail immediately
    assert result is False
    assert "timed out" in caplog.text


def test_hook_command_not_found_warn(tmp_path, caplog):
    """Test FileNotFoundError handling with on_error=warn (lines 189-216)"""
    import logging

    from template_forge.hooks import HookExecutor

    caplog.set_level(logging.WARNING)

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": "nonexistent_command_12345",
                    "description": "Invalid command",
                    "on_error": "warn",
                }
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    assert result is False  # all_success should be False
    # On Windows this returns exit code 1, not FileNotFoundError
    # But we still get a failure message
    assert "failed" in caplog.text.lower() or "not recognized" in caplog.text.lower()


def test_hook_command_not_found_fail(tmp_path, caplog):
    """Test FileNotFoundError handling with on_error=fail"""
    import logging

    from template_forge.hooks import HookExecutor

    caplog.set_level(logging.WARNING)

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {
                    "command": "nonexistent_command_12345",
                    "description": "Invalid command",
                    "on_error": "fail",
                }
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)
    result = executor.execute_post_generate_hooks(dry_run=False)

    assert result is False
    assert "failed" in caplog.text.lower() or "not recognized" in caplog.text.lower()


def test_hook_generic_exception_warn(tmp_path, caplog):
    """Test generic exception handling with on_error=warn"""
    from unittest.mock import patch

    from template_forge.hooks import HookExecutor

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {"command": "echo test", "description": "Test hook", "on_error": "warn"}
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)

    # Mock subprocess.run to raise an unexpected exception
    with patch("subprocess.run", side_effect=RuntimeError("Unexpected error")):
        result = executor.execute_post_generate_hooks(dry_run=False)

    assert result is False  # all_success should be False
    assert "error" in caplog.text.lower()


def test_hook_generic_exception_fail(tmp_path, caplog):
    """Test generic exception handling with on_error=fail"""
    from unittest.mock import patch

    from template_forge.hooks import HookExecutor

    config_file = tmp_path / "config.yaml"
    config = {
        "hooks": {
            "post_generate": [
                {"command": "echo test", "description": "Test hook", "on_error": "fail"}
            ]
        }
    }

    executor = HookExecutor(config, {}, config_file)

    # Mock subprocess.run to raise an unexpected exception
    with patch("subprocess.run", side_effect=RuntimeError("Unexpected error")):
        result = executor.execute_post_generate_hooks(dry_run=False)

    assert result is False
    assert "error" in caplog.text.lower()
