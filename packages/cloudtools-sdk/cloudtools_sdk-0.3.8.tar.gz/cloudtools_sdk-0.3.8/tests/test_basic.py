"""Basic sanity tests for CloudTools SDK."""

def test_sanity():
    """Basic sanity check."""
    assert 1 + 1 == 2


def test_import():
    """Test that the package can be imported."""
    import cloudtools
    assert cloudtools.__version__ == "0.1.0"
