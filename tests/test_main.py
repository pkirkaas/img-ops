"""Tests for the main module."""

import sys
from io import StringIO
import pytest
from img_ops.main import start


def test_start_function(monkeypatch):
    """Test that the start function prints the expected message."""
    # Capture stdout
    captured_output = StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output)
    
    # Call the function
    result = start()
    
    # Check the result
    assert result == 0
    assert captured_output.getvalue().strip() == "In img_ops.main:start with Python & Poetry"


def test_start_function_error_handling(monkeypatch):
    """Test that the start function handles errors gracefully."""
    # Mock print to raise an exception
    def mock_print(*args, **kwargs):
        raise Exception("Test exception")
    
    # Capture stderr
    captured_error = StringIO()
    monkeypatch.setattr(sys, "stderr", captured_error)
    
    # Replace print with our mock
    monkeypatch.setattr("builtins.print", mock_print)
    
    # Call the function
    result = start()
    
    # Check the result
    assert result == 1
    assert "Error: Test exception" in captured_error.getvalue()