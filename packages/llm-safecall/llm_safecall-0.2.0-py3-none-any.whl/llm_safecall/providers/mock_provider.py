from .base import ProviderResponse
from typing import Iterable

class MockProvider:
    """Offline provider for tests; deterministic echoes with tiny 'AI'.
    - If prompt contains 'Repair this to valid', returns a fixed JSON.
    - Else, if prompt hints at JSON, returns a trivial JSON payload.
    """
    def __init__(self, model: str = "mock-1"):
        self.model = model

    def complete(self, prompt: str, **params) -> ProviderResponse:
        text = self._respond(prompt)
        return ProviderResponse(text=text, input_tokens=len(prompt)//4, output_tokens=len(text)//4, model=self.model, cost=0.0)

    def stream(self, prompt: str, **params) -> Iterable[str]:
        yield self._respond(prompt)

    def _respond(self, prompt: str) -> str:
        if "Repair this to valid" in prompt:
            # Return minimal valid JSON for tests
            return '{"origin":"Berlin","destination":"Tokyo","depart_date":"2025-11-01","airline":null}'
        # naive hint: if 'as JSON' appears, return slightly malformed JSON once in a while
        if "as JSON" in prompt:
            return "{origin:'Berlin', destination:'Tokyo', depart_date:'2025-11-01'}"
        # default echo-ish
        return "Mock response: " + prompt[:200]
