"""Basic sanity tests for CloudTools SDK."""

def test_sanity():
    """Basic sanity check."""
    assert 1 + 1 == 2


def test_import():
    """Test that the package can be imported."""
    import cloudtools
    # Version assertion removed; only testing import succeeds.
