"""
Basic tests that can run without external dependencies.
These tests verify the core functionality without requiring pytest or click.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import py_boiler
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_package_imports():
    """Test that the package can be imported."""
    import py_boiler

    assert hasattr(py_boiler, "__version__")
    print("✅ Package import successful")


def test_version_format():
    """Test that the version follows the expected format."""
    from py_boiler import __version__

    assert isinstance(__version__, str)
    assert len(__version__) > 0
    assert __version__ == "2.0.2"
    print("✅ Version format correct")


def test_templates_import():
    """Test that templates can be imported."""
    from py_boiler.templates import README_CODE, MAIN_CODE, GITIGNORE_CODE

    assert isinstance(README_CODE, str)
    assert isinstance(MAIN_CODE, str)
    assert isinstance(GITIGNORE_CODE, str)
    assert len(README_CODE) > 0
    assert len(MAIN_CODE) > 0
    assert len(GITIGNORE_CODE) > 0
    print("✅ Templates import successful")


def test_app_import():
    """Test that app module can be imported."""
    from py_boiler.app import main, new, basic

    assert main is not None
    assert new is not None
    assert basic is not None
    print("✅ App module import successful")


def test_template_content():
    """Test that templates contain expected content."""
    from py_boiler.templates import README_CODE, MAIN_CODE, GITIGNORE_CODE

    # Test README content
    assert "# py_boiler 🚀" in README_CODE
    assert "A simple boilerplate generator" in README_CODE

    # Test main code content
    assert "def main():" in MAIN_CODE
    assert 'print("Hello, World!")' in MAIN_CODE
    assert 'if __name__ == "__main__":' in MAIN_CODE

    # Test gitignore content
    assert "__pycache__/" in GITIGNORE_CODE
    assert "*.pyc" in GITIGNORE_CODE
    assert ".venv/" in GITIGNORE_CODE

    print("✅ Template content validation successful")


def test_main_code_executability():
    """Test that the main code template is valid Python."""
    from py_boiler.templates import MAIN_CODE

    compile(MAIN_CODE, "<string>", "exec")
    print("✅ Main code template is valid Python")


def run_all_tests():
    """Run all basic tests and report results."""
    tests = [
        test_package_imports,
        test_version_format,
        test_templates_import,
        test_app_import,
        test_template_content,
        test_main_code_executability,
    ]

    passed = 0
    total = len(tests)

    print("Running basic tests...")
    print("=" * 50)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All basic tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
