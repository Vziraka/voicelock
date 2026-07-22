"""Smoke test so the Gate suite collects and passes on a greenfield scaffold."""

from voicelock import __version__


def test_package_version() -> None:
    assert __version__ == "0.1.0"
