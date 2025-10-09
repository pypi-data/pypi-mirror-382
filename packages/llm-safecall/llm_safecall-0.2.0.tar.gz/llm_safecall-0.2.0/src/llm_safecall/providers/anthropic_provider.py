from .base import ProviderResponse
from typing import Iterable

class AnthropicProvider:
    """Thin adapter around anthropic>=0.34."""
    def __init__(self, model: str = "claude-3-5-sonnet-20240620", api_key: str | None = None):
        self.model = model
        self.api_key = api_key

    def _client(self):
        try:
            import anthropic
        except Exception as e:
            raise ImportError("anthropic extra not installed: pip install 'llm-safecall[anthropic]'") from e
        return anthropic.Anthropic(api_key=self.api_key)

    def complete(self, prompt: str, **params) -> ProviderResponse:
        client = self._client()
        msg = client.messages.create(
            model=self.model,
            max_tokens=params.get("max_tokens", 512),
            temperature=params.get("temperature", 0.2),
            messages=[{"role":"user","content":prompt}],
        )
        # Anthropic SDK returns content as a list of blocks
        text = "".join(part.text for part in msg.content if getattr(part, "type", "") == "text")
        return ProviderResponse(text=text, model=self.model)

    def stream(self, prompt: str, **params) -> Iterable[str]:
        client = self._client()
        with client.messages.stream(
            model=self.model,
            max_tokens=params.get("max_tokens", 512),
            temperature=params.get("temperature", 0.2),
            messages=[{"role":"user","content":prompt}],
        ) as stream:
            for event in stream:
                if getattr(event, "type", "") == "content_block_delta":
                    yield getattr(event.delta, "text", "") or ""
