"""This module test the hello module."""

from figio.hello import hello


def test_hello():
    result = hello()
    assert result == "Hello World!"
