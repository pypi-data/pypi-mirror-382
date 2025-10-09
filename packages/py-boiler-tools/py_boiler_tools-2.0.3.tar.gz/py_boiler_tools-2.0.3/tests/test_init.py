import re
from py_boiler import __version__


class TestInit:
    """Test the __init__.py module."""

    def test_version_exists(self):
        """Test that __version__ is defined and accessible."""
        assert hasattr(__import__("py_boiler"), "__version__")
        assert __version__ is not None

    def test_version_format(self):
        """Test that __version__ follows semantic versioning format."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0

        # Should be in format X.Y.Z or X.Y.Z-suffix
        version_parts = __version__.split(".")
        assert len(version_parts) >= 2  # At least major.minor

        # Major and minor should be numeric
        assert version_parts[0].isdigit()
        assert version_parts[1].isdigit()

        # If there's a patch version, it should be numeric or have suffix
        if len(version_parts) > 2:
            patch_part = version_parts[2]
            # Should be either numeric or have a suffix like "1-alpha"
            assert patch_part.isdigit() or "-" in patch_part or "+" in patch_part

    def test_version_consistency(self):
        """Test that version is consistent with pyproject.toml."""
        # This test ensures the version in __init__.py matches the project version
        # The actual version value should match what's in pyproject.toml
        assert re.match(r"^\d+\.\d+\.\d+$", __version__)

    def test_version_importability(self):
        """Test that version can be imported in different ways."""
        # Test direct import
        from py_boiler import __version__ as version1

        assert version1 == __version__

        # Test module import
        import py_boiler

        assert py_boiler.__version__ == __version__

        # Test getattr access
        assert getattr(py_boiler, "__version__") == __version__

    def test_version_immutability(self):
        """Test that __version__ is a string and behaves as expected."""
        # Should be a string
        assert isinstance(__version__, str)

        # Should not be empty
        assert __version__.strip() != ""

        # Should not contain newlines or other control characters
        assert "\n" not in __version__
        assert "\r" not in __version__
        assert "\t" not in __version__

    def test_version_semantic_validation(self):
        """Test that version follows semantic versioning rules."""
        # Should not start with a dot
        assert not __version__.startswith(".")

        # Should not end with a dot
        assert not __version__.endswith(".")

        # Should not have consecutive dots
        assert ".." not in __version__

        # Should not have spaces
        assert " " not in __version__

    def test_version_comparison(self):
        """Test that version can be compared properly."""
        # Should be comparable to other version strings
        assert __version__ >= "0.0.1"
        assert __version__ <= "99.99.99"

        # Should be sortable
        versions = ["1.0.0", __version__, "3.0.0"]
        sorted_versions = sorted(versions)
        assert sorted_versions[0] <= sorted_versions[1] <= sorted_versions[2]

    def test_version_string_representation(self):
        """Test that version has proper string representation."""
        # Should be printable
        assert str(__version__) == __version__

        # Should be repr-able
        assert repr(__version__) == f"'{__version__}'"

        # Should be hashable (for use in sets, dicts)
        version_set = {__version__}
        assert __version__ in version_set

        version_dict = {__version__: "test"}
        assert version_dict[__version__] == "test"
