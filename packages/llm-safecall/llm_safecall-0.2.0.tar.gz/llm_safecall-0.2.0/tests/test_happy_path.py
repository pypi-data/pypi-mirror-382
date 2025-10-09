from pydantic import BaseModel
from llm_safecall import SafeCall, MockProvider

class FlightPlan(BaseModel):
    origin: str
    destination: str
    depart_date: str
    airline: str | None = None

def test_happy_path_validation_and_report():
    safe = SafeCall(MockProvider(), output=FlightPlan, temperature=0.1)
    result = safe.generate("Plan a cheap flight from Berlin to Tokyo next month as JSON.")
    assert isinstance(result, FlightPlan)
    assert result.origin.lower() == "berlin"
    assert hasattr(result, "_report")
    rep = result._report.model_dump()
    assert "latency_ms" in rep
