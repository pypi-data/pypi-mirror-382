"""Unit tests for LastScanService."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta, timezone
from check_bitdefender.services.lastscan_service import LastScanService
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
    """Create LastScanService with mock client."""
    return LastScanService(mock_client, verbose_level=0)


def test_init(mock_client):
    """Test service initialization."""
    service = LastScanService(mock_client, verbose_level=0)
    assert service.defender == mock_client
    assert hasattr(service, "logger")


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

    assert result["value"] == 999
    assert "Host not found" in result["details"][0]
    assert "test.domain.com" in result["details"][0]


def test_get_result_no_endpoints_in_system(service, mock_client):
    """Test check when no endpoints exist in system."""
    mock_response = {"value": []}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 999
    assert "Host not found" in result["details"][0]


def test_get_result_missing_value_key(service, mock_client):
    """Test check when API response missing value key."""
    mock_response = {}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 999
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
    service = LastScanService(mock_client, verbose_level=1)
    service.logger = Mock()

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    timestamp_str = yesterday.isoformat()

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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"date": timestamp_str}
    }

    service.get_result(dns_name="test.domain.com")

    service.logger.method_entry.assert_called_once()
    service.logger.method_exit.assert_called_once()


def test_get_result_invalid_timestamp_format(service, mock_client):
    """Test handling of invalid timestamp format."""
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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"date": "invalid-date-format"}
    }

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 999
    assert "unable to parse" in result["details"][0]


def test_get_result_by_endpoint_id(service, mock_client):
    """Test finding endpoint by endpoint_id."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    timestamp_str = yesterday.isoformat()

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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"date": timestamp_str}
    }

    result = service.get_result(endpoint_id="ep123")

    assert result["value"] == 1
    assert "last scanned 1 days ago" in result["details"][0]
    mock_client.get_endpoint_details.assert_called_once_with("ep123")


def test_get_result_api_error_on_details(service, mock_client):
    """Test handling when get_endpoint_details raises an exception."""
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
    mock_client.get_endpoint_details.side_effect = Exception("API Error")

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 0
    assert "Failed to get endpoint details: API Error" in result["details"][0]


def test_get_result_no_lastscan_in_details(service, mock_client):
    """Test when endpoint details has no lastSuccessfulScan field."""
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
    mock_client.get_endpoint_details.return_value = {}

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 999
    assert "no last scan data" in result["details"][0]
    assert "test.domain.com" in result["details"][0]


def test_get_result_lastscan_not_dict(service, mock_client):
    """Test when lastSuccessfulScan is not a dictionary."""
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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": "not-a-dict"
    }

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 999
    assert "no last scan data" in result["details"][0]


def test_get_result_lastscan_no_date(service, mock_client):
    """Test when lastSuccessfulScan dict has no date field."""
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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"name": "scan1"}
    }

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 999
    assert "no last scan date" in result["details"][0]


def test_get_result_with_naive_datetime(service, mock_client):
    """Test with naive datetime string (no timezone)."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=2)
    timestamp_str = yesterday.strftime("%Y-%m-%dT%H:%M:%S")

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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"date": timestamp_str}
    }

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 2
    assert "last scanned 2 days ago" in result["details"][0]


def test_get_result_with_timestamp_number(service, mock_client):
    """Test with numeric timestamp instead of string."""
    three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
    timestamp_num = int(three_days_ago.timestamp())

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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"date": timestamp_num}
    }

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 3
    assert "last scanned 3 days ago" in result["details"][0]


def test_get_result_with_z_suffix(service, mock_client):
    """Test with ISO timestamp ending in Z."""
    four_days_ago = datetime.now(timezone.utc) - timedelta(days=4)
    timestamp_str = four_days_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"date": timestamp_str}
    }

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 4
    assert "last scanned 4 days ago" in result["details"][0]


def test_get_result_scanned_today(service, mock_client):
    """Test endpoint scanned today (0 days ago)."""
    now = datetime.now(timezone.utc)
    timestamp_str = now.isoformat()

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
    mock_client.get_endpoint_details.return_value = {
        "lastSuccessfulScan": {"date": timestamp_str}
    }

    result = service.get_result(dns_name="test.domain.com")

    assert result["value"] == 0
    assert "last scanned 0 days ago" in result["details"][0]
