"""
Pytest configuration and fixtures.
"""

import pytest
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv()


@pytest.fixture
def sample_law_interpretation():
    """Sample law interpretation data for testing."""
    return {
        "case_number": "TEST-001",
        "case_name": "Test Labor Law Case",
        "interpretation_id": "12345",
        "inquiry_org": "Test Organization",
        "reply_date": "20240101",
    }


@pytest.fixture
def sample_full_text():
    """Sample full text data for testing."""
    return {
        "text": "질의요지: Test question\n\n회답: Test answer",
        "metadata": {
            "title": "Test Title",
            "interpretation_id": "12345",
            "reply_date": "20240101",
        },
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("LAW_API_ID", "test_api_id")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
