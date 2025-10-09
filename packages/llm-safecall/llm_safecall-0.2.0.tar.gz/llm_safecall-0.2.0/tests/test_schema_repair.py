from pydantic import BaseModel
from llm_safecall import SafeCall, MockProvider

class FlightPlan(BaseModel):
    origin: str
    destination: str
    depart_date: str
    airline: str | None = None

def test_auto_repair_to_valid_json():
    safe = SafeCall(MockProvider(), output=FlightPlan)
    result = safe.generate("Return a flight plan as JSON for Berlin -> Tokyo")
    assert result.origin == "Berlin"
