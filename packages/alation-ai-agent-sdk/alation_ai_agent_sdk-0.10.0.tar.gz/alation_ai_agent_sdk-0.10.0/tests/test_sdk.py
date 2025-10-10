import pytest
import requests
from unittest.mock import MagicMock, patch

from alation_ai_agent_sdk.sdk import (
    AlationAIAgentSDK,
    AlationTools,
)
from alation_ai_agent_sdk.api import (
    AUTH_METHOD_USER_ACCOUNT,
    AUTH_METHOD_SERVICE_ACCOUNT,
    AlationAPIError,
    UserAccountAuthParams,
    ServiceAccountAuthParams,
)


# --- Mock API Responses & Constants ---
MOCK_BASE_URL = "https://mock-alation-instance.com"
MOCK_USER_ID = 123
MOCK_REFRESH_TOKEN = "test-refresh-token"
MOCK_CLIENT_ID = "test-client-id"
MOCK_CLIENT_SECRET = "test-client-secret"


REFRESH_TOKEN_RESPONSE_SUCCESS = {
    "api_access_token": "mock-api-access-token-from-refresh",
    "status": "success",
    "user_id": MOCK_USER_ID,
    "token_status": "ACTIVE",
}

JWT_RESPONSE_SUCCESS = {
    "access_token": "mock-jwt-access-token",
    "expires_in": 3600,
    "token_type": "Bearer",
}

CONTEXT_RESPONSE_SUCCESS = {"some_context_key": "some_context_value"}


@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mocks requests.post for all relevant endpoints."""
    mock_post_responses = {}

    def _add_mock_response(
        url_identifier,
        response_json=None,
        status_code=200,
        raise_for_status_exception=None,
        side_effect=None,
    ):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = status_code
        if response_json is not None:
            mock_response.json = MagicMock(return_value=response_json)
        else:
            mock_response.json = MagicMock(
                side_effect=requests.exceptions.JSONDecodeError("No JSON", "doc", 0)
            )

        if raise_for_status_exception:
            mock_response.raise_for_status = MagicMock(side_effect=raise_for_status_exception)
        else:
            mock_response.raise_for_status = MagicMock()

        if side_effect:
            mock_post_responses[url_identifier] = MagicMock(side_effect=side_effect)
        else:
            mock_post_responses[url_identifier] = MagicMock(return_value=mock_response)

    def mock_post_router(*args, **kwargs):
        url = args[0]
        # Match all relevant endpoints
        if "createAPIAccessToken" in url:
            if "createAPIAccessToken" in mock_post_responses:
                return mock_post_responses["createAPIAccessToken"](*args, **kwargs)
        elif "auth/accessToken" in url:
            if "auth/accessToken" in mock_post_responses:
                return mock_post_responses["auth/accessToken"](*args, **kwargs)
        elif "oauth/v2/token" in url:
            if "oauth/v2/token" in mock_post_responses:
                return mock_post_responses["oauth/v2/token"](*args, **kwargs)
        elif "context/" in url:
            if "context/" in mock_post_responses:
                return mock_post_responses["context/"](*args, **kwargs)
        elif url in mock_post_responses:
            return mock_post_responses[url](*args, **kwargs)

        print(f"Unmocked POST URL: {url}")  # Debugging line to see unmocked URLs

        # Fallback for unmocked POST requests
        fallback_response = MagicMock(spec=requests.Response)
        fallback_response.status_code = 404
        fallback_response.json = MagicMock(return_value={"error": "Not Found - Unmocked POST URL"})
        fallback_response.raise_for_status = MagicMock(
            side_effect=requests.exceptions.HTTPError("404 Not Found")
        )
        return fallback_response

    monkeypatch.setattr(requests, "post", mock_post_router)
    return _add_mock_response


@pytest.fixture
def mock_requests_get(monkeypatch):
    """Mocks requests.get for all relevant endpoints."""
    mock_get_responses = {}

    def _add_mock_response(
        url_identifier,
        response_json=None,
        status_code=200,
        raise_for_status_exception=None,
        side_effect=None,
    ):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = status_code
        if response_json is not None:
            mock_response.json = MagicMock(return_value=response_json)
        else:
            mock_response.json = MagicMock(
                side_effect=requests.exceptions.JSONDecodeError("No JSON", "doc", 0)
            )

        if raise_for_status_exception:
            mock_response.raise_for_status = MagicMock(side_effect=raise_for_status_exception)
        else:
            mock_response.raise_for_status = MagicMock()

        if side_effect:
            mock_get_responses[url_identifier] = MagicMock(side_effect=side_effect)
        else:
            mock_get_responses[url_identifier] = MagicMock(return_value=mock_response)

    def mock_get_router(*args, **kwargs):
        url = args[0]
        # Match all relevant endpoints
        if "context/" in url:
            if "context/" in mock_get_responses:
                return mock_get_responses["context/"](*args, **kwargs)
        elif "/api/v1/license" in url:
            if "license" in mock_get_responses:
                return mock_get_responses["license"](*args, **kwargs)
        elif "/full_version" in url:
            if "full_version" in mock_get_responses:
                return mock_get_responses["full_version"](*args, **kwargs)

        # Fallback for unmocked GET requests
        fallback_response = MagicMock(spec=requests.Response)
        fallback_response.status_code = 404
        fallback_response.json = MagicMock(return_value={"error": "Not Found - Unmocked GET URL"})
        fallback_response.raise_for_status = MagicMock(
            side_effect=requests.exceptions.HTTPError("404 Not Found")
        )
        return fallback_response

    monkeypatch.setattr(requests, "get", mock_get_router)
    return _add_mock_response


# --- SDK Initialization Tests ---


def test_sdk_valid_initialization_user_account(mock_requests_post, mock_requests_get):
    """Test valid SDK init with user_account auth method."""
    mock_requests_post("createAPIAccessToken", response_json=REFRESH_TOKEN_RESPONSE_SUCCESS)
    mock_requests_get("license", response_json={"is_cloud": True})
    mock_requests_get("full_version", response_json={"ALATION_RELEASE_NAME": "2025.1.2"})
    sdk = AlationAIAgentSDK(
        base_url=MOCK_BASE_URL,
        auth_method=AUTH_METHOD_USER_ACCOUNT,
        auth_params=UserAccountAuthParams(MOCK_USER_ID, MOCK_REFRESH_TOKEN),
        dist_version="test-dist-version",
    )
    assert sdk.api.auth_method == AUTH_METHOD_USER_ACCOUNT
    assert sdk.api.user_id == MOCK_USER_ID
    assert sdk.api.refresh_token == MOCK_REFRESH_TOKEN
    assert sdk.api.dist_version == "test-dist-version"


def test_sdk_valid_initialization_service_account(mock_requests_post, mock_requests_get):
    """Test valid SDK init with service_account auth method."""
    mock_requests_post("oauth/v2/token", response_json=JWT_RESPONSE_SUCCESS)
    mock_requests_get("license", response_json={"is_cloud": True})
    mock_requests_get("full_version", response_json={"ALATION_RELEASE_NAME": "2025.1.2"})
    sdk = AlationAIAgentSDK(
        base_url=MOCK_BASE_URL,
        auth_method=AUTH_METHOD_SERVICE_ACCOUNT,
        auth_params=ServiceAccountAuthParams(MOCK_CLIENT_ID, MOCK_CLIENT_SECRET),
        dist_version="test-dist-version",
    )
    assert sdk.api.auth_method == AUTH_METHOD_SERVICE_ACCOUNT
    assert sdk.api.client_id == MOCK_CLIENT_ID
    assert sdk.api.client_secret == MOCK_CLIENT_SECRET
    assert sdk.api.dist_version == "test-dist-version"


@pytest.mark.parametrize(
    "auth_method, auth_params, expected_error_message_part",
    [
        (
            AUTH_METHOD_USER_ACCOUNT,
            (MOCK_USER_ID,),
            "provide a tuple with (user_id: int, refresh_token: str)",
        ),
        (
            AUTH_METHOD_USER_ACCOUNT,
            ("invalid_user_id", MOCK_REFRESH_TOKEN),
            "provide a tuple with (user_id: int, refresh_token: str)",
        ),
        (
            AUTH_METHOD_SERVICE_ACCOUNT,
            (MOCK_CLIENT_ID,),
            "provide a tuple with (client_id: str, client_secret: str)",
        ),
        (
            "invalid_method",
            (MOCK_USER_ID, MOCK_REFRESH_TOKEN),
            "auth_method must be 'user_account', 'service_account', or 'bearer_token'",
        ),
    ],
)
def test_sdk_invalid_initialization(auth_method, auth_params, expected_error_message_part):
    """Test invalid SDK initialization scenarios."""
    with pytest.raises(ValueError) as excinfo:
        AlationAIAgentSDK(
            base_url=MOCK_BASE_URL,
            auth_method=auth_method,
            auth_params=auth_params,
            dist_version="test-dist-version",
        )
    assert expected_error_message_part in str(excinfo.value)


@pytest.mark.parametrize(
    "auth_method, auth_params, side_effect, expected_token_valid_calls",
    [
        (
            AUTH_METHOD_USER_ACCOUNT,
            UserAccountAuthParams(MOCK_USER_ID, MOCK_REFRESH_TOKEN),
            [True, False, True],
            2,
        ),
        (
            AUTH_METHOD_SERVICE_ACCOUNT,
            ServiceAccountAuthParams(MOCK_CLIENT_ID, MOCK_CLIENT_SECRET),
            [True, False, True],
            2,
        ),
    ],
)
def test_token_reuse_and_refresh(
    mock_requests_post,
    mock_requests_get,
    auth_method,
    auth_params,
    side_effect,
    expected_token_valid_calls,
):
    """Test token reuse and refresh for both auth methods."""
    mock_requests_post("createAPIAccessToken", response_json=REFRESH_TOKEN_RESPONSE_SUCCESS)
    mock_requests_post("oauth/v2/token", response_json=JWT_RESPONSE_SUCCESS)
    mock_requests_get("license", response_json={"is_cloud": True})
    mock_requests_get("full_version", response_json={"ALATION_RELEASE_NAME": "2025.1.2"})
    mock_requests_get("context/", response_json=CONTEXT_RESPONSE_SUCCESS)

    sdk = AlationAIAgentSDK(
        base_url=MOCK_BASE_URL,
        auth_method=auth_method,
        auth_params=auth_params,
        dist_version="test-dist-version",
    )
    sdk.api.access_token = "mock-access-token"  # Ensure access_token is set

    with patch.object(
        sdk.api,
        "_token_is_valid_on_server",
        side_effect=side_effect,
    ) as mock_token_valid, patch.object(
        sdk.api,
        "_generate_new_token",
        wraps=sdk.api._generate_new_token,
    ) as spy_generate_token:
        sdk.get_context("first question")  # Valid token reused
        sdk.get_context("second question")  # Token refreshed

        assert mock_token_valid.call_count == expected_token_valid_calls
        assert spy_generate_token.call_count == 1


def test_error_handling_in_token_validation(mock_requests_post):
    """Test that errors in token validation raise AlationAPIError."""
    mock_requests_post("createAPIAccessToken", response_json=REFRESH_TOKEN_RESPONSE_SUCCESS)

    sdk = AlationAIAgentSDK(
        base_url=MOCK_BASE_URL,
        auth_method=AUTH_METHOD_USER_ACCOUNT,
        auth_params=UserAccountAuthParams(MOCK_USER_ID, MOCK_REFRESH_TOKEN),
        dist_version="test-dist-version",
    )

    with patch.object(
        sdk.api,
        "_is_access_token_valid",
        side_effect=AlationAPIError("Mocked error in access token validation"),
    ) as mock_access_token_valid:
        with pytest.raises(AlationAPIError, match="Mocked error in access token validation"):
            sdk.api._is_access_token_valid()
        mock_access_token_valid.assert_called_once()

    with patch.object(
        sdk.api,
        "_is_jwt_token_valid",
        side_effect=AlationAPIError("Mocked error in JWT token validation"),
    ) as mock_jwt_token_valid:
        with pytest.raises(AlationAPIError, match="Mocked error in JWT token validation"):
            sdk.api._is_jwt_token_valid()
        mock_jwt_token_valid.assert_called_once()

def test_lineage_beta_tools_disabled_by_default(
    mock_requests_get,
    mock_requests_post,
):
    mock_requests_post("createAPIAccessToken", response_json=REFRESH_TOKEN_RESPONSE_SUCCESS)
    mock_requests_post("oauth/v2/token", response_json=JWT_RESPONSE_SUCCESS)
    mock_requests_get("license", response_json={"is_cloud": True})
    mock_requests_get("full_version", response_json={"ALATION_RELEASE_NAME": "2025.1.2"})

    sdk = AlationAIAgentSDK(
        base_url=MOCK_BASE_URL,
        auth_method=AUTH_METHOD_USER_ACCOUNT,
        auth_params=UserAccountAuthParams(MOCK_USER_ID, MOCK_REFRESH_TOKEN),
    )
    assert AlationTools.LINEAGE not in sdk.enabled_beta_tools

def test_check_job_status_tool_explicitly_disabled(
    mock_requests_get,
    mock_requests_post,
):
    mock_requests_post("createAPIAccessToken", response_json=REFRESH_TOKEN_RESPONSE_SUCCESS)
    mock_requests_post("oauth/v2/token", response_json=JWT_RESPONSE_SUCCESS)
    mock_requests_get("license", response_json={"is_cloud": True})
    mock_requests_get("full_version", response_json={"ALATION_RELEASE_NAME": "2025.1.2"})

    sdk = AlationAIAgentSDK(
        base_url=MOCK_BASE_URL,
        auth_method=AUTH_METHOD_USER_ACCOUNT,
        auth_params=UserAccountAuthParams(MOCK_USER_ID, MOCK_REFRESH_TOKEN),
        disabled_tools={AlationTools.CHECK_JOB_STATUS}
    )
    assert AlationTools.CHECK_JOB_STATUS in sdk.disabled_tools
    assert sdk.check_job_status not in sdk.get_tools()

