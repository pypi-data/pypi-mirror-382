"""Unit tests for DetailService."""

import pytest
from unittest.mock import Mock
from check_bitdefender.services.detail_service import DetailService
from check_bitdefender.core.exceptions import DefenderAPIError


@pytest.fixture
def mock_client():
    """Create a mock DefenderClient."""
    client = Mock()
    client.list_endpoints = Mock()
    client.get_endpoint_details = Mock()
    return client


@pytest.fixture
def service(mock_client):
    """Create DetailService with mock client."""
    return DetailService(mock_client, verbose_level=0)


def test_init(mock_client):
    """Test service initialization."""
    service = DetailService(mock_client, verbose_level=0)
    assert service.defender == mock_client
    assert hasattr(service, "logger")


def test_get_result_endpoint_found_with_id(service, mock_client):
    """Test successful check with endpoint ID."""
    mock_details = {
        "id": "ep123",
        "name": "test-server",
        "operatingSystem": "Windows Server 2019",
        "lastSeen": "2023-07-20T10:00:00",
        "lastSuccessfulScan": {
            "name": "scan_name",
            "date": "2023-07-19T04:09:29+00:00"
        },
        "malwareStatus": {
            "detection": False,
            "infected": False
        },
        "riskScore": {
            "value": "81%"
        }
    }
    mock_client.get_endpoint_details.return_value = mock_details

    result = service.get_result(endpoint_id="ep123")

    assert result["value"] == 1  # Found
    assert "Host found" in result["details"][0]
    assert "test-server" in result["details"][0]
    assert "id: ep123" in result["details"][1]
    assert "operatingSystem: Windows Server 2019" in result["details"][3]
    assert "malwareStatus_detection: false" in result["details"][6]
    assert "malwareStatus_infected: false" in result["details"][7]
    assert "riskScore: 81%" in result["details"][8]
    mock_client.get_endpoint_details.assert_called_once_with("ep123")


def test_get_result_endpoint_found_with_dns_name(service, mock_client):
    """Test successful check with DNS name."""
    mock_endpoints = {
        "value": [
            {
                "id": "ep123",
                "fqdn": "test.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_details = {
        "id": "ep123",
        "name": "test.domain.com",
        "operatingSystem": "Windows Server 2019",
        "lastSeen": "2023-07-20T10:00:00",
        "lastSuccessfulScan": {
            "name": "scan_name",
            "date": "2023-07-19T04:09:29+00:00"
        },
        "malwareStatus": {
            "detection": False,
            "infected": False
        },
        "riskScore": {
            "value": "50%"
        }
    }
    mock_client.list_endpoints.return_value = mock_endpoints
    mock_client.get_endpoint_details.return_value = mock_details

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 1  # Found
    assert "Host found" in result["details"][0]
    assert "test.domain.com" in result["details"][0]
    mock_client.list_endpoints.assert_called_once()
    mock_client.get_endpoint_details.assert_called_once_with("ep123")


def test_get_result_endpoint_not_found_by_dns(service, mock_client):
    """Test check for endpoint that doesn't exist (by DNS name)."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "fqdn": "other.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 0  # Not found
    assert "Host not found" in result["details"][0]
    assert "test.domain.com" in result["details"][0]


def test_get_result_no_endpoints_in_system(service, mock_client):
    """Test check when no endpoints exist in system."""
    mock_response = {"value": []}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 0  # Not found
    assert "Host not found" in result["details"][0]


def test_get_result_missing_value_key(service, mock_client):
    """Test check when API response missing value key."""
    mock_response = {}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 0  # Not found
    assert "Host not found" in result["details"][0]


def test_get_result_requires_identifier(service, mock_client):
    """Test that either endpoint_id or dns_name is required."""
    with pytest.raises(ValueError, match="Either endpoint_id or dns_name must be provided"):
        service.get_result()


def test_get_result_api_error_on_details(service, mock_client):
    """Test handling of API error when getting details."""
    mock_endpoints = {
        "value": [
            {
                "id": "ep123",
                "fqdn": "test.domain.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_endpoints
    mock_client.get_endpoint_details.side_effect = DefenderAPIError("API Error")

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 0  # Error treated as not found
    assert "Failed to get endpoint details" in result["details"][0]


def test_get_result_with_malware_detected(service, mock_client):
    """Test endpoint with malware detected."""
    mock_details = {
        "id": "ep123",
        "name": "infected-server",
        "operatingSystem": "Windows 10",
        "lastSeen": "2023-07-20T10:00:00",
        "lastSuccessfulScan": {
            "name": "scan_name",
            "date": "2023-07-19T04:09:29+00:00"
        },
        "malwareStatus": {
            "detection": True,
            "infected": True
        },
        "riskScore": {
            "value": "95%"
        }
    }
    mock_client.get_endpoint_details.return_value = mock_details

    result = service.get_result(endpoint_id="ep123")

    assert result["value"] == 1  # Found
    assert "malwareStatus_detection: true" in result["details"][6]
    assert "malwareStatus_infected: true" in result["details"][7]
    assert "riskScore: 95%" in result["details"][8]


def test_get_result_missing_optional_fields(service, mock_client):
    """Test handling of missing optional fields in response."""
    mock_details = {
        "id": "ep123",
        "name": "minimal-server"
    }
    mock_client.get_endpoint_details.return_value = mock_details

    result = service.get_result(endpoint_id="ep123")

    assert result["value"] == 1  # Found
    assert "operatingSystem: N/A" in result["details"][3]
    assert "lastSeen: N/A" in result["details"][4]
    assert "lastSuccessfulScan: N/A" in result["details"][5]
    assert "riskScore: N/A" in result["details"][8]


def test_logging_calls(mock_client):
    """Test that logging methods are called appropriately."""
    service = DetailService(mock_client, verbose_level=1)
    service.logger = Mock()

    mock_details = {
        "id": "ep123",
        "name": "test-server",
        "operatingSystem": "Windows",
        "lastSeen": "2023-07-20T10:00:00",
        "malwareStatus": {},
        "riskScore": {}
    }
    mock_client.get_endpoint_details.return_value = mock_details

    service.get_result(endpoint_id="ep123")

    service.logger.method_entry.assert_called_once()
    service.logger.method_exit.assert_called_once()
