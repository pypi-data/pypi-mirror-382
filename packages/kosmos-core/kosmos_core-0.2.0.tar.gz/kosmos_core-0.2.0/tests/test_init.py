import kosmos


def test_version_exists() -> None:
    """Test that __version__ is defined."""
    assert hasattr(kosmos, "__version__")


def test_version_format() -> None:
    """Test that __version__ follows semantic versioning format."""
    version = kosmos.__version__
    assert isinstance(version, str)

    # Check if it follows basic semantic versioning (major.minor.patch)
    parts = version.split(".")
    assert len(parts) >= 2, f"Version {version} should have at least major.minor format"

    # Check that each part is numeric
    for i, part in enumerate(parts[:3]):  # Check first 3 parts (major.minor.patch)
        assert part.isdigit(), f"Version part {i} ({part}) should be numeric"
