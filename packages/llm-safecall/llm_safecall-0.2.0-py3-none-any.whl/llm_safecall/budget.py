from __future__ import annotations
import json, time
from pathlib import Path
from typing import Optional
from .errors import BudgetExceededError

class Budget:
    """Very light daily budget tracker by model (local JSON file).
    cost unit is model-dependent; you can also treat it as 'token-units'."""

    def __init__(self, path: str | Path = ".llm_safecall_budget.json", daily_limit: float = float("inf")):
        self.path = Path(path)
        self.daily_limit = daily_limit
        if not self.path.exists():
            self.path.write_text(json.dumps({}), encoding="utf-8")

    def _today_key(self) -> str:
        return time.strftime("%Y-%m-%d")

    def add(self, model: str | None, amount: float):
        day = self._today_key()
        data = json.loads(self.path.read_text() or "{}")
        day_tot = data.get(day, 0.0)
        if day_tot + amount > self.daily_limit:
            raise BudgetExceededError(f"Daily budget exceeded: {day_tot + amount} > {self.daily_limit}")
        data[day] = day_tot + amount
        self.path.write_text(json.dumps(data), encoding="utf-8")
