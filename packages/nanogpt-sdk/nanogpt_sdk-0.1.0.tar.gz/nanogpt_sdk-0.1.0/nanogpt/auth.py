from typing import Dict

class Auth:
    """Base class for authentication providers."""
    def headers(self) -> Dict[str, str]:
        """Return headers to add to each request."""
        return {}

class BearerAuth(Auth):
    """Bearer token authentication.

    Args:
        token: API token for QuizGecko.
    """
    def __init__(self, token: str):
        self.token = token

    def headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.token}'}