class ModerationError(Exception):
    pass

class CircuitOpenError(Exception):
    pass

class PolicyViolationError(Exception):
    """Raised when org policy or guardrails are violated."""
    def __init__(self, message: str, data: dict | None = None):
        super().__init__(message)
        self.data = data or {}

class BudgetExceededError(Exception):
    pass

class RateLimitExceededError(Exception):
    pass
