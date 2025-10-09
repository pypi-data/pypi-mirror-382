from __future__ import annotations
from typing import Any, Dict, Optional
from ..client import Client

def generate_image(client: Client, *, prompt: str, model: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
    """Generate an image from a text prompt.

    Args:
        client (Client): Initialized NanoGPT client.
        prompt (str): Text description of the desired image.
        model (str, optional): Image model to use. Defaults to None.
        **extra: Additional request parameters, for example size or steps.

    Returns:
        dict: Parsed JSON response with image data or URLs.

    Raises:
        APIError: On HTTP or API errors.
    """
    payload = {'prompt': prompt}
    if model is not None:
        payload['model'] = model

    payload.update(extra)
    return client.request('POST', '/images/generations', json = payload)
