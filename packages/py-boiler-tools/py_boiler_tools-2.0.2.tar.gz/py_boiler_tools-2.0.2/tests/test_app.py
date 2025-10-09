import tempfile
import os
from pathlib import Path
from click.testing import CliRunner

from py_boiler.app import main, new, basic


class TestAppCLI:
    """Test the main CLI application."""

    def test_main_group(self):
        """Test that the main group is properly configured."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Py-Boiler: Generate boilerplate Python apps." in result.output

    def test_new_group(self):
        """Test that the new group is properly configured."""
        runner = CliRunner()
        result = runner.invoke(new, ["--help"])
        assert result.exit_code == 0
        assert "Scaffold new boilerplate projects." in result.output

    def test_basic_command_help(self):
        """Test that the basic command shows proper help."""
        runner = CliRunner()
        result = runner.invoke(basic, ["--help"])
        assert result.exit_code == 0
        assert "Generate a Hello World app.py file." in result.output


class TestBasicCommand:
    """Test the basic command functionality."""

    def test_basic_command_creates_files(self):
        """Test that basic command creates all expected files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()
                result = runner.invoke(basic)

                assert result.exit_code == 0

                # Check that all expected files were created
                expected_files = ["README.md", "app.py", ".gitignore", "__init__.py"]
                for file in expected_files:
                    assert Path(file).exists(), f"File {file} should have been created"

                # Check that success messages were printed
                assert (
                    "✅ Created README.md with Hello World template." in result.output
                )
                assert "✅ Created app.py with Hello World template." in result.output
                assert (
                    "✅ Created .gitignore with Hello World template." in result.output
                )
                assert (
                    "✅ Created __init__.py with Hello World template." in result.output
                )

            finally:
                os.chdir(original_cwd)

    def test_basic_command_with_existing_files(self):
        """Test that basic command doesn't overwrite existing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Create existing files
                existing_files = ["README.md", "app.py"]
                for file in existing_files:
                    Path(file).write_text("existing content")

                runner = CliRunner()
                result = runner.invoke(basic)

                assert result.exit_code == 0

                # Check that existing files weren't overwritten
                for file in existing_files:
                    assert Path(file).read_text() == "existing content"
                    assert (
                        f"⚠️  {file} already exists, not overwriting." in result.output
                    )

                # Check that new files were still created
                new_files = [".gitignore", "__init__.py"]
                for file in new_files:
                    assert Path(file).exists()

            finally:
                os.chdir(original_cwd)

    def test_basic_command_file_contents(self):
        """Test that created files contain the correct content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()
                result = runner.invoke(basic)

                assert result.exit_code == 0

                # Test README.md content
                readme_content = Path("README.md").read_text()
                assert "# py_boiler 🚀" in readme_content
                assert (
                    "A simple boilerplate generator for Python projects."
                    in readme_content
                )

                # Test app.py content
                app_content = Path("app.py").read_text()
                assert "def main():" in app_content
                assert 'print("Hello, World!")' in app_content
                assert 'if __name__ == "__main__":' in app_content

                # Test .gitignore content
                gitignore_content = Path(".gitignore").read_text()
                assert "__pycache__/" in gitignore_content
                assert "*.pyc" in gitignore_content
                assert ".venv/" in gitignore_content

                # Test __init__.py content (should be empty)
                init_content = Path("__init__.py").read_text()
                assert init_content == ""

            finally:
                os.chdir(original_cwd)

    def test_basic_command_partial_existing_files(self):
        """Test behavior when only some files already exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Create only one existing file
                Path("README.md").write_text("existing readme")

                runner = CliRunner()
                result = runner.invoke(basic)

                assert result.exit_code == 0

                # Check that existing file wasn't overwritten
                assert Path("README.md").read_text() == "existing readme"
                assert "⚠️  README.md already exists, not overwriting." in result.output

                # Check that other files were created
                other_files = ["app.py", ".gitignore", "__init__.py"]
                for file in other_files:
                    assert Path(file).exists()
                    assert (
                        f"✅ Created {file} with Hello World template." in result.output
                    )

            finally:
                os.chdir(original_cwd)

    def test_basic_command_in_non_empty_directory(self):
        """Test that basic command works in a directory with other files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Create some unrelated files
                Path("other_file.txt").write_text("unrelated content")
                Path("subdir").mkdir()
                Path("subdir/nested.txt").write_text("nested content")

                runner = CliRunner()
                result = runner.invoke(basic)

                assert result.exit_code == 0

                # Check that target files were created
                expected_files = ["README.md", "app.py", ".gitignore", "__init__.py"]
                for file in expected_files:
                    assert Path(file).exists()

                # Check that unrelated files weren't affected
                assert Path("other_file.txt").read_text() == "unrelated content"
                assert Path("subdir/nested.txt").read_text() == "nested content"

            finally:
                os.chdir(original_cwd)


class TestAppIntegration:
    """Integration tests for the app module."""

    def test_import_structure(self):
        """Test that all necessary imports work correctly."""
        from py_boiler.app import main, new, basic
        from py_boiler.templates import README_CODE, MAIN_CODE, GITIGNORE_CODE

        # Test that imports don't raise exceptions
        assert main is not None
        assert new is not None
        assert basic is not None
        assert README_CODE is not None
        assert MAIN_CODE is not None
        assert GITIGNORE_CODE is not None

    def test_cli_help_structure(self):
        """Test the complete CLI help structure."""
        runner = CliRunner()

        # Test main help
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "new" in result.output

        # Test new help
        result = runner.invoke(main, ["new", "--help"])
        assert result.exit_code == 0
        assert "basic" in result.output

        # Test basic help
        result = runner.invoke(main, ["new", "basic", "--help"])
        assert result.exit_code == 0
        assert "Generate a Hello World app.py file." in result.output

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        runner = CliRunner()

        # Test invalid command
        result = runner.invoke(main, ["invalid-command"])
        assert result.exit_code != 0

        # Test invalid subcommand
        result = runner.invoke(main, ["new", "invalid-subcommand"])
        assert result.exit_code != 0
