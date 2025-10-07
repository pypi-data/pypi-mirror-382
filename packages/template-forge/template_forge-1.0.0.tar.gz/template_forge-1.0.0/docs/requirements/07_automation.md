# Automation and Hooks - Requirements

## 1. Post-Generation Hooks

**REQ-AUT-001**: The system shall support executing commands after successful template generation.

**REQ-AUT-002**: Post-generation hooks shall be defined in the configuration file under a `hooks` section:
```yaml
hooks:
  post_generate:
    - command: "black output/*.py"
      description: "Format Python files"
    - command: "npm install"
      description: "Install dependencies"
      working_dir: "output"
```

**REQ-AUT-003**: Each hook entry shall specify:
- `command` (required): Shell command to execute
- `description` (optional): Human-readable description of what the hook does
- `working_dir` (optional): Directory to execute command in (default: current directory)
- `on_error` (optional): Behavior on error (`ignore`, `warn`, `fail`) - default: `warn`

**REQ-AUT-004**: Hooks shall be executed in the order they are defined in the configuration.

**REQ-AUT-005**: The system shall log each hook execution with its description (if provided).

**REQ-AUT-006**: Hook commands shall have access to environment variables including:
- `TEMPLATE_FORGE_CONFIG`: Path to the configuration file
- `TEMPLATE_FORGE_OUTPUT_DIR`: Base output directory (if determinable)
- All system environment variables

## 2. Hook Execution

**REQ-AUT-010**: Hooks shall only execute after ALL templates have been successfully generated.

**REQ-AUT-011**: If any template generation fails, hooks shall NOT be executed.

**REQ-AUT-012**: Hook commands shall be executed in a shell environment (supports pipes, redirects, etc.).

**REQ-AUT-013**: Each hook command shall have a timeout (configurable, default: 300 seconds / 5 minutes).

**REQ-AUT-014**: The system shall capture both stdout and stderr from hook commands.

**REQ-AUT-015**: Hook output shall be logged at INFO level (stdout) and WARNING level (stderr).

**REQ-AUT-016**: The system shall wait for each hook to complete before executing the next one.

## 3. Error Handling

**REQ-AUT-020**: Hook execution errors shall be handled according to the `on_error` setting:
- `ignore`: Continue to next hook, log at DEBUG level
- `warn`: Continue to next hook, log at WARNING level (default)
- `fail`: Stop hook execution, exit with error code

**REQ-AUT-021**: A hook shall be considered failed if:
- Exit code is non-zero
- Timeout is exceeded
- Command cannot be executed

**REQ-AUT-022**: Timeout errors shall provide a clear message:
```
WARNING: Hook 'Format Python files' timed out after 300 seconds
```

**REQ-AUT-023**: Command not found errors shall suggest checking the PATH:
```
ERROR: Hook command failed: 'black' not found
Suggestion: Ensure 'black' is installed and in your PATH
```

## 4. Conditional Hook Execution

**REQ-AUT-030**: Hooks shall support a `when` condition for conditional execution:
```yaml
hooks:
  post_generate:
    - command: "docker build -t myapp ."
      description: "Build Docker image"
      when: "deployment_type == 'docker'"
```

**REQ-AUT-031**: The `when` condition shall use the same expression syntax as conditional templates.

**REQ-AUT-032**: Hooks with failing conditions shall be skipped silently (logged at DEBUG level).

**REQ-AUT-033**: The condition shall have access to all resolved tokens/variables.

## 5. Hook Types

**REQ-AUT-040**: The system shall support multiple hook types (extensible for future):
- `post_generate`: Execute after all templates are generated
- `pre_generate`: Execute before any template processing (future)
- `on_error`: Execute if generation fails (future)

**REQ-AUT-041**: Currently, only `post_generate` hooks shall be implemented.

**REQ-AUT-042**: Hook type specification determines when hooks are executed in the generation lifecycle.

## 6. Working Directory

**REQ-AUT-050**: If `working_dir` is specified for a hook, it shall be resolved relative to:
1. The configuration file directory (if relative path)
2. As absolute path (if absolute path)

**REQ-AUT-051**: If `working_dir` does not exist, the hook shall fail with a clear error.

**REQ-AUT-052**: If `working_dir` is not specified, hooks shall execute in the current working directory.

## 7. Shell Commands

**REQ-AUT-060**: Hook commands shall support full shell syntax:
- Pipes: `command1 | command2`
- Redirects: `command > file.txt`
- Background: `command &` (not recommended)
- Conditional: `command1 && command2`
- Multiple: `command1; command2`

**REQ-AUT-061**: Commands shall be executed via the system's default shell:
- `bash` on Linux/macOS
- `cmd.exe` or `powershell` on Windows

**REQ-AUT-062**: Shell-specific features shall be platform-dependent (users responsible for cross-platform compatibility).

## 8. Security Considerations

**REQ-AUT-070**: Hooks execute arbitrary shell commands - configuration files from untrusted sources should be reviewed carefully.

**REQ-AUT-071**: The system shall log a warning on first hook execution:
```
INFO: Executing post-generation hooks. Review commands in config.yaml for security.
```

**REQ-AUT-072**: Hook commands shall not perform shell escaping/sanitization - users are responsible for safe command construction.

**REQ-AUT-073**: The `--dry-run` mode shall display hooks that would be executed without running them.

## 9. Logging and Feedback

**REQ-AUT-080**: Hook execution shall provide clear feedback:
```
INFO: Running post-generation hooks...
INFO: [1/3] Format Python files
INFO:   → black output/*.py
INFO:   ✓ Completed in 2.3s
INFO: [2/3] Install dependencies
INFO:   → npm install
INFO:   ✓ Completed in 15.7s
INFO: [3/3] Create archive
INFO:   → tar -czf release.tar.gz output/
INFO:   ✓ Completed in 0.5s
INFO: All hooks completed successfully
```

**REQ-AUT-081**: Failed hooks shall display clear error information:
```
WARNING: [2/3] Install dependencies
WARNING:   → npm install
WARNING:   ✗ Failed with exit code 1
WARNING:   stderr: npm ERR! Missing package.json
WARNING: Hook failed but continuing (on_error: warn)
```

**REQ-AUT-082**: Hook output shall respect the `--verbose` flag for detailed logging.

## 10. Examples

### Basic Hook Configuration
```yaml
# config.yaml
templates:
  - template: main.py.j2
    output: output/main.py

hooks:
  post_generate:
    - command: "black output/*.py"
      description: "Format Python code"
    
    - command: "chmod +x output/main.py"
      description: "Make script executable"
```

### Hooks with Error Handling
```yaml
hooks:
  post_generate:
    - command: "pylint output/*.py"
      description: "Lint Python code"
      on_error: ignore  # Continue even if linting fails
    
    - command: "pytest tests/"
      description: "Run tests"
      on_error: fail  # Stop if tests fail
```

### Conditional Hooks
```yaml
hooks:
  post_generate:
    - command: "docker build -t myapp:{{ version }} ."
      description: "Build Docker image"
      when: "deployment_type == 'docker'"
    
    - command: "npm run build"
      description: "Build frontend"
      when: "build_frontend is defined and build_frontend"
    
    - command: "rsync -av output/ /var/www/html/"
      description: "Deploy to production"
      when: "environment == 'production'"
```

### Complex Hook with Working Directory
```yaml
hooks:
  post_generate:
    - command: |
        npm install &&
        npm run build &&
        npm test
      description: "Build and test Node.js application"
      working_dir: "output/app"
      on_error: fail
```

### Multiple Operations in Sequence
```yaml
hooks:
  post_generate:
    # Format generated code
    - command: "black *.py"
      description: "Format Python files"
      working_dir: "output"
    
    # Generate documentation
    - command: "sphinx-build -b html docs/ docs/_build/"
      description: "Build documentation"
    
    # Create distribution package
    - command: "python -m build"
      description: "Build Python package"
      working_dir: "output"
    
    # Run final validation
    - command: "python -m pytest tests/ -v"
      description: "Run test suite"
      on_error: fail
```

## 11. CLI Integration

**REQ-AUT-090**: The CLI shall support a `--no-hooks` flag to skip hook execution.

**REQ-AUT-091**: The `--dry-run` flag shall display hooks without executing them:
```
[DRY RUN] Would execute 3 post-generation hooks:
  1. Format Python files: black output/*.py
  2. Install dependencies: npm install (in output/)
  3. Create archive: tar -czf release.tar.gz output/
```

**REQ-AUT-092**: Hook execution shall be skipped in `--validate` mode.

**REQ-AUT-093**: The `--verbose` flag shall show detailed hook output including all stdout/stderr.
