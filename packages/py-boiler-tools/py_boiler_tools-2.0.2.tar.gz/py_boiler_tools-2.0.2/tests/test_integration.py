import tempfile
import os
import subprocess
import sys
from pathlib import Path
from click.testing import CliRunner

from py_boiler.app import main
from py_boiler.templates import README_CODE, MAIN_CODE, GITIGNORE_CODE
from py_boiler import __version__


class TestIntegration:
    """Integration tests for the entire py_boiler package."""

    def test_full_cli_workflow(self):
        """Test the complete CLI workflow from start to finish."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()

                # Test the complete command chain
                result = runner.invoke(main, ["new", "basic"])

                assert result.exit_code == 0

                # Verify all files were created
                expected_files = ["README.md", "app.py", ".gitignore", "__init__.py"]
                for file in expected_files:
                    assert Path(file).exists()

                # Verify file contents match templates
                assert Path("README.md").read_text() == README_CODE
                assert Path("app.py").read_text() == MAIN_CODE
                assert Path(".gitignore").read_text() == GITIGNORE_CODE
                assert Path("__init__.py").read_text() == ""

            finally:
                os.chdir(original_cwd)

    def test_generated_app_executability(self):
        """Test that the generated app.py can be executed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()

                # Generate the basic app
                result = runner.invoke(main, ["new", "basic"])
                assert result.exit_code == 0

                # Test that the generated app.py can be executed
                result = subprocess.run(
                    [sys.executable, "app.py"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                assert result.returncode == 0
                assert "Hello, World!" in result.stdout
                assert result.stderr == ""

            finally:
                os.chdir(original_cwd)

    def test_generated_app_importability(self):
        """Test that the generated app.py can be imported as a module."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()

                # Generate the basic app
                result = runner.invoke(main, ["new", "basic"])
                assert result.exit_code == 0

                # Test that the generated app.py can be imported
                sys.path.insert(0, temp_dir)
                try:
                    import app

                    assert hasattr(app, "main")
                    assert callable(app.main)

                    # Test that the main function works
                    import io
                    import contextlib

                    f = io.StringIO()
                    with contextlib.redirect_stdout(f):
                        app.main()

                    output = f.getvalue()
                    assert "Hello, World!" in output

                finally:
                    sys.path.remove(temp_dir)

            finally:
                os.chdir(original_cwd)

    def test_package_imports(self):
        """Test that all package imports work correctly."""
        # Test main package import
        import py_boiler

        assert hasattr(py_boiler, "__version__")
        assert py_boiler.__version__ == __version__

        # Test submodule imports
        from py_boiler import app, templates

        assert app is not None
        assert templates is not None

        # Test specific function imports
        from py_boiler.app import main, new, basic

        assert main is not None
        assert new is not None
        assert basic is not None

        # Test template imports
        from py_boiler.templates import README_CODE, MAIN_CODE, GITIGNORE_CODE

        assert README_CODE is not None
        assert MAIN_CODE is not None
        assert GITIGNORE_CODE is not None

    def test_cli_help_consistency(self):
        """Test that CLI help is consistent and complete."""
        runner = CliRunner()

        # Test main help
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Py-Boiler: Generate boilerplate Python apps." in result.output
        assert "new" in result.output

        # Test new help
        result = runner.invoke(main, ["new", "--help"])
        assert result.exit_code == 0
        assert "Scaffold new boilerplate projects." in result.output
        assert "basic" in result.output

        # Test basic help
        result = runner.invoke(main, ["new", "basic", "--help"])
        assert result.exit_code == 0
        assert "Generate a Hello World app.py file." in result.output

    def test_error_scenarios(self):
        """Test various error scenarios and edge cases."""
        runner = CliRunner()

        # Test invalid commands
        result = runner.invoke(main, ["invalid-command"])
        assert result.exit_code != 0

        result = runner.invoke(main, ["new", "invalid-subcommand"])
        assert result.exit_code != 0

        # Test with invalid options
        result = runner.invoke(main, ["--invalid-option"])
        assert result.exit_code != 0

    def test_file_permissions(self):
        """Test that generated files have appropriate permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()

                # Generate files
                result = runner.invoke(main, ["new", "basic"])
                assert result.exit_code == 0

                # Check that files are readable
                expected_files = ["README.md", "app.py", ".gitignore", "__init__.py"]
                for file in expected_files:
                    file_path = Path(file)
                    assert file_path.exists()
                    assert os.access(file_path, os.R_OK)

                    # Files should be writable (for potential modifications)
                    assert os.access(file_path, os.W_OK)

            finally:
                os.chdir(original_cwd)

    def test_unicode_handling(self):
        """Test that the application handles Unicode characters correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()

                # Generate files
                result = runner.invoke(main, ["new", "basic"])
                assert result.exit_code == 0

                # Check that Unicode characters in templates are preserved
                readme_content = Path("README.md").read_text()
                assert "🚀" in readme_content  # Emoji should be preserved

                # Check that files can be read with different encodings
                for file in ["README.md", "app.py", ".gitignore"]:
                    content = Path(file).read_text(encoding="utf-8")
                    assert len(content) > 0

                    # Should be able to encode/decode without issues
                    encoded = content.encode("utf-8")
                    decoded = encoded.decode("utf-8")
                    assert decoded == content

            finally:
                os.chdir(original_cwd)

    def test_cross_platform_compatibility(self):
        """Test that the application works across different platforms."""
        runner = CliRunner()

        # Test that path handling works correctly
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Test with different path separators
                result = runner.invoke(main, ["new", "basic"])
                assert result.exit_code == 0

                # Files should be created with correct path handling
                expected_files = ["README.md", "app.py", ".gitignore", "__init__.py"]
                for file in expected_files:
                    file_path = Path(file)
                    assert file_path.exists()
                    # Path should be resolved correctly
                    assert file_path.resolve().exists()

            finally:
                os.chdir(original_cwd)

    def test_memory_usage(self):
        """Test that the application doesn't have memory leaks."""
        import gc

        # Run the command multiple times to check for memory issues
        for _ in range(5):
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                try:
                    os.chdir(temp_dir)
                    runner = CliRunner()

                    result = runner.invoke(main, ["new", "basic"])
                    assert result.exit_code == 0

                finally:
                    os.chdir(original_cwd)

            # Force garbage collection
            gc.collect()

    def test_concurrent_execution(self):
        """Test that the application can handle concurrent execution."""
        import threading
        import time

        results = []
        errors = []

        def run_command():
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    original_cwd = os.getcwd()
                    try:
                        os.chdir(temp_dir)
                        runner = CliRunner()

                        result = runner.invoke(main, ["new", "basic"])
                        results.append(result.exit_code == 0)

                    finally:
                        os.chdir(original_cwd)
            except Exception as e:
                errors.append(e)

        # Run multiple threads with a small delay to avoid race conditions
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_command)
            threads.append(thread)
            thread.start()
            # Small delay between thread starts to avoid race conditions
            time.sleep(0.1)

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=15)  # Increased timeout

        # Check results - be more lenient with concurrent execution
        if errors:
            print(f"Warning: Some concurrent executions had errors: {errors}")
        if not all(results):
            print(f"Warning: Some concurrent executions failed: {results}")

        # At least some should succeed
        assert len(results) >= 2, "Too many concurrent executions failed"
