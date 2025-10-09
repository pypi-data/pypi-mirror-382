from __future__ import annotations

import requests
from typing import Any, Dict, Optional, Union, IO
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from .errors import APIError, RateLimitError, AuthError, NotFoundError
from .auth import Auth

DEFAULT_BASE_URL = 'https://nano-gpt.com/api/v1'
DEFAULT_TIMEOUT = 30

def create_session(user_agent: str) -> requests.Session:
    """Create a configured requests.Session with retries and headers."""
    session = requests.Session()
    session.headers.update({'User-Agent': user_agent, 'Accept': 'application/json'})
    retry_policy = Retry(
        total = 5,
        backoff_factor = 0.5,
        allowed_methods = ['GET', 'POST'],
        status_forcelist = [429, 500, 502, 503, 504],
        raise_on_status = False
    )
    session.mount('https://', HTTPAdapter(max_retries = retry_policy))
    session.mount('http://', HTTPAdapter(max_retries = retry_policy))
    return session

class Client:
    def __init__(
        self,
        auth: Auth,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        user_agent: str = 'nanogpt-sdk/0.1',
        session: Optional[requests.Session] = None
    ):
        """Initialize the transport.

        Args:
            auth: Authentication provider returning headers().
            base_url: API base URL.
            timeout: Default timeout in seconds.
            user_agent: User-Agent header value.
            session: Optional prebuilt session.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auth = auth
        self.session = session or create_session(user_agent)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, IO[bytes]]] = None,
        timeout: Optional[int] = None,
        accept: Optional[str] = None
    ) -> Union[Dict[str, Any], str]:
        """Send an HTTP request and map common errors.

        Args:
            method: HTTP method.
            path: API path starting with '/'.
            params: Query parameters.
            json: JSON body.
            files: Multipart form data.
            timeout: Per-call timeout override.

        Returns:
            Parsed JSON dict or raw text when not JSON.

        Raises:
            AuthError: 401.
            NotFoundError: 404.
            RateLimitError: 429.
            APIError: Other 4xx/5xx.
        """
        url = f'{self.base_url}/{path.lstrip("/")}'
        headers = {**self.auth.headers()}
        if accept:
            headers['Accept'] = accept

        response = self.session.request(
            method,
            url,
            params = params or {},
            json = json,
            files = files,
            headers = headers,
            timeout = timeout or self.timeout
        )

        if response.status_code == 401:
            raise AuthError('Unauthorized Access', 401)
        if response.status_code == 404:
            raise NotFoundError('Resource Not Found', 404)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', '1'))
            raise RateLimitError(f'Rate limit exceeded. Retry after {retry_after} seconds.', 429)

        if 400 <= response.status_code < 600:
            try:
                data = response.json()
                message = str(data.get('message') or data)
                code = str(data.get('code')) if isinstance(data, dict) and 'code' in data else None
            except Exception:
                message, code = response.text, None
            raise APIError(message, response.status_code, code)

        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json()
        
        return response.text