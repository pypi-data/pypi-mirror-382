import time
from .errors import RateLimitExceededError

class TokenBucket:
    def __init__(self, rate_per_sec: float, capacity: float | None = None):
        self.rate = rate_per_sec
        self.capacity = capacity or rate_per_sec
        self.tokens = self.capacity
        self.last = time.time()

    def take(self, cost: float = 1.0):
        now = time.time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens < cost:
            raise RateLimitExceededError("Rate limit exceeded")
        self.tokens -= cost
