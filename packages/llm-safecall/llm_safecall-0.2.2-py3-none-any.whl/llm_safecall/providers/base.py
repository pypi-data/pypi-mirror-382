from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProviderResponse:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    model: str | None = None
    cost: float | None = None


class Provider(Protocol):
    def complete(self, prompt: str, **params) -> ProviderResponse: ...
    def stream(self, prompt: str, **params) -> Iterable[str]: ...
