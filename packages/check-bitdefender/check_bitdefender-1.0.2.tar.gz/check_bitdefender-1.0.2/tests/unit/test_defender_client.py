"""Unit tests for DefenderClient."""

import pytest
from unittest.mock import Mock, patch
from check_bitdefender.core.defender import DefenderClient
from check_bitdefender.core.exceptions import DefenderAPIError
import requests


@pytest.fixture
def client():
    """Create DefenderClient instance."""
    return DefenderClient("test_token", timeout=10, verbose_level=0)


@pytest.fixture
def client_with_parent():
    """Create DefenderClient instance with parent_id."""
    return DefenderClient("test_token", parent_id="parent123", verbose_level=0)


def test_init():
    """Test client initialization."""
    client = DefenderClient("my_token", timeout=30, region="api", verbose_level=1)
    assert client.authenticator == "my_token"
    assert client.timeout == 30
    assert client.region == "api"
    assert client.base_url == "https://cloudgz.gravityzone.bitdefender.com"
    assert hasattr(client, "logger")


def test_init_with_parent_id():
    """Test client initialization with parent_id."""
    client = DefenderClient("token", parent_id="parent456")
    assert client.parent_id == "parent456"


def test_get_base_url_api_region(client):
    """Test base URL for api region."""
    url = client._get_base_url("api")
    assert url == "https://cloudgz.gravityzone.bitdefender.com"


def test_get_base_url_unknown_region(client):
    """Test base URL defaults to api for unknown region."""
    url = client._get_base_url("unknown")
    assert url == "https://cloudgz.gravityzone.bitdefender.com"


def test_get_auth_header(client):
    """Test authentication header generation."""
    header = client._get_auth_header()
    assert header.startswith("Basic ")
    # Verify it's base64 encoded
    import base64
    encoded_part = header.replace("Basic ", "")
    decoded = base64.b64decode(encoded_part).decode()
    assert decoded == "test_token:"


def test_map_managed_status_true(client):
    """Test mapping managed status when True."""
    status = client._map_managed_status(True)
    assert status == "Onboarded"


def test_map_managed_status_false(client):
    """Test mapping managed status when False."""
    status = client._map_managed_status(False)
    assert status == "InsufficientInfo"


def test_extract_os_platform_windows(client):
    """Test OS platform extraction for Windows."""
    assert client._extract_os_platform("Windows 10 Pro") == "Windows"
    assert client._extract_os_platform("windows server 2019") == "Windows"


def test_extract_os_platform_linux(client):
    """Test OS platform extraction for Linux."""
    assert client._extract_os_platform("Linux Ubuntu 20.04") == "Linux"
    assert client._extract_os_platform("linux") == "Linux"


def test_extract_os_platform_mac(client):
    """Test OS platform extraction for Mac."""
    assert client._extract_os_platform("Mac OS X 10.15") == "Mac"
    assert client._extract_os_platform("darwin") == "Mac"


def test_extract_os_platform_unknown(client):
    """Test OS platform extraction for unknown OS."""
    assert client._extract_os_platform("FreeBSD") == "Unknown"
    assert client._extract_os_platform("") == "Unknown"


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_success(mock_post, client):
    """Test successful endpoint listing."""
    # Mock API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": {
            "items": [
                {
                    "id": "ep1",
                    "fqdn": "host1.domain.com",
                    "isManaged": True,
                    "operatingSystemVersion": "Windows 10",
                    "lastSeen": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "ep2",
                    "name": "host2",
                    "isManaged": False,
                    "operatingSystemVersion": "Linux Ubuntu",
                    "lastSuccessfulScan": {"date": "2024-01-02T00:00:00Z"}
                }
            ],
            "pagesCount": 1,
            "total": 2
        }
    }
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    result = client.list_endpoints()

    assert "value" in result
    assert len(result["value"]) == 2
    assert result["value"][0]["id"] == "ep1"
    assert result["value"][0]["computerDnsName"] == "host1.domain.com"
    assert result["value"][0]["onboardingStatus"] == "Onboarded"
    assert result["value"][0]["osPlatform"] == "Windows"
    assert result["value"][0]["lastSeen"] == "2024-01-01T00:00:00Z"

    assert result["value"][1]["id"] == "ep2"
    assert result["value"][1]["computerDnsName"] == "host2"
    assert result["value"][1]["onboardingStatus"] == "InsufficientInfo"
    assert result["value"][1]["osPlatform"] == "Linux"
    assert result["value"][1]["lastSeen"] == "2024-01-02T00:00:00Z"

    mock_post.assert_called_once()


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_with_pagination(mock_post, client):
    """Test endpoint listing with multiple pages."""
    # Mock responses for 2 pages
    mock_response_page1 = Mock()
    mock_response_page1.json.return_value = {
        "result": {
            "items": [{"id": "ep1", "fqdn": "host1.com", "isManaged": True, "operatingSystemVersion": "Windows"}],
            "pagesCount": 2,
            "total": 2
        }
    }
    mock_response_page1.raise_for_status = Mock()

    mock_response_page2 = Mock()
    mock_response_page2.json.return_value = {
        "result": {
            "items": [{"id": "ep2", "fqdn": "host2.com", "isManaged": True, "operatingSystemVersion": "Linux"}],
            "pagesCount": 2,
            "total": 2
        }
    }
    mock_response_page2.raise_for_status = Mock()

    mock_post.side_effect = [mock_response_page1, mock_response_page2]

    result = client.list_endpoints()

    assert len(result["value"]) == 2
    assert result["value"][0]["id"] == "ep1"
    assert result["value"][1]["id"] == "ep2"
    assert mock_post.call_count == 2


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_with_parent_id(mock_post, client_with_parent):
    """Test endpoint listing with parent_id."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": {
            "items": [{"id": "ep1", "fqdn": "host1.com", "isManaged": True, "operatingSystemVersion": "Windows"}],
            "pagesCount": 1,
            "total": 1
        }
    }
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    client_with_parent.list_endpoints()

    # Verify parent_id was included in the request
    call_args = mock_post.call_args
    payload = call_args.kwargs['json']
    assert payload['params']['parentId'] == 'parent123'


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_with_override_parent_id(mock_post, client):
    """Test endpoint listing with override parent_id parameter."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": {
            "items": [{"id": "ep1", "fqdn": "host1.com", "isManaged": True, "operatingSystemVersion": "Windows"}],
            "pagesCount": 1,
            "total": 1
        }
    }
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    client.list_endpoints(parent_id="override_parent")

    # Verify override parent_id was used
    call_args = mock_post.call_args
    payload = call_args.kwargs['json']
    assert payload['params']['parentId'] == 'override_parent'


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_missing_result(mock_post, client):
    """Test handling of invalid API response missing 'result' field."""
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    with pytest.raises(DefenderAPIError, match="Invalid API response: missing 'result' field"):
        client.list_endpoints()


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_request_exception(mock_post, client):
    """Test handling of request exceptions."""
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(DefenderAPIError, match="Failed to list endpoints"):
        client.list_endpoints()


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_http_error(mock_post, client):
    """Test handling of HTTP errors."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
    mock_post.return_value = mock_response

    with pytest.raises(DefenderAPIError, match="Failed to list endpoints"):
        client.list_endpoints()


@patch('check_bitdefender.core.defender.requests.post')
def test_get_endpoint_details_success(mock_post, client):
    """Test successful endpoint details retrieval."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": {
            "id": "ep123",
            "name": "test-host",
            "operatingSystem": "Windows 10",
            "lastSeen": "2024-01-01T00:00:00Z",
            "malwareStatus": {"detection": False, "infected": False},
            "riskScore": {"value": "81%"}
        }
    }
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    result = client.get_endpoint_details("ep123")

    assert result["id"] == "ep123"
    assert result["name"] == "test-host"
    assert result["operatingSystem"] == "Windows 10"

    # Verify request payload
    call_args = mock_post.call_args
    payload = call_args.kwargs['json']
    assert payload['method'] == 'getManagedEndpointDetails'
    assert payload['params']['endpointId'] == 'ep123'
    assert payload['params']['options']['includeScanLogs'] is True


@patch('check_bitdefender.core.defender.requests.post')
def test_get_endpoint_details_missing_result(mock_post, client):
    """Test handling of invalid response missing 'result' field."""
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    with pytest.raises(DefenderAPIError, match="Invalid API response: missing 'result' field"):
        client.get_endpoint_details("ep123")


@patch('check_bitdefender.core.defender.requests.post')
def test_get_endpoint_details_request_exception(mock_post, client):
    """Test handling of request exceptions."""
    mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

    with pytest.raises(DefenderAPIError, match="Failed to get endpoint details"):
        client.get_endpoint_details("ep123")


@patch('check_bitdefender.core.defender.requests.post')
def test_list_endpoints_empty_items(mock_post, client):
    """Test handling of empty items list."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": {
            "items": [],
            "pagesCount": 1,
            "total": 0
        }
    }
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    result = client.list_endpoints()

    assert "value" in result
    assert len(result["value"]) == 0
