"""
Tests for the version module
"""


def test_version():
    """Test we get a valid version"""
    from lstcam_calib import __version__

    assert __version__ != "0.0.0"
