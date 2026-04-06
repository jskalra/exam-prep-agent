"""
LLM abstraction layer.
Swap between Claude API and local Ollama by changing LLM_PROVIDER in .env
"""

import os
import anthropic
import json

# Future: set LLM_PROVIDER=ollama to use local model
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

_client = None


def get_client():
    global _client
    if _client is None:
        if LLM_PROVIDER == "claude":
            _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Future: elif LLM_PROVIDER == "ollama": ...
    return _client


def chat(system: str, messages: list, max_tokens: int = 1024, stream: bool = False):
    """
    Unified chat call. Returns text string.
    stream=True returns a generator of text chunks (for Streamlit streaming).
    """
    client = get_client()

    if LLM_PROVIDER == "claude":
        if stream:
            return _claude_stream(client, system, messages, max_tokens)
        else:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            return response.content[0].text
    else:
        raise NotImplementedError(f"Provider {LLM_PROVIDER} not yet implemented")


def chat_json(system: str, messages: list, max_tokens: int = 1024) -> dict:
    """Call LLM and parse JSON response. Raises ValueError if not valid JSON."""
    raw = chat(system, messages, max_tokens=max_tokens, stream=False)
    # Strip markdown code fences if present
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw response: {raw}")


def _claude_stream(client, system: str, messages: list, max_tokens: int):
    """Generator that yields text chunks for Streamlit st.write_stream."""
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
