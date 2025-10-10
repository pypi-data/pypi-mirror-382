import datetime

import google.auth.credentials
import google.auth.transport.requests
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class RefreshTokenResponse:
    """
    Response object containing OAuth 2.0 token and expiration information.
    """

    def __init__(self, access_token: str, expires_at: datetime.datetime):
        """
        Initialize the RefreshTokenResponse.

        Args:
            access_token: OAuth 2.0 token
            expires_at: Token's expiration time
        """
        self.access_token = access_token
        self.expires_at = expires_at


class OIDCDiscoveryMetadata:
    """
    Represents OIDC discovery metadata.
    """

    def __init__(self, discovery_document: dict):
        self._document = discovery_document

    @property
    def token_endpoint(self) -> str:
        return self._document["token_endpoint"]


def fetch_oidc_discovery(issuer_url: str) -> OIDCDiscoveryMetadata:
    """
    Fetches OIDC discovery metadata from the provider.

    This function makes a network request to the OIDC provider's discovery endpoint
    to retrieve the provider's metadata including the token endpoint.

    Args:
        issuer_url: The base URL of the OIDC provider.

    Returns:
        OIDCDiscoveryMetadata containing the discovered endpoints.

    Raises:
        requests.exceptions.RequestException: If the discovery document cannot be retrieved.
        ValueError: If the response is not valid JSON.
    """
    discovery_url = f"{issuer_url.rstrip('/')}/.well-known/openid-configuration"
    response = requests.get(discovery_url, timeout=10)
    response.raise_for_status()
    config = response.json()

    return OIDCDiscoveryMetadata(config)


class OAuth2ClientCredentials:
    """
    OAuth2ClientCredentials class for handling the OAuth 2.0 Client Credentials flow.

    Integrates with the google-auth and requests-oauthlib library to fetch an access token
    from a specified token endpoint with automatic refreshing.

    This class only accepts a direct token URL. For OIDC discovery, use the
    fetch_oidc_discovery function to obtain the token endpoint first.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_endpoint: str,
    ):
        """
        Initializes the OAuth2ClientCredentials.

        Args:
            client_id: The client ID for the application.
            client_secret: The client secret for the application.
            token_endpoint: The direct token endpoint URL.
        """
        self._token_endpoint = token_endpoint
        self._client_id = client_id
        self._client_secret = client_secret

        client = BackendApplicationClient(client_id=self._client_id)
        self._session = OAuth2Session(client=client)

        self._token = None
        self._expiry = None

    def get_token(self, force_refresh: bool = False) -> RefreshTokenResponse:
        """
        Get a valid access token, refreshing if necessary or forced.

        Args:
            force_refresh: If True, forces token refresh regardless of expiry.

        Returns:
            RefreshTokenResponse object containing access_token and expires_at.
        """
        current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        if (
            force_refresh
            or self._token is None
            or self._expiry is None
            or self._expiry <= current_time + datetime.timedelta(seconds=300)
        ):
            # Refresh the token
            token_data = self._session.fetch_token(
                token_url=self._token_endpoint,
                client_id=self._client_id,
                client_secret=self._client_secret,
            )

            self._token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 0)
            self._expiry = current_time + datetime.timedelta(seconds=expires_in)

        return RefreshTokenResponse(access_token=self._token, expires_at=self._expiry)


class GoogleOAuth2ClientCredentials(google.auth.credentials.Credentials):
    """
    Adapter class that implements google.auth.credentials.Credentials interface
    for OAuth2ClientCredentials.
    """

    def __init__(self, credentials: OAuth2ClientCredentials):
        """
        Initialize the credentials adapter.

        Args:
            credentials: The OAuth2ClientCredentials instance to adapt.
        """
        self._credentials = credentials
        super().__init__()

    @property
    def token(self) -> str:
        return self._credentials._token

    @token.setter
    def token(self, value: str) -> None:
        self._credentials._token = value

    @property
    def expiry(self) -> datetime.datetime:
        return self._credentials._expiry

    @expiry.setter
    def expiry(self, value: datetime.datetime) -> None:
        self._credentials._expiry = value

    def refresh(self, request: google.auth.transport.requests.Request) -> None:
        self._credentials.get_token(force_refresh=True)


class AuthRequest(requests.auth.AuthBase):
    def __init__(self, credentials: OAuth2ClientCredentials):
        """
        Args:
            credentials: The OAuth2ClientCredentials instance to use for auth.
        """
        self.credentials = credentials

    def __call__(self, r):
        """
        Apply OAuth2 auth to the request.

        This method is called automatically by requests to add auth
        headers to the request.

        Args:
            r: The request object to modify.

        Returns:
            The modified request object with auth headers.
        """
        # Get latest token
        token_response = self.credentials.get_token()

        # Add Bearer token to the auth header
        r.headers["Authorization"] = f"Bearer {token_response.access_token}"

        return r


def oauth2_auth_request(credentials: OAuth2ClientCredentials) -> requests.auth.AuthBase:
    """
    Create a requests-compatible OAuth2 auth handler.

    This function creates an auth handler that can be used with
    the requests library, similar to how oauth2_call_credentials creates
    gRPC call credentials.

    Args:
        credentials: An OAuth2ClientCredentials instance.

    Returns:
        AuthRequest: An auth handler that can be used with requests.
    """
    return AuthRequest(credentials)
