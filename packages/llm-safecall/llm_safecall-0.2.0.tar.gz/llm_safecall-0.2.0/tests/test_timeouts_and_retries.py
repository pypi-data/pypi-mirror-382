import pytest
from llm_safecall import SafeCall, MockProvider
from llm_safecall.errors import CircuitOpenError

class FlakyProvider(MockProvider):
    def __init__(self):
        super().__init__()
        self.calls = 0
    def complete(self, prompt: str, **params):
        self.calls += 1
        if self.calls < 2:
            raise TimeoutError("simulated timeout")
        return super().complete(prompt, **params)

def test_retries_and_circuit_breaker():
    safe = SafeCall(FlakyProvider())
    # First call times out once then succeeds
    txt = safe.generate("hello")
    assert "Mock response" in txt
    # Force open the circuit
    safe.circuit.record_failure(); safe.circuit.record_failure(); safe.circuit.record_failure()
    safe.circuit.record_failure(); safe.circuit.record_failure()
    with pytest.raises(CircuitOpenError):
        safe.generate("blocked")
