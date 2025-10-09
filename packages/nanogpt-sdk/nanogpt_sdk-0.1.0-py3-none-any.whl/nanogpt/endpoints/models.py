from __future__ import annotations
from typing import Any, Dict
from ..client import Client

def list_all(client: Client) -> Dict[str, Any]:
    """List all public models.

    Args:
        client (Client): Initialized NanoGPT client.

    Returns:
        dict: Parsed JSON response containing model entries.

    Raises:
        APIError: On HTTP or API errors.
    """
    return client.request('GET', '/models')

def list_subscription(client: Client, *, detailed: bool = False) -> Dict[str, Any]:
    """List models available to the current subscription.

    Args:
        client (Client): Initialized NanoGPT client.
        detailed (bool, optional): Return extended fields when true. Defaults to False.

    Returns:
        dict: Parsed JSON response containing subscription model entries.

    Raises:
        APIError: On HTTP or API errors.
    """
    params = {}
    if detailed:
        params['detailed'] = True

    return client.request('GET', '/subscription/v1/models', params = params)
