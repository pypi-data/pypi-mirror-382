# NanoGPT SDK

A clean Python client for the [NanoGPT](https://docs.nano-gpt.com/introduction) API. 

Supports text completions, chat completions, image and video generation, and model listing.

## Installation

```
pip install nanogpt-sdk
```

## Quickstart

```python
from nanogpt import Client, BearerAuth, endpoints

# Initialize
client = Client(BearerAuth('YOUR_API_KEY'))

# Create a chat completion
response = endpoints.chat.create_completion(
    client,
    model = 'gpt-nano-1',
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Why is the sky blue?'}
    ],
    temperature = 0.7,
    max_tokens = 256
)

# Print generated text
print(response['choices'][0]['message']['content'])
```

## Endpoints

| Module                | Description                          |
| --------------------- | ------------------------------------ |
| `endpoints.chat`  | Create chat completions (OpenAI-style message schema) |
| `endpoints.completions`      | Generate free-form text completions          |
| `endpoints.models` | List available public or subscription models          |
| `endpoints.images`    | Generate images from text prompts  |
| `endpoints.videos` | Generate videos from text prompts             |

## Development

```
git clone https://github.com/kalenmcmillan/nanogpt-sdk.git
cd nanogpt-sdk
python -m pip install -e .
pytest
```
## License

MIT License © 2025 Kalen McMillan