from __future__ import annotations
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
from typing import Iterable
from .providers.base import Provider
from .moderation import check_input, check_output
from .redact import redact_text
from .metrics import CallReport, time_it
from .cache import Cache
from .errors import CircuitOpenError, PolicyViolationError
from .policy import PolicyEngine, PolicyConfig
from .budget import Budget
from .rate_limit import TokenBucket
from .ids import new_call_id
from .logger import log_json

class LLMText(str):
    """str subclass that can carry attributes like `._report`."""
    def __new__(cls, value: str):
        return super().__new__(cls, value)

def _attach_report(result, report):
    if isinstance(result, str) and not isinstance(result, LLMText):
        result = LLMText(result)
    setattr(result, "_report", report)
    return result

class _CompatCircuit:
    def __init__(self, parent): self._p = parent
    def record_success(self): self._p._record_success()
    def record_failure(self): self._p._record_failure()

class SafeCall:
    def __init__(
        self,
        llm: Provider,
        output: type[BaseModel] | None = None,
        moderation: bool = True,
        timeout_s: int = 20,
        retries: int = 2,
        redact: list[str] | None = None,
        cache: Cache | None = None,
        policy: PolicyEngine | None = None,
        budget: Budget | None = None,
        rate_limit: TokenBucket | None = None,
        org_name: str | None = None,
        fail_safe: bool = False,
        fail_safe_return: str = "",
        **params,
    ):
        self.llm, self.output, self.moderation = llm, output, moderation
        self.timeout_s, self.retries, self.params = timeout_s, retries, params
        self.redactors = redact or []
        self.cache = cache or Cache()
        self.circuit_failures = 0
        self.circuit_threshold = 5
        self.policy = policy or PolicyEngine(PolicyConfig())
        self.budget = budget
        self.rate_limit = rate_limit
        self.org_name = org_name
        self.fail_safe = fail_safe
        self.fail_safe_return = fail_safe_return
        self.circuit = _CompatCircuit(self)

    def _circuit_open(self) -> bool:
        return self.circuit_failures >= self.circuit_threshold

    def _record_success(self):
        self.circuit_failures = 0

    def _record_failure(self):
        self.circuit_failures += 1

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(1, 4))
    def _call(self, prompt: str) -> str:
        return self.llm.complete(prompt, timeout_s=self.timeout_s, **self.params).text

    def generate(self, prompt: str):
        call_id = new_call_id()
        if self._circuit_open():
            raise CircuitOpenError("Circuit is open due to recent failures.")

        # Rate limit
        if self.rate_limit:
            self.rate_limit.take(1.0)

        # Moderation & policy on input
        cleaned = redact_text(prompt, self.redactors)
        if self.moderation:
            check_input(cleaned)
        cleaned = self.policy.pre_call(cleaned)

        # Cache
        key = self.cache.key(cleaned, self.params, self.output) if self.cache else None
        if self.cache and (hit := self.cache.get(key)):
            log_json("cache_hit", call_id=call_id)
            return hit

        with time_it() as t:
            try:
                log_json("llm_call_start", call_id=call_id, model=getattr(self.llm, "model", None))
                text = self._call(cleaned)
                self._record_success()
            except Exception as e:
                self._record_failure()
                log_json("llm_call_error", call_id=call_id, error=type(e).__name__)
                raise

        # Policy checks on output
        try:
            text = self.policy.post_call(text, schema_expected=bool(self.output))
        except PolicyViolationError as e:
            # One repair attempt if schema expected: ask the model to sanitize/JSONify
            if self.output:
                repair_prompt = (
                    "Sanitize and return ONLY valid JSON for the requested schema. "
                    "Remove any secrets, shell commands, or non-JSON content in your response.\n"
                    f"Previous unsafe output:\n{text}"
                )
                text = self._call(repair_prompt)
                text = self.policy.post_call(text, schema_expected=True)
            else:
                raise

        # Schema validation (and one repair attempt)
        result = text  # default passthrough
        if self.output:
            try:
                result = self.output.model_validate_json(text)
            except ValidationError:
                repair_prompt = (
                    f"Repair this to valid {self.output.__name__} JSON only. "
                    f"Respond with JSON and nothing else:\n{text}"
                )
                text = self._call(repair_prompt)
                text = self.policy.post_call(text, schema_expected=True)
                result = self.output.model_validate_json(text)

        # Budget accounting (approximate cost if we have no usage)
        report = CallReport(
            latency_ms=t.elapsed_ms,
            input_tokens=None,
            output_tokens=None,
            model=getattr(self.llm, "model", None),
            cost_estimate=None,
        )
        result = _attach_report(result, report)

        if self.budget:
            self.budget.add(report.model, 0.0)  # placeholder; provider adapters can set actual cost

        if self.cache and key:
            self.cache.set(key, result)

        log_json("llm_call_end", call_id=call_id, latency_ms=report.latency_ms)
        return result

def _generate_core(self, prompt: str):
    call_id = new_call_id()
    if self._circuit_open():
        raise CircuitOpenError("Circuit is open due to recent failures.")
    if self.rate_limit:
        self.rate_limit.take(1.0)
    cleaned = redact_text(prompt, self.redactors)
    if self.moderation:
        check_input(cleaned)
    cleaned = self.policy.pre_call(cleaned)
    key = self.cache.key(cleaned, self.params, self.output) if self.cache else None
    if self.cache and (hit := self.cache.get(key)):
        log_json("cache_hit", call_id=call_id)
        return hit, None
    with time_it() as t:
        try:
            log_json("llm_call_start", call_id=call_id, model=getattr(self.llm, "model", None))
            text = self._call(cleaned)
            self._record_success()
        except Exception as e:
            self._record_failure()
            log_json("llm_call_error", call_id=call_id, error=type(e).__name__)
            raise
    try:
        text = self.policy.post_call(text, schema_expected=bool(self.output))
    except PolicyViolationError as e:
        if self.output:
            repair_prompt = (
                "Sanitize and return ONLY valid JSON for the requested schema. "
                "Remove any secrets, shell commands, or non-JSON content in your response.\n"
                f"Previous unsafe output:\n{text}"
            )
            text = self._call(repair_prompt)
            text = self.policy.post_call(text, schema_expected=True)
        else:
            raise
    result = text
    if self.output:
        from pydantic import ValidationError
        try:
            result = self.output.model_validate_json(text)
        except ValidationError:
            repair_prompt = (
                f"Repair this to valid {self.output.__name__} JSON only. "
                f"Respond with JSON and nothing else:\n{text}"
            )
            text = self._call(repair_prompt)
            text = self.policy.post_call(text, schema_expected=True)
            result = self.output.model_validate_json(text)

    report = CallReport(
        latency_ms=t.elapsed_ms,
        input_tokens=None,
        output_tokens=None,
        model=getattr(self.llm, "model", None),
        cost_estimate=None,
    )
    result = _attach_report(result, report)
    if self.budget:
        self.budget.add(report.model, 0.0)
    if self.cache and key:
        self.cache.set(key, result)
    log_json("llm_call_end", call_id=call_id, latency_ms=report.latency_ms)
    return result, report

def generate(self, prompt: str):
    if not self.fail_safe:
        return self._generate_core(prompt)[0]
    try:
        return self._generate_core(prompt)[0]
    except Exception as _e:
        # Soft-fail path: do not break calling code
        fallback = LLMText(self.fail_safe_return)
        report = CallReport(latency_ms=0, model=getattr(self.llm, "model", None))
        return _attach_report(fallback, report)

def stream_generate(self, prompt: str):
    """Experimental: stream with on-the-fly sanitization. Yields text chunks.
    Note: enforcement is best-effort; final post-call policy still recommended."""
    if self._circuit_open():
        if self.fail_safe:
            yield ""
            return
        raise CircuitOpenError("Circuit is open due to recent failures.")
    if self.rate_limit:
        self.rate_limit.take(1.0)
    cleaned = redact_text(prompt, self.redactors)
    if self.moderation:
        check_input(cleaned)
    cleaned = self.policy.pre_call(cleaned)
    try:
        for chunk in self.llm.stream(cleaned, **self.params):
            # very light inline filtering; full check runs after
            try:
                safe = self.policy.post_call(chunk, schema_expected=False)
            except Exception:
                safe = ""
            yield safe
    except Exception:
        if self.fail_safe:
            yield self.fail_safe_return
            return
        raise
