"""
Unit tests for api_connector module.
"""

import pytest
from unittest.mock import patch, Mock
from app.api_connector import (
    get_law_interpretations,
    parse_interpretation_list,
    get_full_interpretation_text,
    parse_full_text,
)


class TestGetLawInterpretations:
    """Tests for get_law_interpretations function."""

    @patch("app.api_connector.requests.get")
    def test_successful_request(self, mock_get):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_law_interpretations("퇴직")

        assert result == {"test": "data"}
        mock_get.assert_called_once()

    @patch("app.api_connector.requests.get")
    def test_request_timeout(self, mock_get):
        """Test API request timeout handling."""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        result = get_law_interpretations("퇴직")

        assert result is None

    @patch("app.api_connector.requests.get")
    def test_http_error(self, mock_get):
        """Test HTTP error handling."""
        import requests

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        result = get_law_interpretations("퇴직")

        assert result is None


class TestParseInterpretationList:
    """Tests for parse_interpretation_list function."""

    def test_parse_lawsearch_structure(self):
        """Test parsing lawSearch structure."""
        json_data = {
            "lawSearch": {
                "moelCgmExpc": [
                    {
                        "안건번호": "TEST-001",
                        "안건명": "Test Case",
                        "법령해석일련번호": "12345",
                        "질의기관명": "Test Org",
                        "해석일자": "20240101",
                    }
                ]
            }
        }

        result = parse_interpretation_list(json_data)

        assert len(result) == 1
        assert result[0]["case_number"] == "TEST-001"
        assert result[0]["interpretation_id"] == "12345"

    def test_parse_cgmexpc_structure(self):
        """Test parsing CgmExpc structure."""
        json_data = {
            "CgmExpc": {
                "cgmExpc": [
                    {
                        "안건번호": "TEST-002",
                        "안건명": "Test Case 2",
                        "법령해석일련번호": "67890",
                        "질의기관명": "Test Org 2",
                        "해석일자": "20240102",
                    }
                ]
            }
        }

        result = parse_interpretation_list(json_data)

        assert len(result) == 1
        assert result[0]["case_number"] == "TEST-002"

    def test_empty_data(self):
        """Test handling of empty data."""
        result = parse_interpretation_list(None)
        assert result == []

        result = parse_interpretation_list({})
        assert result == []


class TestGetFullInterpretationText:
    """Tests for get_full_interpretation_text function."""

    @patch("app.api_connector.requests.get")
    def test_successful_request(self, mock_get):
        """Test successful full text retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"CgmExpcService": {"test": "data"}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_full_interpretation_text("12345")

        assert "CgmExpcService" in result
        mock_get.assert_called_once()


class TestParseFullText:
    """Tests for parse_full_text function."""

    def test_successful_parse(self):
        """Test successful parsing of full text."""
        json_data = {
            "CgmExpcService": {
                "질의요지": "Test question",
                "회답": "Test answer",
                "안건명": "Test title",
                "법령해석일련번호": "12345",
                "해석일자": "20240101",
            }
        }

        result = parse_full_text(json_data)

        assert "text" in result
        assert "metadata" in result
        assert "Test question" in result["text"]
        assert result["metadata"]["title"] == "Test title"

    def test_invalid_data(self):
        """Test handling of invalid data."""
        result = parse_full_text(None)
        assert result == {}

        result = parse_full_text({"wrong": "structure"})
        assert result == {}
