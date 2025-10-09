from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from ..client import Client

def create_completion(
    client: Client,
    *,
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **extra: Any
) -> Dict[str, Any]:
    """Create a chat completion with NanoGPT.

    Args:
        client (Client): Initialized NanoGPT client.
        model (str): The model to use, e.g. 'gpt-nano-1'.
        messages (list[dict]): List of messages for the chat, following the OpenAI schema.
        temperature (float, optional): Sampling temperature (default: 0.7).
        top_p (float, optional): Nucleus sampling cutoff (default: 1.0).
        max_tokens (int, optional): Maximum number of tokens to generate.
        stream (bool, optional): Whether to stream tokens in real-time.
        **extra: Additional parameters to pass through.

    Returns:
        dict | str: Parsed JSON response or raw text.

    Raises:
        APIError: If the API request fails.
    """
    payload = {
        'model': model,
        'messages': messages
    }
    if temperature is not None: 
        payload['temperature'] = temperature
    if top_p is not None: 
        payload['top_p'] = top_p
    if max_tokens is not None: 
        payload['max_tokens'] = max_tokens
    payload.update(extra)

    accept = 'text/event-stream' if stream else None
    return client.request('POST', '/chat/completions', json = payload, accept = accept)
