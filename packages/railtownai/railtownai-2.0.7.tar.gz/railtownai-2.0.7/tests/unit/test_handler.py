#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the handler module."""

from __future__ import annotations

import datetime
import json
import logging
import sys
import time
import uuid
from unittest.mock import Mock

import pytest

from railtownai.api_client import get_http_client, set_http_client
from railtownai.config import set_api_key
from railtownai.handler import RailtownHandler


class TestRailtownHandler:
    """Test the RailtownHandler class."""

    def setup_method(self):
        """Set up test environment."""
        # Set a valid API key for testing
        valid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501
        set_api_key(valid_key)

        # Store original HTTP client to restore later
        self.original_client = get_http_client()

    def teardown_method(self):
        """Clean up test environment."""
        # Restore original HTTP client
        set_http_client(self.original_client)

    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = RailtownHandler()

        assert handler._config is None
        assert isinstance(handler, logging.Handler)

    def test_handler_with_custom_level(self):
        """Test handler with custom log level."""
        handler = RailtownHandler(level=logging.WARNING)

        assert handler.level == logging.WARNING

    def test_emit_with_valid_config(self):
        """Test emit method with valid configuration."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://test-host.com"  # URL

        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "railtown-py(python)"

        # Verify payload structure
        payload = call_args[1]["json_data"]
        assert len(payload) == 1
        assert "Body" in payload[0]
        assert "UserProperties" in payload[0]

        # Verify user properties
        user_props = payload[0]["UserProperties"]
        assert user_props["AuthenticationCode"] == "test-secret"
        assert user_props["ClientVersion"].startswith("Python-")
        assert user_props["Encoding"] == "utf-8"
        assert user_props["ConnectionName"] == "test-host.com"

    def test_emit_with_exception_info(self):
        """Test emit method with exception information."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        try:
            raise ValueError("Test exception")
        except ValueError:
            # Create a log record with exception info
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Test error with exception",
                args=(),
                exc_info=sys.exc_info(),
            )

            handler.emit(record)

            # Verify the HTTP client was called
            assert mock_client.post.called

            # Get the call arguments
            call_args = mock_client.post.call_args
            payload = call_args[1]["json_data"]
            body_str = payload[0]["Body"]

            # Should contain exception information
            assert "ValueError" in body_str
            assert "Test exception" in body_str

    def test_emit_with_extra_data(self):
        """Test emit method with extra data in log record."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record with extra data
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test info message",
            args=(),
            exc_info=None,
        )
        record.extra_data = {"custom_key": "custom_value", "number": 42}

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]
        body_str = payload[0]["Body"]

        # Should contain extra data (snake_case keys converted to PascalCase)
        assert "CustomKey" in body_str
        assert "custom_value" in body_str
        assert "number" in body_str
        assert "42" in body_str

    def test_emit_without_config(self):
        """Test emit method when no configuration is available."""
        handler = RailtownHandler()

        # Clear the API key to simulate no configuration
        from railtownai.config import clear_config

        clear_config()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None,
        )

        # Should not raise an exception, just return silently
        handler.emit(record)

    def test_emit_with_invalid_config(self):
        """Test emit method with invalid configuration."""
        handler = RailtownHandler()

        # Set an invalid API key
        set_api_key("invalid_key")

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None,
        )

        # Should not raise an exception, just return silently
        handler.emit(record)

    def test_emit_with_different_log_levels(self):
        """Test emit method with different log levels."""
        handler = RailtownHandler()

        level_mappings = {
            logging.DEBUG: "debug",
            logging.INFO: "info",
            logging.WARNING: "warning",
            logging.ERROR: "error",
            logging.CRITICAL: "critical",
        }

        for log_level, expected_level in level_mappings.items():
            # Create a mock HTTP client
            mock_client = Mock()
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_client.post.return_value = mock_response

            # Set the mock client globally
            set_http_client(mock_client)

            record = logging.LogRecord(
                name="test_logger",
                level=log_level,
                pathname="test.py",
                lineno=10,
                msg=f"Test {expected_level} message",
                args=(),
                exc_info=None,
            )

            handler.emit(record)

            # Verify the HTTP client was called
            assert mock_client.post.called

            # Get the call arguments
            call_args = mock_client.post.call_args
            payload = call_args[1]["json_data"]
            body_str = payload[0]["Body"]

            # Should contain the correct level
            assert f'"Level": "{expected_level}"' in body_str

    def test_emit_with_unknown_log_level(self):
        """Test emit method with unknown log level."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record with an unknown level
        record = logging.LogRecord(
            name="test_logger",
            level=999,  # Unknown level
            pathname="test.py",
            lineno=10,
            msg="Test unknown level message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]
        body_str = payload[0]["Body"]

        # Should default to "info" level
        assert '"Level": "info"' in body_str

    def test_emit_with_http_error(self):
        """Test emit method when HTTP request fails."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None,
        )

        # Should not raise an exception, just handle the error silently
        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

    def test_emit_with_timeout(self):
        """Test emit method when HTTP request times out."""
        # Create a mock HTTP client that raises an exception
        mock_client = Mock()
        mock_client.post.side_effect = Exception("Timeout")

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None,
        )

        # Should not raise an exception, just handle the error silently
        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

    def test_emit_with_breadcrumbs_in_properties(self):
        """Test emit method with breadcrumbs included in Properties."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Add some breadcrumbs
        from railtownai import add_breadcrumb, clear_breadcrumbs

        clear_breadcrumbs()
        add_breadcrumb("Test breadcrumb 1", category="test")
        add_breadcrumb("Test breadcrumb 2", category="test", data={"key": "value"})

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message with breadcrumbs",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]
        body_str = payload[0]["Body"]

        # Should contain breadcrumbs in Properties, not as separate field
        assert "Breadcrumbs" in body_str
        assert "Properties" in body_str

    def test_emit_with_snake_case_to_pascal_case_transformation(self):
        """Test emit method transforms snake_case keys to PascalCase."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record with snake_case extra data
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message with snake_case keys",
            args=(),
            exc_info=None,
        )
        record.extra_data = {
            "run_id": "test-run-123",
            "session_id": "test-session-456",
            "other_field": "should_be_converted_to_pascal",
        }

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]
        body_str = payload[0]["Body"]

        # Should contain transformed PascalCase keys
        assert "ConductrAgentRunId" in body_str
        assert "ConductrAgentSessionId" in body_str
        assert "test-run-123" in body_str
        assert "test-session-456" in body_str

        # Should not contain original snake_case keys
        assert "run_id" not in body_str
        assert "session_id" not in body_str
        assert "other_field" not in body_str

        # Other fields should be converted to PascalCase
        assert "OtherField" in body_str

    def test_emit_with_mixed_case_keys(self):
        """Test emit method handles mixed case scenarios correctly."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record with mixed case scenarios
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message with mixed case keys",
            args=(),
            exc_info=None,
        )
        record.extra_data = {
            "run_id": "snake_case_value",
            "ConductrAgentRunId": "already_pascal_case",
            "session_id": "another_snake_case",
            "ConductrAgentSessionId": "another_pascal_case",
            "normal_field": "normal_value",
        }

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]
        body_str = payload[0]["Body"]

        # Should contain both transformed and original PascalCase keys
        assert "ConductrAgentRunId" in body_str
        assert "ConductrAgentSessionId" in body_str
        assert "NormalField" in body_str

        # Should contain the values (PascalCase takes precedence over snake_case)
        assert "already_pascal_case" in body_str  # ConductrAgentRunId value
        assert "another_pascal_case" in body_str  # ConductrAgentSessionId value
        assert "normal_value" in body_str

        # Snake case values should NOT be present since PascalCase takes precedence
        assert "snake_case_value" not in body_str
        assert "another_snake_case" not in body_str

    def test_emit_with_automatic_snake_case_conversion(self):
        """Test emit method automatically converts snake_case keys to PascalCase."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record with various snake_case keys
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message with automatic snake_case conversion",
            args=(),
            exc_info=None,
        )
        record.extra_data = {
            "user_name": "john_doe",
            "api_key": "secret_key",
            "http_status_code": 200,
            "request_id": "req-123",
            "normal_field": "normal_value",
        }

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]
        body_str = payload[0]["Body"]

        # Should contain transformed PascalCase keys
        assert "UserName" in body_str
        assert "ApiKey" in body_str
        assert "HttpStatusCode" in body_str
        assert "RequestId" in body_str
        assert "NormalField" in body_str

        # Should contain the values
        assert "john_doe" in body_str
        assert "secret_key" in body_str
        assert "200" in body_str
        assert "req-123" in body_str
        assert "normal_value" in body_str

        # Should not contain original snake_case keys
        assert "user_name" not in body_str
        assert "api_key" not in body_str
        assert "http_status_code" not in body_str
        assert "request_id" not in body_str
        assert "normal_field" not in body_str

    def test_transform_property_keys_method(self):
        """Test the _transform_property_keys method directly."""
        handler = RailtownHandler()

        # Test basic transformation with specific mappings
        properties = {
            "run_id": "test-run-123",
            "session_id": "test-session-456",
            "normal_field": "normal_value",
        }

        transformed = handler._transform_property_keys(properties)

        assert transformed["ConductrAgentRunId"] == "test-run-123"
        assert transformed["ConductrAgentSessionId"] == "test-session-456"
        assert transformed["NormalField"] == "normal_value"
        assert "run_id" not in transformed
        assert "session_id" not in transformed
        assert "normal_field" not in transformed

        # Test automatic snake_case conversion
        properties_with_snake_case = {
            "user_name": "john_doe",
            "api_key": "secret_key",
            "http_status_code": 200,
            "normal_field": "normal_value",
        }

        transformed_snake_case = handler._transform_property_keys(properties_with_snake_case)

        assert transformed_snake_case["UserName"] == "john_doe"
        assert transformed_snake_case["ApiKey"] == "secret_key"
        assert transformed_snake_case["HttpStatusCode"] == 200
        assert transformed_snake_case["NormalField"] == "normal_value"
        assert "user_name" not in transformed_snake_case
        assert "api_key" not in transformed_snake_case
        assert "http_status_code" not in transformed_snake_case
        assert "normal_field" not in transformed_snake_case

        # Test with no transformation needed
        properties_no_transform = {
            "normalField": "normal_value",
            "anotherField": "another_value",
        }

        transformed_no_transform = handler._transform_property_keys(properties_no_transform)

        assert transformed_no_transform == properties_no_transform

        # Test with empty properties
        empty_properties = {}
        transformed_empty = handler._transform_property_keys(empty_properties)

        assert transformed_empty == {}

        # Test with already PascalCase keys
        pascal_properties = {
            "ConductrAgentRunId": "already_pascal",
            "ConductrAgentSessionId": "already_pascal_too",
            "UserName": "already_pascal_user",
        }

        transformed_pascal = handler._transform_property_keys(pascal_properties)

        assert transformed_pascal == pascal_properties

        # Test mixed case scenarios
        mixed_properties = {
            "run_id": "specific_mapping_value",
            "user_name": "automatic_conversion_value",
            "normal_field": "unchanged_value",
        }

        transformed_mixed = handler._transform_property_keys(mixed_properties)

        assert transformed_mixed["ConductrAgentRunId"] == "specific_mapping_value"
        assert transformed_mixed["UserName"] == "automatic_conversion_value"
        assert transformed_mixed["NormalField"] == "unchanged_value"
        assert "run_id" not in transformed_mixed
        assert "user_name" not in transformed_mixed
        assert "normal_field" not in transformed_mixed

    def test_transform_property_keys_specific_mapping_precedence(self):
        """Test that specific mappings take precedence over automatic conversion."""
        handler = RailtownHandler()

        # Test that specific mappings are applied even when automatic conversion would also work
        properties = {
            "run_id": "specific_mapping_value",
            "session_id": "another_specific_value",
            "user_name": "automatic_conversion_value",
        }

        transformed = handler._transform_property_keys(properties)

        # Specific mappings should be used
        assert transformed["ConductrAgentRunId"] == "specific_mapping_value"
        assert transformed["ConductrAgentSessionId"] == "another_specific_value"

        # Automatic conversion should still work for other keys
        assert transformed["UserName"] == "automatic_conversion_value"

        # Original keys should not be present
        assert "run_id" not in transformed
        assert "session_id" not in transformed
        assert "user_name" not in transformed

    def test_get_platform_api_url_with_test_environment(self):
        """Test _get_platform_api_url method with test environment URL."""
        handler = RailtownHandler()

        # Set up a test configuration with 'tst' URL
        test_config = {"u": "tst-test-host.com", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

        # Mock the _get_config method to return our test config
        handler._get_config = lambda: test_config

        result = handler._get_platform_api_url()

        assert result == "https://testcndr.railtown.ai/api"

    def test_get_platform_api_url_with_overwatch_environment(self):
        """Test _get_platform_api_url method with overwatch environment URL."""
        handler = RailtownHandler()

        # Set up a test configuration with 'ovr' URL
        test_config = {"u": "ovr-test-host.com", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

        # Mock the _get_config method to return our test config
        handler._get_config = lambda: test_config

        result = handler._get_platform_api_url()

        assert result == "https://overwatch.railtown.ai/api"

    def test_get_platform_api_url_with_production_environment(self):
        """Test _get_platform_api_url method with production environment URL."""
        handler = RailtownHandler()

        # Set up a test configuration with production URL (no prefix)
        test_config = {
            "u": "prod-test-host.com",
            "o": "test-org",
            "p": "test-proj",
            "h": "test-secret",
            "e": "test-env",
        }

        # Mock the _get_config method to return our test config
        handler._get_config = lambda: test_config

        result = handler._get_platform_api_url()

        assert result == "https://cndr.railtown.ai/api"

    def test_get_platform_api_url_with_empty_url(self):
        """Test _get_platform_api_url method with empty URL."""
        handler = RailtownHandler()

        # Set up a test configuration with empty URL
        test_config = {"u": "", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

        # Mock the _get_config method to return our test config
        handler._get_config = lambda: test_config

        result = handler._get_platform_api_url()

        assert result == "https://cndr.railtown.ai/api"

    def test_get_platform_api_url_with_none_config(self):
        """Test _get_platform_api_url method when config is None."""
        handler = RailtownHandler()

        # Mock the _get_config method to return None
        handler._get_config = lambda: None

        result = handler._get_platform_api_url()

        assert result is None

    def test_get_platform_api_url_with_missing_url_key(self):
        """Test _get_platform_api_url method when URL key is missing from config."""
        handler = RailtownHandler()

        # Set up a test configuration without 'u' key
        test_config = {"o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

        # Mock the _get_config method to return our test config
        handler._get_config = lambda: test_config

        # This should raise a KeyError when trying to access config["u"]
        with pytest.raises(KeyError):
            handler._get_platform_api_url()

    def test_get_platform_api_url_with_various_test_prefixes(self):
        """Test _get_platform_api_url method with various test environment prefixes."""
        handler = RailtownHandler()

        test_cases = [
            ("tst", "https://testcndr.railtown.ai/api"),
            ("tst-", "https://testcndr.railtown.ai/api"),
            ("tst_", "https://testcndr.railtown.ai/api"),
            ("tst123", "https://testcndr.railtown.ai/api"),
            ("tst.example.com", "https://testcndr.railtown.ai/api"),
        ]

        for url_prefix, expected_url in test_cases:
            test_config = {"u": url_prefix, "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

            # Mock the _get_config method to return our test config
            handler._get_config = lambda: test_config  # noqa: B023

            result = handler._get_platform_api_url()
            assert result == expected_url, f"Failed for URL prefix: {url_prefix}"

    def test_get_platform_api_url_with_various_overwatch_prefixes(self):
        """Test _get_platform_api_url method with various overwatch environment prefixes."""
        handler = RailtownHandler()

        test_cases = [
            ("ovr", "https://overwatch.railtown.ai/api"),
            ("ovr-", "https://overwatch.railtown.ai/api"),
            ("ovr_", "https://overwatch.railtown.ai/api"),
            ("ovr123", "https://overwatch.railtown.ai/api"),
            ("ovr.example.com", "https://overwatch.railtown.ai/api"),
        ]

        for url_prefix, expected_url in test_cases:
            test_config = {"u": url_prefix, "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

            # Mock the _get_config method to return our test config
            handler._get_config = lambda: test_config  # noqa: B023

            result = handler._get_platform_api_url()
            assert result == expected_url, f"Failed for URL prefix: {url_prefix}"

    def test_get_platform_api_url_with_production_prefixes(self):
        """Test _get_platform_api_url method with various production environment prefixes."""
        handler = RailtownHandler()

        test_cases = [
            ("prod", "https://cndr.railtown.ai/api"),
            ("prod-", "https://cndr.railtown.ai/api"),
            ("prod_", "https://cndr.railtown.ai/api"),
            ("prod123", "https://cndr.railtown.ai/api"),
            ("prod.example.com", "https://cndr.railtown.ai/api"),
            ("", "https://cndr.railtown.ai/api"),
            ("example.com", "https://cndr.railtown.ai/api"),
            ("api.railtown.ai", "https://cndr.railtown.ai/api"),
        ]

        for url_prefix, expected_url in test_cases:
            test_config = {"u": url_prefix, "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

            # Mock the _get_config method to return our test config
            handler._get_config = lambda: test_config  # noqa: B023

            result = handler._get_platform_api_url()
            assert result == expected_url, f"Failed for URL prefix: {url_prefix}"

    def test_get_platform_api_url_case_sensitivity(self):
        """Test _get_platform_api_url method is case sensitive for environment prefixes."""
        handler = RailtownHandler()

        test_cases = [
            ("TST", "https://cndr.railtown.ai/api"),  # Should default to production
            ("OVR", "https://cndr.railtown.ai/api"),  # Should default to production
            ("tSt", "https://cndr.railtown.ai/api"),  # Should default to production
            ("oVr", "https://cndr.railtown.ai/api"),  # Should default to production
        ]

        for url_prefix, expected_url in test_cases:
            test_config = {"u": url_prefix, "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

            # Mock the _get_config method to return our test config
            handler._get_config = lambda: test_config  # noqa: B023

            result = handler._get_platform_api_url()
            assert result == expected_url, f"Failed for URL prefix: {url_prefix}"

    def test_get_conductr_presigned_sas_url_success(self):
        """Test _get_conductr_presigned_sas_url method with successful response."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = "https://test-sas-url.com"
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Set up test configuration
        test_config = {"u": "tst-test-host.com", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

        # Mock the _get_config method
        handler._get_config = lambda: test_config

        # Mock the _get_platform_api_url method
        handler._get_platform_api_url = lambda: "https://testcndr.railtown.ai/api"

        from unittest.mock import patch

        with patch("railtownai.handler.get_api_key", return_value="test-api-key"):
            result = handler._get_conductr_presigned_sas_url()

            assert result == "https://test-sas-url.com"
            assert mock_client.post.called

            # Verify the request was made correctly
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://testcndr.railtown.ai/api/observe/exchange"  # URL

            # Verify headers
            headers = call_args[1]["headers"]
            assert headers["Content-Type"] == "application/json"
            assert headers["User-Agent"] == "railtown-py(python)"
            assert headers["Authorization"] == "Bearer test-secret"

            # Verify the request body
            assert call_args[1]["data"] == '"test-api-key"'

    def test_get_conductr_presigned_sas_url_with_none_config(self):
        """Test _get_conductr_presigned_sas_url method when config is None."""
        handler = RailtownHandler()

        # Mock the _get_config method to return None
        handler._get_config = lambda: None

        result = handler._get_conductr_presigned_sas_url()

        assert result is None

    def test_get_conductr_presigned_sas_url_with_http_error(self):
        """Test _get_conductr_presigned_sas_url method when HTTP request fails."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Set up test configuration
        test_config = {"u": "tst-test-host.com", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

        # Mock the _get_config method
        handler._get_config = lambda: test_config

        # Mock the _get_platform_api_url method
        handler._get_platform_api_url = lambda: "https://testcndr.railtown.ai/api"

        result = handler._get_conductr_presigned_sas_url()

        assert result is None

    def test_get_conductr_presigned_sas_url_with_exception(self):
        """Test _get_conductr_presigned_sas_url method when an exception occurs."""
        # Create a mock HTTP client that raises an exception
        mock_client = Mock()
        mock_client.post.side_effect = Exception("Network error")

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Set up test configuration
        test_config = {"u": "tst-test-host.com", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}

        # Mock the _get_config method
        handler._get_config = lambda: test_config

        # Mock the _get_platform_api_url method
        handler._get_platform_api_url = lambda: "https://testcndr.railtown.ai/api"

        result = handler._get_conductr_presigned_sas_url()

        assert result is None

    def test_upload_agent_run_success(self):
        """Test upload_agent_run method with successful upload."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is True
        assert mock_client.put.called

        # Verify the request was made correctly
        call_args = mock_client.put.call_args
        assert call_args[0][0] == "https://test-sas-url.com"  # URL

        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "text/plain; charset=utf-8"
        assert headers["x-ms-version"] == "2022-11-02"
        assert headers["x-ms-blob-type"] == "BlockBlob"

        # Verify the uploaded data matches our test data
        uploaded_data = json.loads(call_args[1]["data"].decode("utf-8"))
        assert uploaded_data["name"] == "test agent run"
        assert len(uploaded_data["nodes"]) == 1
        assert len(uploaded_data["steps"]) == 1
        assert len(uploaded_data["edges"]) == 1

    def test_upload_agent_run_with_no_sas_url(self):
        """Test upload_agent_run method when no SAS URL is available."""
        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method to return None
        handler._get_conductr_presigned_sas_url = lambda: None

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_http_error(self):
        """Test upload_agent_run method when HTTP request fails."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "key": "value",
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_exception(self):
        """Test upload_agent_run method when an exception occurs."""
        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method to raise an exception
        handler._get_conductr_presigned_sas_url = lambda: Exception("Network error")

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "key": "value",
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_complex_data(self):
        """Test upload_agent_run method with complex JSON data."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "string": "test",
            "number": 42,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"},
            "unicode": "café",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is True
        assert mock_client.put.called

        # Verify the JSON was serialized correctly
        call_args = mock_client.put.call_args
        uploaded_data = json.loads(call_args[1]["data"].decode("utf-8"))
        assert uploaded_data["string"] == "test"
        assert uploaded_data["number"] == 42
        assert uploaded_data["boolean"] is True
        assert uploaded_data["null"] is None
        assert uploaded_data["array"] == [1, 2, 3]
        assert uploaded_data["object"] == {"nested": "value"}
        assert uploaded_data["unicode"] == "café"
        assert len(uploaded_data["nodes"]) == 1
        assert len(uploaded_data["steps"]) == 1
        assert len(uploaded_data["edges"]) == 1

    def test_upload_agent_run_with_valid_agent_data(self):
        """Test upload_agent_run method with valid agent run data (nodes, steps, edges)."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is True
        assert mock_client.put.called

        # Verify the JSON was serialized correctly
        call_args = mock_client.put.call_args
        uploaded_data = call_args[1]["data"].decode("utf-8")
        assert "nodes" in uploaded_data
        assert "steps" in uploaded_data
        assert "edges" in uploaded_data

    def test_upload_agent_run_with_empty_nodes(self):
        """Test upload_agent_run method with empty nodes array."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_empty_steps(self):
        """Test upload_agent_run method with empty steps array."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_empty_edges(self):
        """Test upload_agent_run method with empty edges array."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_missing_nodes(self):
        """Test upload_agent_run method with missing nodes field."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_missing_steps(self):
        """Test upload_agent_run method with missing steps field."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_missing_edges(self):
        """Test upload_agent_run method with missing edges field."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_all_empty_arrays(self):
        """Test upload_agent_run method with all required arrays empty."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [],
            "steps": [],
            "edges": [],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False

    def test_upload_agent_run_with_partial_empty_arrays(self):
        """Test upload_agent_run method with some arrays empty."""
        handler = RailtownHandler()

        # Test with nodes and steps empty
        test_data_1 = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [],
            "steps": [],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }
        result = handler.upload_agent_run(test_data_1)
        assert result is False

        # Test with nodes and edges empty
        test_data_2 = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [],
        }
        result = handler.upload_agent_run(test_data_2)
        assert result is False

        # Test with steps and edges empty
        test_data_3 = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [],
            "edges": [],
        }
        result = handler.upload_agent_run(test_data_3)
        assert result is False

    def test_upload_agent_run_with_non_list_values(self):
        """Test upload_agent_run method with non-list values for required fields."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        # Test with nodes as string (should succeed since len("not a list") > 0)
        test_data_1 = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": "not a list",
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }
        result = handler.upload_agent_run(test_data_1)
        assert result is True  # Current implementation doesn't validate types

        # Test with steps as dict (should succeed since len({"not": "a list"}) > 0)
        test_data_2 = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": {"not": "a list"},
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }
        result = handler.upload_agent_run(test_data_2)
        assert result is True  # Current implementation doesn't validate types

        # Test with edges as number (should succeed since len(42) > 0 is False, but we need to check the actual behavior)  # noqa: E501
        test_data_3 = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": 42,
        }
        result = handler.upload_agent_run(test_data_3)
        assert result is False  # This should fail because len(42) raises TypeError

        # Verify that the HTTP client was called for the successful cases
        assert mock_client.put.called

    def test_upload_agent_run_with_string_payload_single_object(self):
        """Test upload_agent_run method with string payload containing a single JSON object."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        # Create a string payload with a single JSON object
        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }
        string_payload = json.dumps(test_data)

        result = handler.upload_agent_run(string_payload)

        assert result is True
        assert mock_client.put.called

        # Verify the request was made correctly
        call_args = mock_client.put.call_args
        assert call_args[0][0] == "https://test-sas-url.com"  # URL

        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "text/plain; charset=utf-8"
        assert headers["x-ms-version"] == "2022-11-02"
        assert headers["x-ms-blob-type"] == "BlockBlob"

        # Verify the uploaded data matches our test data
        uploaded_data = json.loads(call_args[1]["data"].decode("utf-8"))
        assert uploaded_data["name"] == "test agent run"
        assert len(uploaded_data["nodes"]) == 1
        assert len(uploaded_data["steps"]) == 1
        assert len(uploaded_data["edges"]) == 1

    def test_upload_agent_run_with_string_payload_array(self):
        """Test upload_agent_run method with string payload containing an array of JSON objects."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        # Create a string payload with an array of JSON objects
        test_data = [
            {
                "name": "test agent run 1",
                "session_id": "test-session-123",
                "run_id": "test-run-456",
                "nodes": [{"identifier": "node1", "node_type": "planner"}],
                "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
                "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
            },
            {
                "name": "test agent run 2",
                "session_id": "test-session-456",
                "run_id": "test-run-789",
                "nodes": [{"identifier": "node2", "node_type": "executor"}],
                "steps": [{"step": 1, "time": 1234567891, "identifier": "step2"}],
                "edges": [{"source": "node2", "target": "node3", "identifier": "edge2"}],
            },
        ]
        string_payload = json.dumps(test_data)

        result = handler.upload_agent_run(string_payload)

        assert result is True
        # Should be called twice (once for each payload in the array)
        assert mock_client.put.call_count == 2

        # Verify both requests were made correctly
        call_args_list = mock_client.put.call_args_list

        # First call
        first_call = call_args_list[0]
        assert first_call[0][0] == "https://test-sas-url.com"
        first_uploaded_data = json.loads(first_call[1]["data"].decode("utf-8"))
        assert first_uploaded_data["name"] == "test agent run 1"
        # Verify session_id is preserved (not regenerated)
        assert first_uploaded_data["session_id"] == "test-session-123"

        # Second call
        second_call = call_args_list[1]
        assert second_call[0][0] == "https://test-sas-url.com"
        second_uploaded_data = json.loads(second_call[1]["data"].decode("utf-8"))
        assert second_uploaded_data["name"] == "test agent run 2"
        # Verify session_id is preserved (not regenerated)
        assert second_uploaded_data["session_id"] == "test-session-456"

    def test_upload_agent_run_with_invalid_json_string(self):
        """Test upload_agent_run method with invalid JSON string."""
        handler = RailtownHandler()

        # Test with invalid JSON string
        invalid_json = "{ invalid json }"

        result = handler.upload_agent_run(invalid_json)

        assert result is False

    def test_upload_agent_run_with_empty_string(self):
        """Test upload_agent_run method with empty string."""
        handler = RailtownHandler()

        # Test with empty string
        empty_string = ""

        result = handler.upload_agent_run(empty_string)

        assert result is False

    def test_upload_agent_run_with_string_containing_null(self):
        """Test upload_agent_run method with string containing null."""
        handler = RailtownHandler()

        # Test with string containing null
        null_string = "null"

        result = handler.upload_agent_run(null_string)

        assert result is False

    def test_upload_agent_run_with_string_containing_empty_array(self):
        """Test upload_agent_run method with string containing empty array."""
        handler = RailtownHandler()

        # Test with string containing empty array
        empty_array_string = "[]"

        result = handler.upload_agent_run(empty_array_string)

        assert result is True  # Empty array should return True (no payloads to upload)

    def test_upload_agent_run_with_string_containing_mixed_valid_invalid_payloads(self):
        """Test upload_agent_run method with string containing mix of valid and invalid payloads."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        # Create a string payload with mix of valid and invalid payloads
        test_data = [
            {
                "name": "valid payload",
                "session_id": "test-session-123",
                "run_id": "test-run-456",
                "nodes": [{"identifier": "node1", "node_type": "planner"}],
                "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
                "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
            },
            {
                "name": "invalid payload - missing required fields",
                "session_id": "test-session-456",
                "run_id": "test-run-789",
                # Missing nodes, steps, edges
            },
        ]
        string_payload = json.dumps(test_data)

        result = handler.upload_agent_run(string_payload)

        # Should fail because one payload is invalid
        assert result is False
        # Should be called once (for the valid payload)
        assert mock_client.put.call_count == 1

        # Verify the valid payload was uploaded
        call_args = mock_client.put.call_args
        uploaded_data = json.loads(call_args[1]["data"].decode("utf-8"))
        assert uploaded_data["name"] == "valid payload"

    def test_emit_payload_serialization_format(self):
        """Test that the emit method produces correctly serialized JSON in Body field."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record with extra data
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None,
        )
        record.extra_data = {"user_id": "12345", "action": "login"}

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]

        # Verify payload structure
        assert len(payload) == 1
        assert "Body" in payload[0]
        assert "UserProperties" in payload[0]

        # Get the Body field
        body_str = payload[0]["Body"]

        # Verify Body is a string (not an object)
        assert isinstance(body_str, str)

        # Verify it's valid JSON
        body_data = json.loads(body_str)

        # Verify the JSON structure matches RailtownPayload model
        assert "Message" in body_data
        assert "Level" in body_data
        assert "OrganizationId" in body_data
        assert "ProjectId" in body_data
        assert "EnvironmentId" in body_data
        assert "Runtime" in body_data
        assert "Exception" in body_data
        assert "TimeStamp" in body_data
        assert "Properties" in body_data

        # Verify specific values
        assert body_data["Message"] == "Test error message"
        assert body_data["Level"] == "error"
        assert body_data["Runtime"] == "python-traceback"
        assert body_data["Properties"]["UserId"] == "12345"  # snake_case converted to PascalCase
        assert body_data["Properties"]["action"] == "login"  # non-snake_case keys are kept as-is

        # Verify the JSON string format matches API requirements
        # Should be a valid JSON string that can be parsed
        assert body_str.startswith("{")
        assert body_str.endswith("}")

        # Verify it can be parsed as JSON (as the API would receive it)
        parsed_json = json.loads(body_str)
        assert parsed_json["Message"] == "Test error message"

    def test_emit_payload_serialization_approaches_equivalence(self):
        """Test that the current serialization approach produces equivalent results to alternatives."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Clear any existing breadcrumbs to ensure clean test
        from railtownai import clear_breadcrumbs

        clear_breadcrumbs()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test info message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        payload = call_args[1]["json_data"]
        body_str = payload[0]["Body"]

        # Parse the current approach result
        current_result = json.loads(body_str)

        # Create the same RailtownPayload manually to test alternative approaches
        from railtownai.config import get_config
        from railtownai.models import RailtownPayload

        config = get_config()
        manual_payload = RailtownPayload(
            Message=record.getMessage(),
            Level="info",
            Exception="",
            OrganizationId=config["o"],
            ProjectId=config["p"],
            EnvironmentId=config["e"],
            Runtime="python-traceback",
            TimeStamp=datetime.datetime.fromtimestamp(record.created).isoformat(),  # Convert to ISO string
            Properties={},
        )

        # Test alternative approach: model_dump_json()
        alternative_json = manual_payload.model_dump_json()
        alternative_result = json.loads(alternative_json)

        # Both approaches should produce equivalent data structures
        # (timestamps might differ, so we'll compare individual fields)
        assert current_result["Message"] == alternative_result["Message"]
        assert current_result["Level"] == alternative_result["Level"]
        assert current_result["OrganizationId"] == alternative_result["OrganizationId"]
        assert current_result["ProjectId"] == alternative_result["ProjectId"]
        assert current_result["EnvironmentId"] == alternative_result["EnvironmentId"]
        assert current_result["Runtime"] == alternative_result["Runtime"]
        assert current_result["Exception"] == alternative_result["Exception"]
        assert current_result["Properties"] == alternative_result["Properties"]

        # Both should be valid JSON strings
        assert isinstance(body_str, str)
        assert isinstance(alternative_json, str)

        # Both should be parseable
        json.loads(body_str)
        json.loads(alternative_json)

    # ===== SESSION FORMAT TESTS =====

    def test_is_session_format_true(self):
        """Test _is_session_format detects session format correctly."""
        handler = RailtownHandler()

        # Valid session format
        session_data = {
            "session_id": "test-session-id",
            "name": "Test Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [{"run_id": "run1", "name": "Run 1"}],
        }
        assert handler._is_session_format(session_data) is True

    def test_is_session_format_false(self):
        """Test _is_session_format rejects non-session format."""
        handler = RailtownHandler()

        # Old format (no runs field)
        old_format = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [],
            "steps": [],
            "edges": [],
        }
        assert handler._is_session_format(old_format) is False

        # Invalid runs field
        invalid_runs = {"runs": "not_a_list"}
        assert handler._is_session_format(invalid_runs) is False

    def test_validate_session_format_valid(self):
        """Test _validate_session_format with valid session data."""
        handler = RailtownHandler()

        valid_session = {
            "session_id": "test-session-id",
            "name": "Test Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "run_id": "run1",
                    "name": "Run 1",
                    "start_time": 1234567890,
                    "end_time": 1234567891,
                    "status": "Completed",
                    "nodes": [{"identifier": "node1"}],
                    "steps": [{"step": 1}],
                    "edges": [{"source": "node1", "target": "node2"}],
                }
            ],
        }

        is_valid, errors = handler._validate_session_format(valid_session)
        assert is_valid is True
        assert errors == []

    def test_validate_session_format_missing_fields(self):
        """Test _validate_session_format with missing required fields."""
        handler = RailtownHandler()

        # Missing session fields
        invalid_session = {
            "name": "Test Session",  # missing session_id, start_time, end_time, runs
            "start_time": 1234567890,
            "end_time": 1234567891,
        }

        is_valid, errors = handler._validate_session_format(invalid_session)
        assert is_valid is False
        assert "session_id" in " ".join(errors)
        assert "runs" in " ".join(errors)

    def test_validate_session_format_invalid_runs(self):
        """Test _validate_session_format with invalid runs structure."""
        handler = RailtownHandler()

        # Empty runs array
        invalid_session = {
            "session_id": "test-session-id",
            "name": "Test Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [],  # empty array
        }

        is_valid, errors = handler._validate_session_format(invalid_session)
        assert is_valid is False
        assert "non-empty list" in " ".join(errors)

    def test_validate_session_format_missing_run_fields(self):
        """Test _validate_session_format with missing run fields."""
        handler = RailtownHandler()

        # Test missing required run_id field
        invalid_session = {
            "session_id": "test-session-id",
            "name": "Test Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "name": "Run 1",  # missing run_id (required)
                    "nodes": [],
                    "steps": [],
                    "edges": [],
                }
            ],
        }

        is_valid, errors = handler._validate_session_format(invalid_session)
        assert is_valid is False
        assert any("run_id" in error for error in errors)

        # Test missing required name field
        invalid_session2 = {
            "session_id": "test-session-id",
            "name": "Test Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "run_id": "run-123",  # missing name (required)
                    "nodes": [],
                    "steps": [],
                    "edges": [],
                }
            ],
        }

        is_valid, errors = handler._validate_session_format(invalid_session2)
        assert is_valid is False
        assert any("name" in error for error in errors)

        # Test that start_time, end_time, status are now optional
        valid_session = {
            "session_id": "test-session-id",
            "name": "Test Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "run_id": "run-123",
                    "name": "Run 1",
                    # start_time, end_time, status are now optional
                    "nodes": [],
                    "steps": [],
                    "edges": [],
                }
            ],
        }

        is_valid, errors = handler._validate_session_format(valid_session)
        assert is_valid is True
        assert errors == []

    def test_validate_session_format_with_session_name(self):
        """Test _validate_session_format with session_name field (railtracks format)."""
        handler = RailtownHandler()

        # Test with session_name field instead of name
        valid_session = {
            "session_id": "test-session-id",
            "session_name": "Test Session",  # railtracks uses session_name
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "run_id": "run-123",
                    "name": "Run 1",
                    "nodes": [],
                    "steps": [],
                    "edges": [],
                }
            ],
        }

        is_valid, errors = handler._validate_session_format(valid_session)
        assert is_valid is True
        assert errors == []

        # Test missing both name and session_name
        invalid_session = {
            "session_id": "test-session-id",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "run_id": "run-123",
                    "name": "Run 1",
                    "nodes": [],
                    "steps": [],
                    "edges": [],
                }
            ],
        }

        is_valid, errors = handler._validate_session_format(invalid_session)
        assert is_valid is False
        assert any("missing 'name' or 'session_name' field" in error for error in errors)

    def test_enrich_run_with_session_data(self):
        """Test _enrich_run_with_session_data correctly enriches run data."""
        handler = RailtownHandler()

        session_data = {
            "session_id": "session-guid-123",
            "name": "Ticket Triage Agent",
            "start_time": 39929293,
            "end_time": 494949,
            "runs": [],
        }

        run_data = {
            "run_id": "run-guid-456",
            "name": "Initial Analysis Run",
            "start_time": 39929294,
            "end_time": 494950,
            "status": "Completed",
            "nodes": [{"identifier": "node1", "node_type": "analyzer"}],
            "steps": [{"step": 1, "time": 39929295, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        enriched_data = handler._enrich_run_with_session_data(session_data, run_data)

        # Check session metadata is attached - session_id should be preserved from session data
        assert enriched_data["session_id"] == "session-guid-123"  # Should preserve session_id
        assert enriched_data["session_name"] == "Ticket Triage Agent"
        assert enriched_data["session_start_time"] == 39929293
        assert enriched_data["session_end_time"] == 494949

        # Check run fields are renamed
        assert enriched_data["run_id"] == "run-guid-456"
        assert enriched_data["run_name"] == "Initial Analysis Run"
        assert enriched_data["run_start_time"] == 39929294
        assert enriched_data["run_end_time"] == 494950
        assert enriched_data["run_status"] == "Completed"

        # Check original arrays are preserved
        assert enriched_data["nodes"] == run_data["nodes"]
        assert enriched_data["steps"] == run_data["steps"]
        assert enriched_data["edges"] == run_data["edges"]

    def test_enrich_run_with_session_data_session_name(self):
        """Test _enrich_run_with_session_data with session_name field (railtracks format)."""
        handler = RailtownHandler()

        session_data = {
            "session_id": "session-guid-123",
            "session_name": "Ticket Triage Agent",  # railtracks uses session_name
            "start_time": 39929293,
            "end_time": 494949,
            "runs": [],
        }

        run_data = {
            "run_id": "run-guid-456",
            "name": "Initial Analysis Run",
            # Missing optional fields: start_time, end_time, status
            "nodes": [{"identifier": "node1", "node_type": "analyzer"}],
            "steps": [{"step": 1, "time": 39929295, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        enriched_data = handler._enrich_run_with_session_data(session_data, run_data)

        # Check session metadata is attached - session_id should be preserved from session data
        assert enriched_data["session_id"] == "session-guid-123"  # Should preserve session_id
        assert enriched_data["session_name"] == "Ticket Triage Agent"
        assert enriched_data["session_start_time"] == 39929293
        assert enriched_data["session_end_time"] == 494949

        # Check run fields are renamed with defaults for missing optional fields
        assert enriched_data["run_id"] == "run-guid-456"
        assert enriched_data["run_name"] == "Initial Analysis Run"

        # Check that missing start_time and end_time get current timestamp
        current_time = time.time()
        assert enriched_data["run_start_time"] is not None
        assert enriched_data["run_end_time"] is not None
        assert abs(enriched_data["run_start_time"] - current_time) < 1.0  # Within 1 second
        assert abs(enriched_data["run_end_time"] - current_time) < 1.0  # Within 1 second
        assert enriched_data["run_status"] == "Unknown"  # Default for missing field

        # Check original arrays are preserved
        assert enriched_data["nodes"] == run_data["nodes"]
        assert enriched_data["steps"] == run_data["steps"]
        assert enriched_data["edges"] == run_data["edges"]

    def test_enrich_run_with_session_data_null_session_name_fallback(self):
        """Test _enrich_run_with_session_data with null session_name falls back to session_id."""
        handler = RailtownHandler()

        session_data = {
            "session_id": "session-guid-123",
            "session_name": None,  # null session_name
            "start_time": 39929293,
            "end_time": 494949,
            "runs": [],
        }

        run_data = {
            "run_id": "run-guid-456",
            "name": "Initial Analysis Run",
            "nodes": [{"identifier": "node1", "node_type": "analyzer"}],
            "steps": [{"step": 1, "time": 39929295, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        enriched_data = handler._enrich_run_with_session_data(session_data, run_data)

        # Check that session_name falls back to session_id when null
        assert enriched_data["session_name"] == "session-guid-123"
        assert enriched_data["session_start_time"] == 39929293
        assert enriched_data["session_end_time"] == 494949

        # Test with empty string session_name
        session_data_empty = {
            "session_id": "session-guid-456",
            "session_name": "",  # empty string session_name
            "start_time": 39929293,
            "end_time": 494949,
            "runs": [],
        }

        enriched_data_empty = handler._enrich_run_with_session_data(session_data_empty, run_data)
        assert enriched_data_empty["session_name"] == "session-guid-456"

        # Test with missing session_name entirely
        session_data_missing = {
            "session_id": "session-guid-789",
            "start_time": 39929293,
            "end_time": 494949,
            "runs": [],
        }

        enriched_data_missing = handler._enrich_run_with_session_data(session_data_missing, run_data)
        assert enriched_data_missing["session_name"] == "session-guid-789"

    def test_upload_agent_run_session_format_success(self):
        """Test upload_agent_run with valid session format."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        session_data = {
            "session_id": "session-guid-123",
            "name": "Test Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "run_id": "run-guid-456",
                    "name": "Test Run",
                    "start_time": 1234567892,
                    "end_time": 1234567893,
                    "status": "Completed",
                    "nodes": [{"identifier": "node1", "node_type": "test"}],
                    "steps": [{"step": 1, "time": 1234567894, "identifier": "step1"}],
                    "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
                }
            ],
        }

        result = handler.upload_agent_run(session_data)

        assert result is True
        # Should have made 1 HTTP request (for 1 run)
        assert mock_client.put.call_count == 1

        # Verify the uploaded data contains enriched fields
        call_args = mock_client.put.call_args
        uploaded_data = call_args[1]["data"].decode("utf-8")
        uploaded_json = json.loads(uploaded_data)

        # Check that enriched data contains both session and run metadata
        assert uploaded_json["session_id"] == "session-guid-123"  # Should preserve session_id
        assert uploaded_json["session_name"] == "Test Session"
        assert uploaded_json["run_id"] == "run-guid-456"
        assert uploaded_json["run_name"] == "Test Run"
        assert uploaded_json["run_status"] == "Completed"

    def test_upload_agent_run_session_format_multiple_runs(self):
        """Test upload_agent_run with session format containing multiple runs."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        session_data = {
            "session_id": "session-guid-123",
            "name": "Multi-Run Session",
            "start_time": 1234567890,
            "end_time": 1234567891,
            "runs": [
                {
                    "run_id": "run-1",
                    "name": "First Run",
                    "start_time": 1234567892,
                    "end_time": 1234567893,
                    "status": "Completed",
                    "nodes": [{"identifier": "node1"}],
                    "steps": [{"step": 1}],
                    "edges": [{"source": "node1", "target": "node2"}],
                },
                {
                    "run_id": "run-2",
                    "name": "Second Run",
                    "start_time": 1234567894,
                    "end_time": 1234567895,
                    "status": "Failed",
                    "nodes": [{"identifier": "node3"}],
                    "steps": [{"step": 2}],
                    "edges": [{"source": "node3", "target": "node4"}],
                },
            ],
        }

        result = handler.upload_agent_run(session_data)

        assert result is True
        # Should have made 2 HTTP requests (for 2 runs)
        assert mock_client.put.call_count == 2

    def test_upload_agent_run_session_format_validation_failure(self):
        """Test upload_agent_run with invalid session format."""
        handler = RailtownHandler()

        # Invalid session data (missing required fields)
        invalid_session = {
            "name": "Invalid Session",  # missing session_id, start_time, end_time, runs
        }

        result = handler.upload_agent_run(invalid_session)

        # Should fail validation and return False
        assert result is False

    def test_upload_agent_run_mixed_formats(self):
        """Test upload_agent_run with mix of session and old formats."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        # Mix of session format and old format
        mixed_payloads = [
            # Session format
            {
                "session_id": "session-1",
                "name": "Session One",
                "start_time": 1234567890,
                "end_time": 1234567891,
                "runs": [
                    {
                        "run_id": "run-1",
                        "name": "Run One",
                        "start_time": 1234567892,
                        "end_time": 1234567893,
                        "status": "Completed",
                        "nodes": [{"identifier": "node1"}],
                        "steps": [{"step": 1}],
                        "edges": [{"source": "node1", "target": "node2"}],
                    }
                ],
            },
            # Old format
            {
                "name": "Old Format Run",
                "session_id": "old-session",
                "run_id": "old-run",
                "nodes": [{"identifier": "node3"}],
                "steps": [{"step": 1}],
                "edges": [{"source": "node3", "target": "node4"}],
            },
        ]

        result = handler.upload_agent_run(mixed_payloads)

        assert result is True
        # Should have made 2 HTTP requests (1 for session run, 1 for old format)
        assert mock_client.put.call_count == 2

    def test_upload_single_agent_run_enriched_format(self):
        """Test _upload_single_agent_run handles enriched format correctly."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        # Enriched format data (as would be created by session processing)
        enriched_data = {
            "session_id": "session-guid-123",
            "session_name": "Test Session",
            "session_start_time": 1234567890,
            "session_end_time": 1234567891,
            "run_id": "run-guid-456",
            "run_name": "Test Run",
            "run_start_time": 1234567892,
            "run_end_time": 1234567893,
            "run_status": "Completed",
            "nodes": [{"identifier": "node1"}],
            "steps": [{"step": 1}],
            "edges": [{"source": "node1", "target": "node2"}],
        }

        result = handler._upload_single_agent_run(enriched_data)

        assert result is True
        assert mock_client.put.called

        # Verify the data was uploaded as-is
        call_args = mock_client.put.call_args
        uploaded_data = call_args[1]["data"].decode("utf-8")
        uploaded_json = json.loads(uploaded_data)

        # For enriched format, session_id should be preserved
        assert uploaded_json["session_id"] == "session-guid-123"  # Should preserve session_id
        assert uploaded_json["run_id"] == "run-guid-456"

    def test_enrich_old_format_data(self):
        """Test _enrich_old_format_data correctly enriches old format data."""
        handler = RailtownHandler()

        old_format_data = {
            "name": "my_agent_run",
            "session_id": "session-123",
            "run_id": "run-456",
            "nodes": [{"identifier": "node1"}],
            "steps": [{"step": 1}],
            "edges": [{"source": "node1", "target": "node2"}],
        }

        enriched_data = handler._enrich_old_format_data(old_format_data)

        # Check that original data is preserved (except session_id which gets regenerated)
        assert enriched_data["name"] == "my_agent_run"
        assert enriched_data["run_id"] == "run-456"  # Original run_id preserved
        assert enriched_data["nodes"] == [{"identifier": "node1"}]
        assert enriched_data["steps"] == [{"step": 1}]
        assert enriched_data["edges"] == [{"source": "node1", "target": "node2"}]

        # Check that session_id is preserved (not regenerated)
        assert enriched_data["session_id"] == "session-123"

        # Check that new fields are added with correct values
        assert enriched_data["session_name"] == "my_agent_run"  # Uses name as session_name
        assert enriched_data["run_name"] == "my_agent_run"  # Uses name as run_name
        assert "session_start_time" in enriched_data
        assert "session_end_time" in enriched_data
        assert "run_start_time" in enriched_data
        assert "run_end_time" in enriched_data
        assert enriched_data["run_status"] == "Completed"  # Default status

    def test_enrich_old_format_data_with_defaults(self):
        """Test _enrich_old_format_data handles missing fields with defaults."""
        handler = RailtownHandler()

        # Minimal old format data
        old_format_data = {
            "name": "test_run",
            "nodes": [{"identifier": "node1"}],
            "steps": [{"step": 1}],
            "edges": [{"source": "node1", "target": "node2"}],
        }

        enriched_data = handler._enrich_old_format_data(old_format_data)

        # Check defaults are applied
        assert enriched_data["session_id"] != "default-session"  # Should be a new GUID
        assert enriched_data["run_id"] != "default-run"  # Should be a new GUID
        assert enriched_data["session_name"] == "test_run"
        assert enriched_data["run_name"] == "test_run"
        assert enriched_data["run_status"] == "Completed"

        # Verify GUID format
        assert uuid.UUID(enriched_data["session_id"])  # Should be valid UUID
        assert uuid.UUID(enriched_data["run_id"])  # Should be valid UUID

    def test_upload_old_format_enrichment(self):
        """Test that old format data gets enriched during upload."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Mock the _get_conductr_presigned_sas_url method
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        # Old format data
        old_format_data = {
            "name": "legacy_agent_run",
            "session_id": "legacy-session-123",
            "run_id": "legacy-run-456",
            "nodes": [{"identifier": "node1", "node_type": "test"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler._upload_single_agent_run(old_format_data)

        assert result is True
        assert mock_client.put.called

        # Verify the uploaded data contains enriched fields
        call_args = mock_client.put.call_args
        uploaded_data = call_args[1]["data"].decode("utf-8")
        uploaded_json = json.loads(uploaded_data)

        # Check that enriched data contains both original and new fields
        assert uploaded_json["name"] == "legacy_agent_run"  # Original field preserved

        # Check that session_id is preserved (not regenerated)
        assert uploaded_json["session_id"] == "legacy-session-123"  # Should preserve original

        # Check that run_id is preserved from original data
        assert uploaded_json["run_id"] == "legacy-run-456"  # Should preserve original

        # Check that new fields are added with correct values
        assert uploaded_json["session_name"] == "legacy_agent_run"
        assert uploaded_json["run_name"] == "legacy_agent_run"
        assert uploaded_json["run_status"] == "Completed"
        assert "session_start_time" in uploaded_json
        assert "session_end_time" in uploaded_json
        assert "run_start_time" in uploaded_json
        assert "run_end_time" in uploaded_json

        # Check that all required arrays are present and not null
        assert isinstance(uploaded_json["nodes"], list)
        assert isinstance(uploaded_json["steps"], list)
        assert isinstance(uploaded_json["edges"], list)
