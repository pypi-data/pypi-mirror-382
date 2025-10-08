"""Unit tests for EndpointsService."""

import pytest
from unittest.mock import Mock
from check_bitdefender.services.endpoint_service import EndpointsService
from check_bitdefender.core.exceptions import DefenderAPIError


@pytest.fixture
def mock_client():
    """Create a mock DefenderClient."""
    client = Mock()
    client.list_endpoints = Mock()
    return client


@pytest.fixture
def service(mock_client):
    """Create EndpointsService with mock client."""
    return EndpointsService(mock_client, verbose_level=0)


def test_init(mock_client):
    """Test service initialization."""
    service = EndpointsService(mock_client, verbose_level=0)
    assert service.defender == mock_client
    assert hasattr(service, "logger")


def test_get_result_success(service, mock_client):
    """Test successful endpoint list retrieval."""
    # Mock API response with multiple endpoints
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "test1.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            },
            {
                "id": "ep2",
                "computerDnsName": "test2.com",
                "onboardingStatus": "InsufficientInfo",
                "osPlatform": "Linux"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result()

    assert result["value"] == 2
    assert len(result["details"]) == 3  # header + 2 endpoints
    assert "Total endpoints: 2" in result["details"][0]
    assert "ep1: test1.com (Windows) ✓" in result["details"][1]
    assert "ep2: test2.com (Linux) ✗" in result["details"][2]
    mock_client.list_endpoints.assert_called_once()


def test_get_result_no_endpoints(service, mock_client):
    """Test handling of empty endpoint list."""
    mock_response = {"value": []}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result()

    assert result["value"] == 0
    assert "No endpoints found" in result["details"][0]


def test_get_result_missing_value(service, mock_client):
    """Test handling of response without 'value' key."""
    mock_response = {}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result()

    assert result["value"] == 0
    assert "No endpoints found" in result["details"][0]


def test_endpoint_sorting_by_status(service, mock_client):
    """Test endpoints are sorted by status then name."""
    # Mock response with mixed statuses
    mock_response = {
        "value": [
            {
                "id": "ep3",
                "computerDnsName": "unsupported.com",
                "onboardingStatus": "Unsupported",
                "osPlatform": "Windows"
            },
            {
                "id": "ep1",
                "computerDnsName": "alpha.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            },
            {
                "id": "ep2",
                "computerDnsName": "beta.com",
                "onboardingStatus": "InsufficientInfo",
                "osPlatform": "Linux"
            },
            {
                "id": "ep4",
                "computerDnsName": "bravo.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Linux"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result()

    # Verify sorted order: Onboarded first (alphabetically), then InsufficientInfo, then Unsupported
    details = result["details"]
    assert "alpha.com" in details[1]  # First Onboarded (alphabetically)
    assert "bravo.com" in details[2]  # Second Onboarded (alphabetically)
    assert "beta.com" in details[3]  # InsufficientInfo
    assert "unsupported.com" in details[4]  # Unsupported


def test_api_exception_propagation(service, mock_client):
    """Test that API exceptions are propagated."""
    mock_client.list_endpoints.side_effect = DefenderAPIError("API Error")

    with pytest.raises(DefenderAPIError, match="API Error"):
        service.get_result()


def test_logging_calls(mock_client):
    """Test that logging methods are called appropriately."""
    service = EndpointsService(mock_client, verbose_level=1)
    service.logger = Mock()

    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "test.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    service.get_result()

    service.logger.method_entry.assert_called_once_with("get_result")
    service.logger.method_exit.assert_called_once()


def test_get_details_success(service, mock_client):
    """Test get_details method returns formatted list."""
    mock_response = {
        "value": [
            {
                "id": "1a2b3c4d5e6f7890abcdef12",
                "computerDnsName": "server01.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            },
            {
                "id": "2b3c4d5e6f7890abcdef1234",
                "computerDnsName": "server02.com",
                "onboardingStatus": "InsufficientInfo",
                "osPlatform": "Linux"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    details = service.get_details()

    assert len(details) == 2
    # Check that IDs are truncated to 10 chars
    assert details[0].startswith("1a2b3c4d5e")
    assert "server01.com" in details[0]
    assert "Onboarded" in details[0]
    assert "Windows" in details[0]


def test_get_details_no_endpoints(service, mock_client):
    """Test get_details with no endpoints returns empty list."""
    mock_response = {"value": []}
    mock_client.list_endpoints.return_value = mock_response

    details = service.get_details()

    assert details == []


def test_get_details_missing_value(service, mock_client):
    """Test get_details handles missing 'value' key."""
    mock_response = {}
    mock_client.list_endpoints.return_value = mock_response

    details = service.get_details()

    assert details == []


def test_onboarding_status_indicators(service, mock_client):
    """Test that onboarding status indicators are correct."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": "onboarded.com",
                "onboardingStatus": "Onboarded",
                "osPlatform": "Windows"
            },
            {
                "id": "ep2",
                "computerDnsName": "insufficient.com",
                "onboardingStatus": "InsufficientInfo",
                "osPlatform": "Linux"
            },
            {
                "id": "ep3",
                "computerDnsName": "unsupported.com",
                "onboardingStatus": "Unsupported",
                "osPlatform": "Mac"
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result()
    details = result["details"]

    # Check for ✓ indicator for Onboarded
    onboarded_line = [d for d in details if "onboarded.com" in d][0]
    assert "✓" in onboarded_line

    # Check for ✗ indicator for non-Onboarded statuses
    insufficient_line = [d for d in details if "insufficient.com" in d][0]
    assert "✗" in insufficient_line

    unsupported_line = [d for d in details if "unsupported.com" in d][0]
    assert "✗" in unsupported_line


def test_get_result_with_null_values(service, mock_client):
    """Test handling of endpoints with null/missing values."""
    mock_response = {
        "value": [
            {
                "id": "ep1",
                "computerDnsName": None,
                "onboardingStatus": None,
                "osPlatform": None
            }
        ]
    }
    mock_client.list_endpoints.return_value = mock_response

    # Should not raise an exception
    result = service.get_result()

    assert result["value"] == 1
    assert len(result["details"]) == 2  # header + 1 endpoint


def test_large_endpoint_list(service, mock_client):
    """Test handling of large endpoint lists with pagination."""
    # Mock a large response (simulating pagination working correctly)
    large_list = [
        {
            "id": f"ep{i}",
            "computerDnsName": f"endpoint{i}.example.com",
            "onboardingStatus": "Onboarded" if i % 2 == 0 else "InsufficientInfo",
            "osPlatform": "Windows" if i % 3 == 0 else "Linux"
        }
        for i in range(150)  # More than default page size
    ]
    mock_response = {"value": large_list}
    mock_client.list_endpoints.return_value = mock_response

    result = service.get_result()

    assert result["value"] == 150
    assert len(result["details"]) == 151  # header + 150 endpoints