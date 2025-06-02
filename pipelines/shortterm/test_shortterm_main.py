"""Tests for main.py"""

from shortterm_main import hello_world


def test_hello_world():
    """Testing if the function returns the correct message."""
    assert hello_world() == "Hello World!"
