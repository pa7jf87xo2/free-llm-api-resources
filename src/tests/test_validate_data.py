"""Unit tests for validate_data.py module."""

import unittest
from unittest.mock import patch
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validate_data import validate_url, validate_rate_limit, validate_model, validate_provider


class TestValidateUrl(unittest.TestCase):
    """Tests for the validate_url function."""

    def test_valid_https_url(self):
        errors = []
        validate_url("https://api.example.com/v1", errors)
        self.assertEqual(errors, [])

    def test_valid_http_url(self):
        errors = []
        validate_url("http://localhost:8080", errors)
        self.assertEqual(errors, [])

    def test_invalid_url_no_scheme(self):
        errors = []
        validate_url("api.example.com", errors)
        self.assertTrue(len(errors) > 0)

    def test_none_url(self):
        errors = []
        validate_url(None, errors)
        self.assertTrue(len(errors) > 0)

    def test_empty_url(self):
        errors = []
        validate_url("", errors)
        self.assertTrue(len(errors) > 0)


class TestValidateRateLimit(unittest.TestCase):
    """Tests for the validate_rate_limit function."""

    def test_valid_rate_limit_with_requests_and_period(self):
        errors = []
        rate_limit = {"requests": 100, "period": "minute"}
        validate_rate_limit(rate_limit, errors)
        self.assertEqual(errors, [])

    def test_valid_rate_limit_none(self):
        errors = []
        validate_rate_limit(None, errors)
        self.assertEqual(errors, [])

    def test_invalid_rate_limit_missing_requests(self):
        errors = []
        rate_limit = {"period": "day"}
        validate_rate_limit(rate_limit, errors)
        self.assertTrue(len(errors) > 0)

    def test_invalid_rate_limit_missing_period(self):
        errors = []
        rate_limit = {"requests": 50}
        validate_rate_limit(rate_limit, errors)
        self.assertTrue(len(errors) > 0)

    def test_invalid_rate_limit_negative_requests(self):
        errors = []
        rate_limit = {"requests": -10, "period": "hour"}
        validate_rate_limit(rate_limit, errors)
        self.assertTrue(len(errors) > 0)


class TestValidateModel(unittest.TestCase):
    """Tests for the validate_model function."""

    def test_valid_model(self):
        errors = []
        model = {"name": "gpt-4o", "type": "chat"}
        validate_model(model, errors)
        self.assertEqual(errors, [])

    def test_model_missing_name(self):
        errors = []
        model = {"type": "chat"}
        validate_model(model, errors)
        self.assertTrue(len(errors) > 0)

    def test_model_empty_name(self):
        errors = []
        model = {"name": "", "type": "completion"}
        validate_model(model, errors)
        self.assertTrue(len(errors) > 0)


class TestValidateProvider(unittest.TestCase):
    """Tests for the validate_provider function."""

    def test_valid_provider(self):
        errors = []
        provider = {
            "name": "ExampleAI",
            "url": "https://example.ai",
            "api_base_url": "https://api.example.ai/v1",
            "free_tier": True,
            "requires_account": True,
            "models": [{"name": "example-model", "type": "chat"}],
        }
        validate_provider(provider, errors)
        self.assertEqual(errors, [])

    def test_provider_missing_name(self):
        errors = []
        provider = {
            "url": "https://example.ai",
            "api_base_url": "https://api.example.ai/v1",
            "free_tier": True,
        }
        validate_provider(provider, errors)
        self.assertTrue(len(errors) > 0)

    def test_provider_missing_url(self):
        errors = []
        provider = {
            "name": "ExampleAI",
            "api_base_url": "https://api.example.ai/v1",
            "free_tier": True,
        }
        validate_provider(provider, errors)
        self.assertTrue(len(errors) > 0)


if __name__ == "__main__":
    unittest.main()
