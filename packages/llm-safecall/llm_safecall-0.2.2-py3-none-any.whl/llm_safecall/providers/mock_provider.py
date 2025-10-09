from collections.abc import Iterable
from typing import Any

from .base import ProviderResponse

CHARS_PER_TOKEN = 4
MAX_ECHO_LEN = 200


class MockProvider:
    """Offline provider for tests.

    Deterministic echoes with a tiny "AI":
    - If the prompt contains 'Repair this to valid', returns a fixed JSON.
    - Else, if the prompt hints at JSON, returns a trivial malformed JSON payload.
    - Otherwise, returns an echo-style response.
    """

    def __init__(self, model: str = "mock-1") -> None:
        self.model = model

    def complete(self, prompt: str, **params: Any) -> ProviderResponse:
        text = self._respond(prompt)
        return ProviderResponse(
            text=text,
            input_tokens=len(prompt) // CHARS_PER_TOKEN,
            output_tokens=len(text) // CHARS_PER_TOKEN,
            model=self.model,
            cost=0.0,
        )

    def stream(self, prompt: str, **params: Any) -> Iterable[str]:
        yield self._respond(prompt)

    def _respond(self, prompt: str) -> str:
        if "Repair this to valid" in prompt:
            # Return minimal valid JSON for tests
            return (
                '{"origin":"Berlin","destination":"Tokyo",'
                '"depart_date":"2025-11-01","airline":null}'
            )

        # Naive hint: if 'as JSON' appears, return slightly malformed JSON occasionally
        if "as JSON" in prompt:
            return "{origin:'Berlin', destination:'Tokyo', depart_date:'2025-11-01'}"

        # Default echo-ish
        return "Mock response: " + prompt[:MAX_ECHO_LEN]
