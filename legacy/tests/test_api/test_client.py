"""Tests for API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tc_tui.api import ThreatConnectClient, AuthenticationError, NotFoundError, RateLimitError


@patch('tc_tui.api.client.requests.Session')
def test_client_initialization(mock_session):
    """Test client initialization."""
    client = ThreatConnectClient(
        access_id="test_id",
        secret_key="test_secret",
        instance="mycompany"
    )

    assert client.instance == "mycompany"
    assert client.base_url == "https://mycompany.threatconnect.com/api/v3"


@patch('tc_tui.api.client.requests.Session')
def test_client_handles_401(mock_session):
    """Test client raises AuthenticationError on 401."""
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    mock_session_instance = Mock()
    mock_session_instance.request.return_value = mock_response
    mock_session.return_value = mock_session_instance

    client = ThreatConnectClient(
        access_id="test_id",
        secret_key="test_secret",
        instance="mycompany"
    )

    with pytest.raises(AuthenticationError):
        client.get("/indicators")


@patch('tc_tui.api.client.requests.Session')
def test_client_handles_404(mock_session):
    """Test client raises NotFoundError on 404."""
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    mock_session_instance = Mock()
    mock_session_instance.request.return_value = mock_response
    mock_session.return_value = mock_session_instance

    client = ThreatConnectClient(
        access_id="test_id",
        secret_key="test_secret",
        instance="mycompany"
    )

    with pytest.raises(NotFoundError):
        client.get("/indicators/999999")


@patch('tc_tui.api.client.requests.Session')
def test_client_handles_429(mock_session):
    """Test client raises RateLimitError on 429."""
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"

    mock_session_instance = Mock()
    mock_session_instance.request.return_value = mock_response
    mock_session.return_value = mock_session_instance

    client = ThreatConnectClient(
        access_id="test_id",
        secret_key="test_secret",
        instance="mycompany"
    )

    with pytest.raises(RateLimitError):
        client.get("/indicators")


@patch('tc_tui.api.client.requests.Session')
def test_client_successful_get(mock_session):
    """Test successful GET request."""
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [], "count": 0}

    mock_session_instance = Mock()
    mock_session_instance.request.return_value = mock_response
    mock_session.return_value = mock_session_instance

    client = ThreatConnectClient(
        access_id="test_id",
        secret_key="test_secret",
        instance="mycompany"
    )

    result = client.get("/indicators")

    assert result == {"data": [], "count": 0}
    mock_session_instance.request.assert_called_once()
