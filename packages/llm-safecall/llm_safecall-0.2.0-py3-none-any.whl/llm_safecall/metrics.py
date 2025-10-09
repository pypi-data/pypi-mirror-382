from dataclasses import dataclass, field
from contextlib import contextmanager
import time

@dataclass
class CallReport:
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    model: str | None = None
    cost_estimate: float | None = None

    def model_dump(self) -> dict:
        return {
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "model": self.model,
            "cost_estimate": self.cost_estimate,
        }

@contextmanager
def time_it():
    start = time.perf_counter()
    yield type("Elapsed", (), {"elapsed_ms": int((time.perf_counter() - start) * 1000)})
