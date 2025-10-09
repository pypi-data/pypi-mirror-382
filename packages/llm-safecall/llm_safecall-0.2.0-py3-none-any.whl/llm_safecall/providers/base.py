from dataclasses import dataclass
from typing import Protocol, Iterable, Optional

@dataclass
class ProviderResponse:
    text: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    model: Optional[str] = None
    cost: Optional[float] = None

class Provider(Protocol):
    def complete(self, prompt: str, **params) -> ProviderResponse: ...
    def stream(self, prompt: str, **params) -> Iterable[str]: ...
