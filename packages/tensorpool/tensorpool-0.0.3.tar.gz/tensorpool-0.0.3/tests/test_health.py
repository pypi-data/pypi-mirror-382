"""
Tests for the TensorPool CLI health check functionality.

This module tests the health check function for various scenarios including:
- Missing API key (should fail)
- Invalid API key (should fail)
- Invalid package version (should fail)
- Valid scenarios
- Connection errors
"""

import pytest
import os
import unittest.mock
from typing import Tuple
from unittest.mock import patch, MagicMock
import requests

from tensorpool.helpers import health_check, get_version


class TestHealthCheck:
    """Test cases for the health check functionality."""

    def test_health_check_no_api_key_should_fail(self) -> None:
        """Test health check behavior when no API key is available - should fail."""
        # Temporarily remove API key from environment
        original_key = os.environ.get("TENSORPOOL_KEY")
        if original_key:
            del os.environ["TENSORPOOL_KEY"]

        try:
            with patch("requests.post") as mock_post:
                # Mock server response for missing API key
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_response.json.return_value = {
                    "message": "Invalid or missing API key"
                }
                mock_post.return_value = mock_response

                success, message = health_check()

                # Should fail when no API key is provided
                assert success is False
                assert isinstance(message, str)
                assert "API key" in message or "Invalid" in message

                # Verify the request was made with None key
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[1]["json"]["key"] is None

        finally:
            # Restore original key if it existed
            if original_key:
                os.environ["TENSORPOOL_KEY"] = original_key

    def test_health_check_invalid_api_key(self) -> None:
        """Test health check behavior with an invalid API key."""
        invalid_key = "invalid-key-12345"

        with patch.dict(os.environ, {"TENSORPOOL_KEY": invalid_key}):
            with patch("requests.post") as mock_post:
                # Mock server response for invalid API key
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_response.json.return_value = {"message": "Invalid API key"}
                mock_post.return_value = mock_response

                success, message = health_check()

                # Should fail with invalid API key
                assert success is False
                assert isinstance(message, str)
                assert "Invalid API key" in message

                # Verify the request was made with the invalid key
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[1]["json"]["key"] == invalid_key

    def test_health_check_invalid_package_version(self) -> None:
        """Test health check behavior with an invalid package version."""
        valid_key = "valid-key-12345"

        with patch.dict(os.environ, {"TENSORPOOL_KEY": valid_key}):
            with patch("requests.post") as mock_post:
                with patch("tensorpool.helpers.get_version") as mock_get_version:
                    # Mock an outdated version
                    mock_get_version.return_value = "0.1.0"

                    # Mock server response for invalid package version
                    mock_response = MagicMock()
                    mock_response.status_code = 400
                    mock_response.json.return_value = {
                        "message": "Package version 0.1.0 is not supported. Please upgrade."
                    }
                    mock_post.return_value = mock_response

                    success, message = health_check()

                    # Should fail with invalid package version
                    assert success is False
                    assert isinstance(message, str)
                    assert "version" in message.lower() and "upgrade" in message.lower()

                    # Verify the request was made with the outdated version
                    mock_post.assert_called_once()
                    call_args = mock_post.call_args
                    assert call_args[1]["json"]["package_version"] == "0.1.0"

    def test_health_check_valid_scenario(self) -> None:
        """Test health check behavior with valid API key and package version."""
        valid_key = "valid-key-12345"

        with patch.dict(os.environ, {"TENSORPOOL_KEY": valid_key}):
            with patch("requests.post") as mock_post:
                with patch("tensorpool.helpers.get_version") as mock_get_version:
                    # Mock a valid version
                    mock_get_version.return_value = "4.4.0"

                    # Mock successful server response
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"message": "Health check passed"}
                    mock_post.return_value = mock_response

                    success, message = health_check()

                    # Should succeed with valid credentials
                    assert success is True
                    assert isinstance(message, str)
                    assert "Health check passed" in message

    def test_health_check_connection_error(self) -> None:
        """Test health check behavior when connection to server fails."""
        valid_key = "valid-key-12345"

        with patch.dict(os.environ, {"TENSORPOOL_KEY": valid_key}):
            with patch("requests.post") as mock_post:
                # Mock connection error
                mock_post.side_effect = requests.exceptions.ConnectionError(
                    "Connection failed"
                )

                success, message = health_check()

                # Should fail with connection error
                assert success is False
                assert isinstance(message, str)
                assert "Cannot reach" in message and "TensorPool engine" in message

    def test_health_check_malformed_response(self) -> None:
        """Test health check behavior when server returns malformed JSON."""
        valid_key = "valid-key-12345"

        with patch.dict(os.environ, {"TENSORPOOL_KEY": valid_key}):
            with patch("requests.post") as mock_post:
                # Mock malformed JSON response
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
                    "Malformed JSON", "", 0
                )
                mock_post.return_value = mock_response

                success, message = health_check()

                # Should fail with malformed response
                assert success is False
                assert isinstance(message, str)
                assert "malformed response" in message.lower()

    def test_health_check_unexpected_error(self) -> None:
        """Test health check behavior when an unexpected error occurs."""
        valid_key = "valid-key-12345"

        with patch.dict(os.environ, {"TENSORPOOL_KEY": valid_key}):
            with patch("requests.post") as mock_post:
                # Mock unexpected exception
                mock_post.side_effect = Exception("Unexpected error")

                success, message = health_check()

                # Should fail with unexpected error
                assert success is False
                assert isinstance(message, str)
                assert "Unexpected error" in message

    def test_health_check_missing_api_key_env_and_file(self) -> None:
        """Test that health check properly fails when no API key is available anywhere."""
        # Ensure no API key in environment or .env file
        original_key = os.environ.get("TENSORPOOL_KEY")
        if original_key:
            del os.environ["TENSORPOOL_KEY"]

        # Mock that no .env file exists
        with patch("builtins.open", side_effect=FileNotFoundError()):
            with patch("requests.post") as mock_post:
                # Mock server response for missing API key
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_response.json.return_value = {"message": "API key required"}
                mock_post.return_value = mock_response

                try:
                    success, message = health_check()

                    # Must fail when no API key is available
                    assert success is False, (
                        "Health check should fail when no API key is provided"
                    )
                    assert isinstance(message, str)

                finally:
                    # Restore original key if it existed
                    if original_key:
                        os.environ["TENSORPOOL_KEY"] = original_key
