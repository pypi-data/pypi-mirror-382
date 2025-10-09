from __future__ import annotations
from typing import Any, Dict, Optional
from ..client import Client

def generate_video(client: Client, *, prompt: str, model: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
    """Generate a video from a text prompt.

    Args:
        client (Client): Initialized NanoGPT client.
        prompt (str): Text description of the desired video.
        model (str, optional): Video model to use. Defaults to None.
        **extra: Additional request parameters, for example duration or fps.

    Returns:
        dict: Parsed JSON response with video data or URLs.

    Raises:
        APIError: On HTTP or API errors.
    """
    payload = {'prompt': prompt}
    if model is not None:
        payload['model'] = model

    payload.update(extra)
    return client.request('POST', '/videos/generations', json = payload)
