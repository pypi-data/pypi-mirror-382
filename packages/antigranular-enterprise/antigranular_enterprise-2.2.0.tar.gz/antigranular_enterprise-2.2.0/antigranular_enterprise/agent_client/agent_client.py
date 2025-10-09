import json
import jwt
import time
import requests
from ..config.config import config
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class AGClient:
    """
    Class to test AGClient when the AG Server with Oblv server is not available. 
    Instead using AG private python server directly(passing custom x_oblv_name headers).
    """
    def __init__(
        self,
        URL,
        PORT,
        headers=None,
    ):
        """Initialize low-level AG HTTP client with dynamic auth header support.

        Args:
            URL (str): Base host (scheme+host) e.g. http://localhost
            PORT (str): Port as string
            headers (dict|None): Initial headers (may contain external gateway token and/or internal token)
        """
        self.url = URL
        self.port = PORT
        self.base_url = URL + ":" + PORT
        self.session = requests.Session()

        # Dynamic header names aligned with higher-level clients (standard: client_auth_header / oblv_auth_header)
        self.client_auth_header = (
            getattr(config, 'CLIENT_AUTH_HEADER', None)
            or 'Authorization'
        )
        self.oblv_auth_header = (
            getattr(config, 'OBLV_AUTH_HEADER', None)
            or 'X-Authorization'
        )

        if headers:
            self.session.headers.update(headers)

    def update_headers(self, headers):
        self.session.headers.update(headers)

    def get(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "GET", endpoint, data=data, json=json, params=params, headers=headers
        )

    def post(self, endpoint, data=None, json=None, params=None, headers=None, files=None):
        return self._make_request(
            "POST", endpoint, data=data, json=json, params=params, headers=headers, files=files
        )

    def put(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "PUT", endpoint, data=data, json=json, params=params, headers=headers
        )

    def delete(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "DELETE", endpoint, data=data, json=json, params=params, headers=headers
        )
    
    def __is_token_expired(self) -> bool:
        """Check expiry of the internal (exchanged) access token.

        Returns True if missing or expired so that a refresh can be attempted.
        """
        try:
            token_with_prefix = self.session.headers.get(self.oblv_auth_header, '')
            if not token_with_prefix:
                # If we don't yet have an internal token, treat as expired so upstream can obtain one.
                return True
            raw = token_with_prefix.split('Bearer ')[-1].strip()
            if not raw:
                return True
            payload = jwt.decode(raw, options={"verify_signature": False})
            current_time = time.time() + 10  # small buffer
            return payload.get('exp', 0) < current_time
        except Exception:
            # On decode issues, force refresh attempt
            return True

    def __get_refresh_token(self) -> None:
        """Refresh internal (oblv) access token if expired.

        Preserves external gateway token (stored under client_gw_auth_header) while
        updating internal token (under oblv_gw_auth_header) and refresh_token header.
        """
        try:
            # Only attempt if we already have a refresh token
            if not self.session.headers.get('refresh_token'):
                return
            if not self.__is_token_expired():
                return
            res = requests.post(
                config.AGENT_CONSOLE_URL + "/jupyter/token/refresh",
                json={"refresh_token": self.session.headers.get('refresh_token')},
            )
            res.raise_for_status()
            data = res.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            if access_token:
                self.session.headers[self.oblv_auth_header] = f"Bearer {access_token}"
            if refresh_token:
                self.session.headers['refresh_token'] = refresh_token
        except Exception:
            raise ConnectionError("Error while refreshing token")

    def _make_request(
        self, method, endpoint, data=None, json=None, params=None, headers=None, files=None
    ):
        # Refresh only based on internal token header presence
        if self.session.headers.get(self.oblv_auth_header):
            self.__get_refresh_token()
        url = endpoint
        verify = True
        if hasattr(config, 'TLS_ENABLED'):
            verify = config.TLS_ENABLED.lower() == "true"
            if not verify:
                urllib3.disable_warnings(InsecureRequestWarning)
        if headers:
            with self.session as s:
                s.headers.update(headers)
                response = s.request(method, url, data=data, json=json, params=params, files=files, verify=verify)
                s.headers.update(self.session.headers)
        else:
            response = self.session.request(
                method, url, data=data, json=json, params=params, verify=verify
            )
        return response


def get_ag_client():
    """
    Connect to AG server Server and initialize the Oblv client, AG server Server URL and port from config.
    """
    return AGClient(
        config.AGENT_JUPYTER_URL,
        config.AGENT_JUPYTER_PORT,
    )
