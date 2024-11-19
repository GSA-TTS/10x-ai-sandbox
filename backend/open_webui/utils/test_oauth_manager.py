import pytest
import logging
from fastapi import Request
from fastapi.datastructures import URL
from starlette.datastructures import Headers, QueryParams
from starlette.responses import RedirectResponse
from unittest.mock import patch, AsyncMock, MagicMock
from urllib.parse import urlparse, parse_qs
import json

from authlib.integrations.starlette_client import OAuth
from open_webui.utils.oauth import OAuthManager, OAUTH_PROVIDERS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_request():
    async def receive():
        return {"type": "http.request"}

    headers = Headers({"host": "testserver"})
    query_params = QueryParams({})
    url = URL("http://testserver/test/path")
    request = AsyncMock(
        spec=Request,
        receive=receive,
        headers=headers,
        query_params=query_params,
        url=url,
    )
    request.url_for = AsyncMock(return_value=url)
    return request


@pytest.mark.asyncio
async def test_handle_login(mock_request):
    # Set up a test OAuth provider configuration
    test_provider_config = {
        "oidc": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "server_metadata_url": "https://uaa.fr.cloud.gov/.well-known/openid-configuration",
            "scope": "openid profile email",
            "redirect_uri": "http://localhost/oauth/oidc/callback",
        }
    }

    # Mock the server metadata response
    mock_metadata = {
        "issuer": "https://uaa.fr.cloud.gov",
        "authorization_endpoint": "https://uaa.fr.cloud.gov/oauth/authorize",
        "token_endpoint": "https://uaa.fr.cloud.gov/oauth/token",
        "userinfo_endpoint": "https://uaa.fr.cloud.gov/userinfo",
        "jwks_uri": "https://uaa.fr.cloud.gov/token_keys",
        "scopes_supported": ["openid", "profile", "email"],
        "response_types_supported": ["code", "token", "id_token"],
        "grant_types_supported": ["authorization_code", "implicit"],
    }

    with patch.dict(OAUTH_PROVIDERS, test_provider_config):
        oauth_manager = OAuthManager()

        # Patch the OAuth.create_client method to return a client that we can inspect
        with (
            patch.object(OAuth, "create_client") as mock_create_client,
            patch("aiohttp.ClientSession.get") as mock_get,
        ):

            # Mock the HTTP request to the metadata URL
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_metadata
            mock_get.return_value.__aenter__.return_value = mock_response

            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client

            # Set up the mock client's authorize_redirect method
            async def mock_authorize_redirect(request, redirect_uri):
                auth_url = mock_metadata["authorization_endpoint"]
                params = {
                    "response_type": "code",
                    "client_id": "test_client_id",
                    "redirect_uri": redirect_uri,
                    "scope": "openid profile email",
                    "state": "some_state_value",
                }
                query_string = "&".join(f"{k}={v}" for k, v in params.items())
                full_url = f"{auth_url}?{query_string}"
                return RedirectResponse(url=full_url)

            mock_client.authorize_redirect = mock_authorize_redirect

            # Call the handle_login method
            redirect_response = await oauth_manager.handle_login("oidc", mock_request)

            # Log the redirect response
            logger.info("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
            logger.info(f"Redirect location: {redirect_response.headers['location']}")
            logger.info("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

            # Assert that we got a RedirectResponse
            assert isinstance(redirect_response, RedirectResponse)
            assert redirect_response.status_code == 307  # Temporary Redirect

            # Parse the URL from the response
            parsed_url = urlparse(redirect_response.headers["location"])
            query_params = parse_qs(parsed_url.query)

            # Assert on the components of the URL
            assert parsed_url.scheme == "https"
            assert parsed_url.netloc == "uaa.fr.cloud.gov"
            assert parsed_url.path == "/oauth/authorize"

            # Assert on the query parameters
            assert query_params["response_type"] == ["code"]
            assert query_params["client_id"] == ["test_client_id"]
            assert query_params["redirect_uri"] == [
                "http://localhost/oauth/oidc/callback"
            ]
            assert query_params["scope"] == ["openid profile email"]
            assert "state" in query_params
