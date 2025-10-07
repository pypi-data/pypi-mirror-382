"""Test glob pattern with list strategy - reproducing the bug."""

import json
import logging
import tempfile
from pathlib import Path

from template_forge import TemplateForge

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.DEBUG)


def test_glob_pattern_list_strategy_bug():
    """Reproduce the bug with glob pattern and list match strategy.

    This test reproduces the error:
    "string indices must be integers, not 'str'"
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test data files
        data_dir = tmpdir / "data"
        data_dir.mkdir()

        (data_dir / "user1.json").write_text(
            json.dumps(
                {"username": "user1", "name": "Alice", "email": "alice@example.com"}
            )
        )

        (data_dir / "user2.json").write_text(
            json.dumps({"username": "user2", "name": "Bob", "email": "bob@example.com"})
        )

        # Create template
        templates_dir = tmpdir / "templates"
        templates_dir.mkdir()

        # Simple template that doesn't use variables
        (templates_dir / "simple.txt.j2").write_text("Test")

        # Template that uses the users list
        (templates_dir / "users.txt.j2").write_text(
            """
Users:
{% for user in users %}
- {{ user.name }}: {{ user.email }}
{% endfor %}
""".strip()
        )

        # Create config
        config_file = tmpdir / "config.yaml"
        config_file.write_text("""
inputs:
  - path: "data/*.json"
    format: json
    namespace: "users"
    match: "list"

template_dir: "templates"
output_dir: "output"

static_tokens:
  title: "Test"
""")

        # Try to generate - this should reproduce the error
        forge = TemplateForge(config_file)

        # Enable strict mode to get the full exception
        forge.config["jinja_options"] = {"strict_undefined": True}

        # This should fail with "string indices must be integers, not 'str'"
        try:
            forge.run()
        except Exception as e:
            print("\n=== Exception caught ===")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {e}")
            import traceback

            traceback.print_exc()
            raise

        # Check output
        output_dir = tmpdir / "output"
        assert output_dir.exists(), "Output directory should be created"

        # Check generated files
        simple_output = output_dir / "simple.txt"
        users_output = output_dir / "users.txt"

        assert simple_output.exists(), "simple.txt should be generated"
        assert users_output.exists(), "users.txt should be generated"

        print("\n=== simple.txt ===")
        print(simple_output.read_text())

        print("\n=== users.txt ===")
        print(users_output.read_text())


if __name__ == "__main__":
    test_glob_pattern_list_strategy_bug()
    print("Test completed!")
