"""Tests for REQ-ADV-004: Environment and Context Variables

This module tests the support for environment variables and context variables
in static token definitions, including ${ENV.VAR}, ${CWD}, ${CONFIG_DIR},
${TIMESTAMP}, and ${DATE}.
"""

import os
from datetime import datetime
from pathlib import Path

import pytest

from template_forge.core import StructuredDataExtractor


class TestEnvironmentVariables:
    """Test ${ENV.VAR_NAME} support."""

    def test_env_variable_access(self, tmp_path):
        """Test accessing environment variables via ${ENV.VAR_NAME}."""
        # Set environment variable
        os.environ["TEST_USER"] = "john_doe"

        config = {
            "static_tokens": {
                "username": "${ENV.TEST_USER}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["username"] == "john_doe"

        # Clean up
        del os.environ["TEST_USER"]

    def test_env_variable_in_complex_value(self, tmp_path):
        """Test environment variables in string interpolation."""
        os.environ["API_HOST"] = "api.example.com"
        os.environ["API_PORT"] = "8080"

        config = {
            "static_tokens": {
                "api_url": {"value": "https://${ENV.API_HOST}:${ENV.API_PORT}/v1"}
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["api_url"] == "https://api.example.com:8080/v1"

        # Clean up
        del os.environ["API_HOST"]
        del os.environ["API_PORT"]

    def test_env_variable_not_set_warning(self, tmp_path, caplog):
        """Test warning when environment variable is not set."""
        config = {
            "static_tokens": {
                "missing_var": "${ENV.NONEXISTENT_VAR}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should keep original reference when not found
        assert tokens["missing_var"] == "${ENV.NONEXISTENT_VAR}"
        assert (
            "Environment variable 'NONEXISTENT_VAR' referenced but not set"
            in caplog.text
        )

    def test_required_env_variable_set(self, tmp_path):
        """Test required environment variable that is set."""
        os.environ["API_KEY"] = "secret123"

        config = {
            "static_tokens": {
                "api_key": {
                    "value": "${ENV.API_KEY}",
                    "required": True,
                }
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["api_key"] == "secret123"

        # Clean up
        del os.environ["API_KEY"]

    def test_required_env_variable_not_set_error(self, tmp_path):
        """Test required environment variable that is not set raises error."""
        config = {
            "static_tokens": {
                "api_key": {
                    "value": "${ENV.MISSING_KEY}",
                    "required": True,
                }
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)

        with pytest.raises(
            ValueError, match="required environment variable 'MISSING_KEY' is not set"
        ):
            extractor.extract_tokens()

    def test_multiple_env_variables(self, tmp_path):
        """Test multiple environment variables in configuration."""
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_PORT"] = "5432"
        os.environ["DB_NAME"] = "testdb"
        os.environ["DB_USER"] = "admin"

        config = {
            "static_tokens": {
                "database": {
                    "host": "${ENV.DB_HOST}",
                    "port": "${ENV.DB_PORT}",
                    "name": "${ENV.DB_NAME}",
                    "user": "${ENV.DB_USER}",
                }
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["database"]["host"] == "localhost"
        assert tokens["database"]["port"] == "5432"
        assert tokens["database"]["name"] == "testdb"
        assert tokens["database"]["user"] == "admin"

        # Clean up
        for key in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER"]:
            del os.environ[key]

    def test_env_variable_with_transform(self, tmp_path):
        """Test environment variable with transformation."""
        os.environ["PROJECT_NAME"] = "my-project"

        config = {
            "static_tokens": {
                "project_upper": {
                    "value": "${ENV.PROJECT_NAME}",
                    "transform": "upper",
                }
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["project_upper"] == "MY-PROJECT"

        # Clean up
        del os.environ["PROJECT_NAME"]


class TestContextVariables:
    """Test ${CWD}, ${CONFIG_DIR}, ${TIMESTAMP}, ${DATE} support."""

    def test_cwd_absolute_path(self, tmp_path):
        """Test ${CWD} returns current working directory."""
        config = {
            "static_tokens": {
                "workspace_dir": "${CWD}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should be absolute path to current directory
        assert tokens["workspace_dir"] == str(Path.cwd())
        assert Path(tokens["workspace_dir"]).is_absolute()

    def test_cwd_basename(self, tmp_path):
        """Test ${CWD.basename} returns directory name only."""
        config = {
            "static_tokens": {
                "workspace_name": "${CWD.basename}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should be just the directory name
        assert tokens["workspace_name"] == Path.cwd().name
        assert "/" not in tokens["workspace_name"]
        assert "\\" not in tokens["workspace_name"]

    def test_config_dir(self, tmp_path):
        """Test ${CONFIG_DIR} returns configuration file directory."""
        config = {
            "static_tokens": {
                "config_location": "${CONFIG_DIR}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Without a config file, should use current directory
        assert tokens["config_location"] == str(Path.cwd())

    def test_timestamp_format(self, tmp_path):
        """Test ${TIMESTAMP} returns ISO format timestamp."""
        config = {
            "static_tokens": {
                "generated_at": "${TIMESTAMP}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should be valid ISO format timestamp
        timestamp = tokens["generated_at"]
        # Parse to validate format
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

        # Should be close to current time (within 5 seconds)
        now = datetime.now()
        delta = abs((now - parsed).total_seconds())
        assert delta < 5

    def test_date_format(self, tmp_path):
        """Test ${DATE} returns YYYY-MM-DD format."""
        config = {
            "static_tokens": {
                "release_date": "${DATE}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should be valid YYYY-MM-DD format
        date_str = tokens["release_date"]
        assert len(date_str) == 10
        assert date_str[4] == "-"
        assert date_str[7] == "-"

        # Should be today's date
        expected_date = datetime.now().strftime("%Y-%m-%d")
        assert date_str == expected_date

    def test_multiple_context_variables(self, tmp_path):
        """Test multiple context variables together."""
        config = {
            "static_tokens": {
                "build_info": {
                    "workspace": "${CWD}",
                    "workspace_name": "${CWD.basename}",
                    "config_dir": "${CONFIG_DIR}",
                    "timestamp": "${TIMESTAMP}",
                    "date": "${DATE}",
                }
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        build_info = tokens["build_info"]
        assert build_info["workspace"] == str(Path.cwd())
        assert build_info["workspace_name"] == Path.cwd().name
        assert build_info["config_dir"] == str(Path.cwd())

        # Validate timestamp and date
        datetime.fromisoformat(build_info["timestamp"])
        assert len(build_info["date"]) == 10

    def test_context_in_string_interpolation(self, tmp_path):
        """Test context variables in string interpolation."""
        config = {
            "static_tokens": {
                "header_comment": {"value": "Generated from ${CONFIG_DIR} on ${DATE}"}
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        today = datetime.now().strftime("%Y-%m-%d")
        expected = f"Generated from {Path.cwd()} on {today}"
        assert tokens["header_comment"] == expected


class TestMixedVariables:
    """Test combinations of environment and context variables."""

    def test_env_and_context_together(self, tmp_path):
        """Test using both environment and context variables."""
        os.environ["BUILD_USER"] = "jenkins"

        config = {
            "static_tokens": {
                "build_metadata": {
                    "user": "${ENV.BUILD_USER}",
                    "workspace": "${CWD.basename}",
                    "timestamp": "${TIMESTAMP}",
                }
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        metadata = tokens["build_metadata"]
        assert metadata["user"] == "jenkins"
        assert metadata["workspace"] == Path.cwd().name
        datetime.fromisoformat(metadata["timestamp"])

        # Clean up
        del os.environ["BUILD_USER"]

    def test_context_variables_in_paths(self, tmp_path):
        """Test context variables used to construct paths."""
        config = {
            "static_tokens": {
                "output_dir": {"value": "${CWD}/output"},
                "config_backup": {"value": "${CONFIG_DIR}/backup"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["output_dir"] == f"{Path.cwd()}/output"
        assert tokens["config_backup"] == f"{Path.cwd()}/backup"

    def test_env_context_and_token_references(self, tmp_path):
        """Test mixing environment, context, and token references."""
        os.environ["DEPLOY_ENV"] = "production"

        config = {
            "static_tokens": {
                "environment": "${ENV.DEPLOY_ENV}",
                "workspace_name": "${CWD.basename}",
                "deployment_id": {"value": "${environment}-${workspace_name}-${DATE}"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        today = datetime.now().strftime("%Y-%m-%d")
        workspace = Path.cwd().name
        expected = f"production-{workspace}-{today}"

        assert tokens["deployment_id"] == expected

        # Clean up
        del os.environ["DEPLOY_ENV"]

    def test_template_with_context_variables(self, tmp_path):
        """Test that context variables work in token extraction."""
        os.environ["APP_VERSION"] = "2.0.0"

        config = {
            "static_tokens": {
                "app_version": "${ENV.APP_VERSION}",
                "generated_at": "${TIMESTAMP}",
                "workspace": "${CWD.basename}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Verify tokens were correctly extracted
        assert tokens["app_version"] == "2.0.0"
        assert tokens["workspace"] == Path.cwd().name

        # Verify timestamp is valid
        datetime.fromisoformat(tokens["generated_at"])

        # Clean up
        del os.environ["APP_VERSION"]


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_env_variable_name(self, tmp_path):
        """Test handling of invalid environment variable names."""
        config = {
            "static_tokens": {
                "invalid": "${ENV.}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should keep original reference
        assert tokens["invalid"] == "${ENV.}"

    def test_context_variable_case_sensitive(self, tmp_path):
        """Test that context variables are case-sensitive."""
        config = {
            "static_tokens": {
                "lower_cwd": "${cwd}",
                "upper_cwd": "${CWD}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # lowercase 'cwd' should not match, uppercase 'CWD' should
        assert tokens["lower_cwd"] == "${cwd}"  # Not found, keep original
        assert tokens["upper_cwd"] == str(Path.cwd())

    def test_nested_references_with_context(self, tmp_path):
        """Test nested token references with context variables."""
        os.environ["PREFIX"] = "prod"

        config = {
            "static_tokens": {
                "prefix": "${ENV.PREFIX}",
                "workspace": "${CWD.basename}",
                "full_name": {"value": "${prefix}_${workspace}"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        expected = f"prod_{Path.cwd().name}"
        assert tokens["full_name"] == expected

        # Clean up
        del os.environ["PREFIX"]

    def test_empty_env_variable(self, tmp_path):
        """Test handling of empty environment variable."""
        os.environ["EMPTY_VAR"] = ""

        config = {
            "static_tokens": {
                "empty": "${ENV.EMPTY_VAR}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should get empty string
        assert tokens["empty"] == ""

        # Clean up
        del os.environ["EMPTY_VAR"]

    def test_special_characters_in_env_value(self, tmp_path):
        """Test environment variables with special characters."""
        os.environ["SPECIAL_VAR"] = "value with spaces & symbols!@#$%"

        config = {
            "static_tokens": {
                "special": "${ENV.SPECIAL_VAR}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["special"] == "value with spaces & symbols!@#$%"

        # Clean up
        del os.environ["SPECIAL_VAR"]

    def test_numeric_env_values(self, tmp_path):
        """Test environment variables with numeric values."""
        os.environ["PORT"] = "8080"
        os.environ["TIMEOUT"] = "30.5"

        config = {
            "static_tokens": {
                "port": "${ENV.PORT}",
                "timeout": "${ENV.TIMEOUT}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Environment variables are always strings
        assert tokens["port"] == "8080"
        assert tokens["timeout"] == "30.5"

        # Clean up
        del os.environ["PORT"]
        del os.environ["TIMEOUT"]
