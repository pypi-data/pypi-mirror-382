import pytest
from py_boiler.templates import (
    README_CODE,
    MAIN_CODE,
    GITIGNORE_CODE,
    PYPROJECT_TOML,
    VERSION_CODE,
)


class TestTemplates:
    """Test the template constants and their content."""

    def test_readme_code_structure(self):
        """Test that README_CODE has the expected structure and content."""
        assert isinstance(README_CODE, str)
        assert len(README_CODE) > 0

        # Check for key sections
        assert "# py_boiler 🚀" in README_CODE
        assert "A simple boilerplate generator for Python projects." in README_CODE
        assert "## Features" in README_CODE
        assert "## Quickstart" in README_CODE
        assert "```bash" in README_CODE
        assert "pip install py-boiler" in README_CODE
        assert "py-boiler new hello-world" in README_CODE

    def test_readme_code_content_quality(self):
        """Test the quality and completeness of README content."""
        # Should have proper markdown structure
        assert README_CODE.startswith("# ")
        assert "🚀" in README_CODE  # Should have emoji

        # Should contain installation instructions
        assert "pip install" in README_CODE.lower()

        # Should contain usage examples
        assert "```" in README_CODE  # Code blocks

        # Should be informative
        assert len(README_CODE.split("\n")) > 10  # Should have multiple lines

    def test_main_code_structure(self):
        """Test that MAIN_CODE has the expected Python structure."""
        assert isinstance(MAIN_CODE, str)
        assert len(MAIN_CODE) > 0

        # Check for Python function structure
        assert "def main():" in MAIN_CODE
        assert 'print("Hello, World!")' in MAIN_CODE
        assert 'if __name__ == "__main__":' in MAIN_CODE
        assert "main()" in MAIN_CODE

    def test_main_code_executability(self):
        """Test that MAIN_CODE is valid Python code."""
        # Should be able to compile as Python code
        try:
            compile(MAIN_CODE, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"MAIN_CODE contains invalid Python syntax: {e}")

        # Should contain proper indentation
        lines = MAIN_CODE.split("\n")
        for line in lines:
            if (
                line.strip()
                and not line.startswith("def ")
                and not line.startswith("if ")
            ):
                # Non-empty lines should have proper indentation
                if line.strip() != "main()":
                    assert line.startswith("    ") or line.strip() == "main()"

    def test_gitignore_code_structure(self):
        """Test that GITIGNORE_CODE has the expected gitignore structure."""
        assert isinstance(GITIGNORE_CODE, str)
        assert len(GITIGNORE_CODE) > 0

        # Check for common Python gitignore patterns
        assert "__pycache__/" in GITIGNORE_CODE
        assert "*.pyc" in GITIGNORE_CODE
        assert "*.pyo" in GITIGNORE_CODE
        assert "*.pyd" in GITIGNORE_CODE
        assert "*.log" in GITIGNORE_CODE

        # Check for virtual environment patterns
        assert ".venv/" in GITIGNORE_CODE
        assert ".env/" in GITIGNORE_CODE
        assert ".py_boiler_env/" in GITIGNORE_CODE

        # Check for build patterns
        assert "build/" in GITIGNORE_CODE
        assert "dist/" in GITIGNORE_CODE
        assert "*.egg-info/" in GITIGNORE_CODE

    def test_gitignore_code_completeness(self):
        """Test that GITIGNORE_CODE covers essential Python patterns."""
        gitignore_lines = GITIGNORE_CODE.split("\n")

        # Should have section comments
        assert any("# Python" in line for line in gitignore_lines)
        assert any("# Virtual envs" in line for line in gitignore_lines)
        assert any("# Build" in line for line in gitignore_lines)

        # Should have essential patterns
        essential_patterns = [
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".venv/",
            "build/",
            "dist/",
        ]

        for pattern in essential_patterns:
            assert pattern in GITIGNORE_CODE, (
                f"Missing essential gitignore pattern: {pattern}"
            )

    def test_pyproject_toml_structure(self):
        """Test that PYPROJECT_TOML has the expected TOML structure."""
        assert isinstance(PYPROJECT_TOML, str)
        assert len(PYPROJECT_TOML) > 0

        # Check for key TOML sections
        assert "[project]" in PYPROJECT_TOML
        assert "[project.scripts]" in PYPROJECT_TOML
        assert "[build-system]" in PYPROJECT_TOML

        # Check for essential project metadata
        assert 'name = "py-boiler"' in PYPROJECT_TOML
        assert 'version = "1.0.0-alpha"' in PYPROJECT_TOML
        assert "description =" in PYPROJECT_TOML
        assert "authors =" in PYPROJECT_TOML
        assert 'readme = "README.md"' in PYPROJECT_TOML
        assert "license =" in PYPROJECT_TOML
        assert 'requires-python = ">=3.9"' in PYPROJECT_TOML

    def test_pyproject_toml_dependencies(self):
        """Test that PYPROJECT_TOML has correct dependencies."""
        assert "dependencies = [" in PYPROJECT_TOML
        assert '"click>=8.0"' in PYPROJECT_TOML

        # Check for build system
        assert 'requires = ["hatchling"]' in PYPROJECT_TOML
        assert 'build-backend = "hatchling.build"' in PYPROJECT_TOML

    def test_pyproject_toml_scripts(self):
        """Test that PYPROJECT_TOML has correct script configuration."""
        assert 'py-boiler = "app:main"' in PYPROJECT_TOML

    def test_version_code_structure(self):
        """Test that VERSION_CODE has the expected version structure."""
        assert isinstance(VERSION_CODE, str)
        assert len(VERSION_CODE) > 0

        # Should be a valid Python assignment
        assert "__version__ =" in VERSION_CODE
        assert '"1.0.0-alpha"' in VERSION_CODE

        # Should be valid Python syntax
        try:
            compile(VERSION_CODE, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"VERSION_CODE contains invalid Python syntax: {e}")

    def test_templates_consistency(self):
        """Test that all templates are consistent with each other."""
        # Version should match between PYPROJECT_TOML and VERSION_CODE
        assert "1.0.0-alpha" in PYPROJECT_TOML
        assert "1.0.0-alpha" in VERSION_CODE

        # Project name should be consistent
        assert "py-boiler" in PYPROJECT_TOML
        assert "py_boiler" in README_CODE  # Note: different naming convention

    def test_templates_encoding(self):
        """Test that all templates are properly encoded strings."""
        templates = [
            README_CODE,
            MAIN_CODE,
            GITIGNORE_CODE,
            PYPROJECT_TOML,
            VERSION_CODE,
        ]

        for template in templates:
            assert isinstance(template, str)
            # Should be able to encode/decode without issues
            encoded = template.encode("utf-8")
            decoded = encoded.decode("utf-8")
            assert decoded == template

    def test_templates_no_whitespace_issues(self):
        """Test that templates don't have problematic whitespace."""
        templates = [
            README_CODE,
            MAIN_CODE,
            GITIGNORE_CODE,
            PYPROJECT_TOML,
            VERSION_CODE,
        ]

        for template in templates:
            # Should not have trailing whitespace on lines
            lines = template.split("\n")
            for i, line in enumerate(lines):
                if line.rstrip() != line:
                    pytest.fail(f"Line {i + 1} has trailing whitespace in template")

            # Should not have excessive blank lines at the end
            if template.endswith("\n\n\n"):
                pytest.fail("Template has excessive trailing newlines")

    def test_templates_importability(self):
        """Test that all template constants can be imported without issues."""
        # This test is implicitly passing if we can import all constants
        # without any import errors
        assert README_CODE is not None
        assert MAIN_CODE is not None
        assert GITIGNORE_CODE is not None
        assert PYPROJECT_TOML is not None
        assert VERSION_CODE is not None

    def test_templates_content_length(self):
        """Test that templates have reasonable content length."""
        # README should be substantial
        assert len(README_CODE) > 200

        # Main code should be minimal but complete
        assert 50 < len(MAIN_CODE) < 200

        # Gitignore should have reasonable number of patterns
        assert len(GITIGNORE_CODE) > 100

        # Pyproject.toml should be comprehensive
        assert len(PYPROJECT_TOML) > 300

        # Version should be minimal
        assert len(VERSION_CODE) < 50

    def test_templates_special_characters(self):
        """Test that templates handle special characters correctly."""
        # README should have emoji
        assert "🚀" in README_CODE

        # Should handle quotes properly
        assert '"Hello, World!"' in MAIN_CODE

        # Should handle backslashes in paths
        assert "\\" in GITIGNORE_CODE or "/" in GITIGNORE_CODE

        # Should handle quotes in TOML
        assert '"' in PYPROJECT_TOML

    def test_templates_line_endings(self):
        """Test that templates use consistent line endings."""
        templates = [
            README_CODE,
            MAIN_CODE,
            GITIGNORE_CODE,
            PYPROJECT_TOML,
            VERSION_CODE,
        ]

        for template in templates:
            # Should use Unix line endings (LF) not Windows (CRLF)
            assert "\r\n" not in template
            # Should have proper line endings
            if template.strip():  # Non-empty template
                assert template.endswith("\n") or template.endswith("\r")
