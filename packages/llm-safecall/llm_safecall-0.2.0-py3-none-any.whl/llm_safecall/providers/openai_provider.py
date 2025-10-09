from .base import ProviderResponse
from typing import Iterable

class OpenAIProvider:
    """Thin adapter around openai>=1.x. Imported lazily so package works without the extra."""
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        self.model = model
        self.api_key = api_key

    def _client(self):
        try:
            from openai import OpenAI
        except Exception as e:
            raise ImportError("openai extra not installed: pip install 'llm-safecall[openai]'") from e
        return OpenAI(api_key=self.api_key)

    def complete(self, prompt: str, **params) -> ProviderResponse:
        client = self._client()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role":"user","content":prompt}],
            temperature=params.get("temperature", 0.2),
            max_tokens=params.get("max_tokens", 512),
            timeout=params.get("timeout_s", None),
        )
        text = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", None)
        output_tokens = getattr(usage, "completion_tokens", None)
        return ProviderResponse(text=text, input_tokens=input_tokens, output_tokens=output_tokens, model=self.model, cost=None)

    def stream(self, prompt: str, **params) -> Iterable[str]:
        client = self._client()
        stream = client.chat.completions.create(
            model=self.model,
            messages=[{"role":"user","content":prompt}],
            stream=True,
            temperature=params.get("temperature", 0.2),
            max_tokens=params.get("max_tokens", 512),
        )
        buf = []
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            buf.append(delta)
            yield delta
