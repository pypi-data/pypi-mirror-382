"""Unit tests for OnboardingService."""

import pytest
from unittest.mock import Mock
from check_bitdefender.services.onboarding_service import OnboardingService
from check_bitdefender.core.exceptions import DefenderAPIError


@pytest.fixture
def mock_client():
    """Create a mock DefenderClient."""
    client = Mock()
    client.list_endpoints = Mock()
    return client


@pytest.fixture
def service(mock_client):
    """Create OnboardingService with mock client."""
    return OnboardingService(mock_client, verbose_level=0)


def test_init(mock_client):
    """Test service initialization."""
    service = OnboardingService(mock_client, verbose_level=0)
    assert service.defender == mock_client
    assert hasattr(service, "logger")


def test_get_result_endpoint_onboarded(service, mock_client):
    """Test successful check for onboarded endpoint."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "test.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 0  # Onboarded
    assert "Host onboarded" in result["details"][0]
    assert "test.domain.com" in result["details"][0]
    mock_client.list_endpoints.assert_called_once()


def test_get_result_endpoint_not_found(service, mock_client):
    """Test check for endpoint that doesn't exist."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "other.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 1  # Not found
    assert "Host not found" in result["details"][0]
    assert "test.domain.com" in result["details"][0]


def test_get_result_endpoint_not_onboarded(service, mock_client):
    """Test check for endpoint that is not onboarded."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "test.domain.com",
                "onboardingStatus": "InsufficientInfo",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 1  # Not onboarded
    assert "Host not onboarded" in result["details"][0]
    assert "test.domain.com" in result["details"][0]
    assert "InsufficientInfo" in result["details"][1]


def test_get_result_by_endpoint_id(service, mock_client):
    """Test check using endpoint ID instead of DNS name."""
    mock_response = {
        "value": [
            {
                "id": "ep123",
                "computerDnsName": "test.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(endpoint_id="ep123")

    assert result["value"] == 0  # Onboarded
    assert "Host onboarded" in result["details"][0]


def test_get_result_no_endpoints_in_system(service, mock_client):
    """Test check when no endpoints exist in system."""
    mock_response = {"value": []}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 1  # Not found
    assert "Host not found" in result["details"][0]


def test_get_result_missing_value_key(service, mock_client):
    """Test check when API response missing value key."""
    mock_response = {}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 1  # Not found
    assert "Host not found" in result["details"][0]


def test_get_result_requires_identifier(service, mock_client):
    """Test that either endpoint_id or dns_name is required."""
    with pytest.raises(ValueError, match="Either endpoint_id or dns_name must be provided"):
        service.get_result()


def test_api_exception_propagation(service, mock_client):
    """Test that API exceptions are propagated."""
    mock_client.list_endpoints.side_effect = DefenderAPIError("API Error")

    with pytest.raises(DefenderAPIError, match="API Error"):
        service.get_result(dns_name="test.domain.com")


def test_logging_calls(mock_client):
    """Test that logging methods are called appropriately."""
    service = OnboardingService(mock_client, verbose_level=1)
    service.logger = Mock()

    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "test.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    service.get_result(dns_name="test.domain.com")

    service.logger.method_entry.assert_called_once()
    service.logger.method_exit.assert_called_once()


def test_get_result_multiple_endpoints(service, mock_client):
    """Test finding correct endpoint among multiple."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "server1.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            },
            {
                "id": "ep2",
                "computerDnsName": "server2.domain.com",
                "onboardingStatus": "InsufficientInfo",
                "osPlatform": "Linux"
            },
            {
                "id": "ep3",
                "computerDnsName": "server3.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    # Find the second endpoint (not onboarded)
    result = service.get_result(dns_name="server2.domain.com")

    assert result["value"] == 1  # Not onboarded
    assert "server2.domain.com" in result["details"][0]


def test_get_result_unsupported_status(service, mock_client):
    """Test endpoint with Unsupported status."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "test.domain.com",
                "onboardingStatus": "Unsupported",
                "osPlatform": "Mac"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 1  # Not onboarded
    assert "Host not onboarded" in result["details"][0]
    assert "Unsupported" in result["details"][1]
