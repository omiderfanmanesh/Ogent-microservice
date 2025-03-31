"""
Tests for verifying OpenAI API connectivity.

This module provides tests to ensure that the OpenAI API
connection is working properly with the configured API key.
"""

import os
import sys
import unittest
from unittest import TestCase
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic


class TestOpenAIConnectivity(TestCase):
    """Test OpenAI API connectivity."""

    def setUp(self):
        """Set up the test environment."""
        # Load environment variables
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    def test_openai_api_key_exists(self):
        """Test that the OpenAI API key exists."""
        self.assertIsNotNone(self.openai_api_key, "OpenAI API key not found in environment variables")
        self.assertTrue(len(self.openai_api_key) > 0, "OpenAI API key is empty")

    def test_openai_connection(self):
        """Test connection to OpenAI API."""
        if not self.openai_api_key:
            self.skipTest("OpenAI API key not available")

        try:
            # Create an OpenAI client
            client = OpenAI(api_key=self.openai_api_key)
            
            # Test API with a simple chat completion
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello, respond with just the word 'OK' for testing"}],
                max_tokens=5
            )
            
            # Check that we got a response
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.choices)
            self.assertTrue(len(response.choices) > 0)
            self.assertIsNotNone(response.choices[0].message.content)
            
        except Exception as e:
            self.fail(f"OpenAI API connection failed: {e}")

    def test_anthropic_connection(self):
        """Test connection to Anthropic API if key is available."""
        if not self.anthropic_api_key:
            self.skipTest("Anthropic API key not available")
            
        try:
            # Create an Anthropic client
            client = Anthropic(api_key=self.anthropic_api_key)
            
            # Test API with a simple completion
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello, respond with just the word 'OK' for testing"}]
            )
            
            # Check that we got a response
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.content)
            self.assertTrue(len(response.content) > 0)
            
        except Exception as e:
            self.fail(f"Anthropic API connection failed: {e}")


if __name__ == "__main__":
    unittest.main() 